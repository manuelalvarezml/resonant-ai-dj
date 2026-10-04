# Build only the allowlisted context made by package-runtime.py, never the repository.
FROM node:22.20.0-bookworm-slim AS node
FROM python:3.12.12-slim-bookworm
COPY --from=node /usr/local/bin/node /usr/local/bin/node
RUN apt-get update && apt-get install -y --no-install-recommends libsndfile1 libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 resonant && useradd --uid 10001 --gid 10001 --create-home resonant \
    && python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false \
    PLAYLISTIQ_CPU_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
WORKDIR /opt/resonant
COPY requirements*.lock /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements-build.lock \
    && pip install --no-cache-dir --no-deps -r /tmp/requirements-cpu.lock \
    && pip install --no-cache-dir --no-deps --no-build-isolation --only-binary=:all: --no-binary=muq -r /tmp/requirements.lock \
    && pip check
COPY packages /opt/resonant/packages
COPY healthcheck.mjs runtime-smoke.py /opt/resonant/
ENV PYTHONPATH=/opt/resonant/packages/prompt-to-playlist/src \
    RESONANT_PYTHON=/opt/venv/bin/python RESONANT_RELEASE_ROOT=/release \
    RESONANT_STATE_ROOT=/state RESONANT_MODEL_ROOT=/models RESONANT_HOST=0.0.0.0 RESONANT_PORT=4175
RUN python runtime-smoke.py --imports-only
USER 10001:10001
EXPOSE 4175
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD ["node", "/opt/resonant/healthcheck.mjs"]
CMD ["node", "packages/web-player/scripts/serve-cloud.mjs"]
