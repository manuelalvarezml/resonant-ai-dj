"""RAM and process-tree guards for Step 1 workers.

The analysis Mac has 16 GB of RAM. Cursor and other apps already occupy a
large share. Workers must not grow until the kernel starts swapping the
whole session.
"""

from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass

PAGE_SIZE_BYTES = 16384
_SWAP_FIELD = re.compile(r"(total|used)\s*=\s*([0-9.]+)([MGT])", re.I)


@dataclass(frozen=True)
class MemorySnapshot:
    total_bytes: int
    free_bytes: int
    reclaimable_bytes: int
    compressor_bytes: int
    wired_bytes: int
    swap_used_bytes: int = 0
    swap_total_bytes: int = 0

    @property
    def reclaimable_mb(self) -> float:
        return self.reclaimable_bytes / (1024 * 1024)

    @property
    def swap_used_mb(self) -> float:
        return self.swap_used_bytes / (1024 * 1024)


def _parse_vm_stat() -> dict[str, int]:
    output = subprocess.check_output(["vm_stat"], text=True)
    parsed: dict[str, int] = {}
    for line in output.splitlines()[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        digits = "".join(ch for ch in value if ch.isdigit())
        if digits:
            parsed[key.strip()] = int(digits)
    return parsed


def _parse_swap_bytes() -> tuple[int, int]:
    try:
        raw = subprocess.check_output(["sysctl", "-n", "vm.swapusage"], text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 0, 0
    multipliers = {"M": 1024**2, "G": 1024**3, "T": 1024**4}
    values = {"total": 0, "used": 0}
    for key, amount, unit in _SWAP_FIELD.findall(raw):
        values[key.lower()] = int(float(amount) * multipliers[unit.upper()])
    return values["used"], values["total"]


def memory_snapshot() -> MemorySnapshot:
    stats = _parse_vm_stat()
    page = PAGE_SIZE_BYTES
    free = stats.get("Pages free", 0) * page
    inactive = stats.get("Pages inactive", 0) * page
    speculative = stats.get("Pages speculative", 0) * page
    purgeable = stats.get("Pages purgeable", 0) * page
    compressor = stats.get("Pages occupied by compressor", 0) * page
    wired = stats.get("Pages wired down", 0) * page
    total = int(
        subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip()
    )
    swap_used, swap_total = _parse_swap_bytes()
    return MemorySnapshot(
        total_bytes=total,
        free_bytes=free,
        reclaimable_bytes=free + inactive + speculative + purgeable,
        compressor_bytes=compressor,
        wired_bytes=wired,
        swap_used_bytes=swap_used,
        swap_total_bytes=swap_total,
    )


def process_tree_rss_kb(pid: int) -> int:
    total = 0
    stack = [pid]
    seen: set[int] = set()
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        try:
            rss = subprocess.check_output(
                ["ps", "-o", "rss=", "-p", str(current)],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            if rss:
                total += int(rss)
        except (subprocess.CalledProcessError, ValueError):
            continue
        try:
            children = subprocess.check_output(
                ["pgrep", "-P", str(current)],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            stack.extend(int(token) for token in children.split() if token)
        except (subprocess.CalledProcessError, ValueError):
            continue
    return total


def wait_for_ram_headroom(
    *,
    min_reclaimable_mb: float,
    timeout_s: float = 120,
    poll_s: float = 5,
    progress=print,
) -> MemorySnapshot:
    deadline = time.monotonic() + timeout_s
    snapshot = memory_snapshot()
    while snapshot.reclaimable_mb < min_reclaimable_mb:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise MemoryError(
                f"RAM headroom too low to start a worker: "
                f"{snapshot.reclaimable_mb:.0f} MB reclaimable, "
                f"need {min_reclaimable_mb:.0f} MB"
            )
        progress(
            f"Waiting for RAM headroom "
            f"({snapshot.reclaimable_mb:.0f} MB reclaimable, "
            f"need {min_reclaimable_mb:.0f} MB)"
        )
        time.sleep(min(poll_s, remaining))
        snapshot = memory_snapshot()
    return snapshot


def wait_for_ram_recovery(
    *,
    min_reclaimable_mb: float,
    timeout_s: float = 45,
    poll_s: float = 3,
    progress=print,
) -> MemorySnapshot:
    deadline = time.monotonic() + timeout_s
    snapshot = memory_snapshot()
    while snapshot.reclaimable_mb < min_reclaimable_mb and time.monotonic() < deadline:
        progress(
            f"live recovery reclaimable={snapshot.reclaimable_mb:.0f}MB "
            f"target={min_reclaimable_mb:.0f}MB "
            f"swap={snapshot.swap_used_mb:.0f}MB"
        )
        time.sleep(poll_s)
        snapshot = memory_snapshot()
    progress(
        f"live recovery done reclaimable={snapshot.reclaimable_mb:.0f}MB "
        f"swap={snapshot.swap_used_mb:.0f}MB"
    )
    return snapshot


class WorkerMemoryExceeded(RuntimeError):
    """Raised when a track worker is killed to protect the host."""


def run_capped_subprocess(
    command: list[str],
    *,
    env: dict[str, str],
    max_rss_mb: float,
    min_reclaimable_mb: float,
    timeout_s: float = 900,
    poll_s: float = 2.0,
    stage: str = "worker",
    label: str = "",
    progress=print,
) -> subprocess.CompletedProcess:
    proc = subprocess.Popen(command, env=env)
    started = time.monotonic()
    peak_rss_mb = 0.0
    last_logged = 0.0
    last_rss = 0.0
    prefix = f"live track={label} stage={stage}" if label else f"live stage={stage}"
    snapshot = memory_snapshot()
    progress(
        f"{prefix} started reclaimable={snapshot.reclaimable_mb:.0f}MB "
        f"swap={snapshot.swap_used_mb:.0f}MB"
    )
    try:
        while True:
            code = proc.poll()
            if code is not None:
                snapshot = memory_snapshot()
                progress(
                    f"{prefix} finished code={code} peak_rss={peak_rss_mb:.0f}MB "
                    f"reclaimable={snapshot.reclaimable_mb:.0f}MB "
                    f"swap={snapshot.swap_used_mb:.0f}MB"
                )
                return subprocess.CompletedProcess(command, code)
            elapsed = time.monotonic() - started
            if elapsed > timeout_s:
                _kill_process_tree(proc.pid)
                raise TimeoutError(f"track worker timed out after {timeout_s:.0f}s")
            rss_mb = process_tree_rss_kb(proc.pid) / 1024
            peak_rss_mb = max(peak_rss_mb, rss_mb)
            snapshot = memory_snapshot()
            now = time.monotonic()
            if now - last_logged >= 5 or rss_mb - last_rss >= 256:
                progress(
                    f"{prefix} rss={rss_mb:.0f}MB peak={peak_rss_mb:.0f}MB "
                    f"reclaimable={snapshot.reclaimable_mb:.0f}MB "
                    f"free={snapshot.free_bytes / (1024 * 1024):.0f}MB "
                    f"wired={snapshot.wired_bytes / (1024 * 1024):.0f}MB "
                    f"swap={snapshot.swap_used_mb:.0f}MB"
                )
                last_logged = now
                last_rss = rss_mb
            if rss_mb > max_rss_mb:
                _kill_process_tree(proc.pid)
                raise WorkerMemoryExceeded(
                    f"worker RSS {rss_mb:.0f} MB exceeded cap {max_rss_mb:.0f} MB "
                    f"(peak {peak_rss_mb:.0f} MB)"
                )
            snapshot = memory_snapshot()
            if snapshot.reclaimable_mb < min_reclaimable_mb:
                _kill_process_tree(proc.pid)
                raise WorkerMemoryExceeded(
                    f"system reclaimable RAM fell to {snapshot.reclaimable_mb:.0f} MB "
                    f"while worker RSS was {rss_mb:.0f} MB; killed worker to protect the host"
                )
            time.sleep(poll_s)
    except Exception:
        if proc.poll() is None:
            _kill_process_tree(proc.pid)
        raise


def _kill_process_tree(pid: int) -> None:
    try:
        subprocess.run(["pkill", "-TERM", "-P", str(pid)], check=False)
    except Exception:
        pass
    try:
        subprocess.run(["kill", "-TERM", str(pid)], check=False)
    except Exception:
        pass
    time.sleep(2)
    try:
        subprocess.run(["pkill", "-KILL", "-P", str(pid)], check=False)
    except Exception:
        pass
    try:
        subprocess.run(["kill", "-KILL", str(pid)], check=False)
    except Exception:
        pass
