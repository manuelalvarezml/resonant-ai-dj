# Use only the allowlisted context from prepare.py. Never send the whole repo.
FROM python:3.12.12-slim-bookworm AS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends libsndfile1 libgomp1 \
    && rm -rf /var/lib/apt/lists/*
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false \
    PLAYLISTIQ_CPU_THREADS=2 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 \
    NUMBA_CACHE_DIR=/tmp/numba MPLCONFIGDIR=/tmp/matplotlib HF_HOME=/tmp/huggingface \
    PYTHONPATH=/opt/resonant/packages/prompt-to-playlist/src:/opt/resonant \
    RESONANT_RELEASE_ROOT=/opt/resonant/release RESONANT_MODEL_ROOT=/opt/resonant/models \
    RESONANT_IDENTITY=/opt/resonant/identity.json
WORKDIR /opt/resonant
COPY requirements.lock requirements-cpu.lock requirements-build.lock ./
RUN pip install --no-cache-dir -r requirements-build.lock \
    && pip install --no-cache-dir --no-deps -r requirements-cpu.lock \
    && pip install --no-cache-dir --no-deps --no-build-isolation --only-binary=:all: --no-binary=muq -r requirements.lock \
    && pip check
COPY requirements-aws.lock ./
RUN pip install --no-cache-dir --no-deps -r requirements-aws.lock && pip check
FROM dependencies AS runtime
# Refresh distribution security fixes without changing the pinned Python/model stack.
RUN apt-get update && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
COPY packages ./packages
COPY runtime ./runtime
COPY release ./release
COPY models ./models
COPY identity.json verify.py benchmark.py Dockerfile ./
RUN python verify.py
# Lambda supplies an unprivileged user. Local verification explicitly uses UID10001.
ENTRYPOINT ["python", "-m", "awslambdaric"]
CMD ["runtime.worker.handler"]
