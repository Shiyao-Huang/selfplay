# Docker 开发环境

Docker 环境提供 Python 3.11 + SelfPlay CLI 的隔离验证。

## 一键 QA 验证

```bash
./qa-docker.sh
```

11 项检查全部通过才算 PASS。详见 [Docker QA SOP](docker-qa-sop.md)。

## 30 秒 mock 验证

```bash
cp .env.example .env
docker compose up --build
```

默认 `SELFPLAY_RUNTIME=mock`，不需要 API key，会运行：

```bash
selfplay --runtime mock demo "Docker self-evolution smoke test"
```

## 手动验证命令

```bash
# Build
docker build -t selfplay-dev:latest .

# Version
docker run --rm selfplay-dev:latest selfplay --version

# Demo
docker run --rm selfplay-dev:latest selfplay demo "smoke test"

# Tests
docker run --rm selfplay-dev:latest python -m pytest tests/ -v

# JSON output
docker run --rm selfplay-dev:latest selfplay demo --json "test" | python3 -m json.tool

# History + Tree (with persistent volume)
docker run --rm -v selfplay-qa-data:/workspace/selfplay/data \
  selfplay-dev:latest sh -c 'selfplay demo "test" > /dev/null && selfplay history && selfplay tree'
```

## 真实 Claude 运行

在 `.env` 中改为：

```bash
SELFPLAY_RUNTIME=claude
ANTHROPIC_AUTH_TOKEN=replace-me
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL=claude-sonnet-4-5
```

需要安装 SDK 依赖：修改 Dockerfile 中 `pip install -e "."` 为 `pip install -e ".[sdk]"`。

不要把真实 token 写入 README、Dockerfile 或提交到仓库。

## 常用命令

```bash
docker compose config
docker compose run --rm selfplay selfplay --version
docker compose run --rm selfplay selfplay history
docker compose down
docker volume rm selfplay_selfplay-data
```
