FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace/selfplay

COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests

RUN python -m pip install --upgrade pip \
    && python -m pip install -e "." \
    && python -m pip install pytest rich pyyaml anthropic

CMD ["selfplay", "demo", "Docker self-evolution smoke test"]
