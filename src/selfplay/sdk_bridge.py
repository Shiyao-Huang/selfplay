from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator, Literal, Protocol

from .models import AgentImage

EventKind = Literal[
    "thread.started", "turn.started", "tool.started", "tool.ended",
    "message", "diff", "usage", "turn.completed", "error",
]


@dataclass
class RuntimeEvent:
    """SDK-neutral event: Claude/Codex adapters both normalize into this shape."""

    kind: EventKind
    content: str
    runtime: str
    metadata: dict[str, Any] = field(default_factory=dict)


class RuntimeAdapter(Protocol):
    name: str

    async def run(self, image: AgentImage, goal: str) -> AsyncIterator[RuntimeEvent]:
        """运行一轮 Turn，并产出统一事件。"""


@dataclass
class MockRuntimeAdapter:
    name: str = "mock"

    async def run(self, image: AgentImage, goal: str) -> AsyncIterator[RuntimeEvent]:
        yield RuntimeEvent("thread.started", "mock thread", self.name, {"image_id": image.id})
        yield RuntimeEvent("turn.started", goal, self.name, {"version": image.version})
        output = self._generate_output(image, goal)
        yield RuntimeEvent("message", output, self.name)
        yield RuntimeEvent("turn.completed", "ok", self.name)

    def _generate_output(self, image: AgentImage, goal: str) -> str:
        """Simulate LLM output that responds to prompt constraints."""
        parts: list[str] = [image.prompt, f"任务：{goal}"]
        prompt = image.prompt
        if any(kw in prompt for kw in ("结论", "一句话", "总结")):
            parts.append("结论：分析完成，给出具体建议。")
        else:
            parts.append("执行中。")
        if any(kw in prompt for kw in ("错误", "边界", "异常", "edge")):
            parts.append("错误处理：已覆盖边界情况和异常输入。")
        if any(kw in prompt for kw in ("复杂度", "性能", "performance")):
            parts.append("复杂度分析：O(n log n) 平均情况，O(n²) 最坏情况。")
        if any(kw in prompt for kw in ("下一步", "next")):
            parts.append("下一步：部署到测试环境并验证。")
        if any(kw in prompt for kw in ("示例", "样例", "example")):
            parts.append("示例：输入 [3,1,4,1,5] → 输出 [1,1,3,4,5]。")
        if any(kw in prompt for kw in ("证据", "路径", "验证")):
            parts.append("证据路径：单元测试覆盖 95%，可通过 pytest 验证。")
        if any(kw in prompt for kw in ("步骤", "结构", "分层")):
            parts.append("步骤：1. 分析问题 2. 设计方案 3. 实现 4. 测试。")
        return "\n".join(parts)


# Backward-compatible alias used by early prototype notes.
MockRuntime = MockRuntimeAdapter


def _ensure_local_claude_sdk_path() -> None:
    root = Path(__file__).resolve().parents[2]
    local_src = root / "sources" / "claude-agent-sdk-python" / "src"
    if local_src.exists() and str(local_src) not in sys.path:
        sys.path.insert(0, str(local_src))


def _text_from_content_blocks(blocks: Any) -> str:
    chunks: list[str] = []
    for block in blocks or []:
        text = getattr(block, "text", None)
        if text:
            chunks.append(str(text))
    return "\n".join(chunks)


@dataclass
class ClaudeRuntimeAdapter:
    """Claude Agent SDK adapter：真实 SDK 可用时调用 query()，否则产出 error 事件。"""

    name: str = "claude"
    cwd: str = "."
    max_turns: int = 3

    async def run(self, image: AgentImage, goal: str) -> AsyncIterator[RuntimeEvent]:
        try:
            _ensure_local_claude_sdk_path()
            from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server, query, tool
        except Exception as exc:  # pragma: no cover - depends on optional SDK deps
            yield RuntimeEvent(
                "error",
                "Claude SDK unavailable: "
                f"{exc}. Mock mode is zero-dependency; for Claude mode install a verified "
                "Claude Agent SDK package/API and run with a compatible Python version.",
                self.name,
            )
            return

        @tool("score_state", "评估 OEDM 闭环状态", {"state": str})
        async def score_state(args):
            state = str(args.get("state", ""))
            score = 1.0 if "下一步" in state and "证据" in state else 0.6
            return {"content": [{"type": "text", "text": f"score={score}"}]}

        tool_names = [t.name for t in image.tools if t.enabled and t.kind == "builtin"]
        allowed = list(image.permissions.allowed_tools)
        mcp_servers: dict[str, Any] = {}
        try:
            selfref_server = create_sdk_mcp_server("selfref-tools", tools=[score_state])
            mcp_servers = {"selfref": selfref_server}
            allowed = list(dict.fromkeys(allowed + ["mcp__selfref__score_state", "score_state"]))
        except Exception as exc:
            yield RuntimeEvent(
                "message",
                f"selfref MCP disabled: {exc}",
                self.name,
                {"warning": "mcp_disabled"},
            )

        options = ClaudeAgentOptions(
            system_prompt=image.prompt,
            tools=tool_names,
            allowed_tools=allowed,
            disallowed_tools=image.permissions.disallowed_tools,
            permission_mode=image.permissions.mode,
            max_turns=self.max_turns,
            cwd=self.cwd,
            mcp_servers=mcp_servers,
            include_hook_events=True,
        )
        yield RuntimeEvent("thread.started", "claude query", self.name, {"image_id": image.id})
        yield RuntimeEvent("turn.started", goal, self.name, {"max_turns": self.max_turns})

        try:
            async for message in query(prompt=goal, options=options):
                name = type(message).__name__
                if name == "AssistantMessage":
                    text = _text_from_content_blocks(getattr(message, "content", []))
                    yield RuntimeEvent(
                        "message",
                        text,
                        self.name,
                        {"model": getattr(message, "model", None)},
                    )
                    usage = getattr(message, "usage", None)
                    if usage:
                        yield RuntimeEvent("usage", str(usage), self.name, {"usage": usage})
                elif name == "ResultMessage":
                    if getattr(message, "usage", None):
                        yield RuntimeEvent(
                            "usage",
                            str(message.usage),
                            self.name,
                            {"usage": message.usage},
                        )
                    yield RuntimeEvent(
                        "turn.completed",
                        getattr(message, "result", None) or message.subtype,
                        self.name,
                    )
                elif name.endswith("HookEventMessage"):
                    yield RuntimeEvent("tool.ended", getattr(message, "hook_event_name", "hook"), self.name)
                elif name == "SystemMessage":
                    subtype = getattr(message, "subtype", "system")
                    yield RuntimeEvent("thread.started", subtype, self.name, getattr(message, "data", {}))
                else:
                    yield RuntimeEvent("message", str(message), self.name, {"type": name})
        except Exception as exc:  # pragma: no cover - real SDK/environment failures
            yield RuntimeEvent("error", f"Claude run failed: {exc}", self.name)


@dataclass
class AnthropicRuntimeAdapter:
    """Real LLM adapter using the official anthropic Python SDK."""

    name: str = "claude"
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 1024

    async def run(self, image: AgentImage, goal: str) -> AsyncIterator[RuntimeEvent]:
        try:
            import anthropic  # type: ignore
        except ImportError as exc:
            yield RuntimeEvent(
                "error",
                f"anthropic package not installed: {exc}. "
                "Install with: pip install anthropic",
                self.name,
            )
            return

        yield RuntimeEvent("thread.started", "anthropic query", self.name, {"image_id": image.id})
        yield RuntimeEvent("turn.started", goal, self.name, {"model": self.model})

        try:
            api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
            base_url = os.environ.get("ANTHROPIC_BASE_URL") or None
            client = anthropic.AsyncAnthropic(api_key=api_key, base_url=base_url)
            response = await client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=image.prompt,
                messages=[{"role": "user", "content": goal}],
            )
            text_parts = [
                block.text for block in response.content if hasattr(block, "text")
            ]
            output = "\n".join(text_parts)
            yield RuntimeEvent("message", output, self.name, {
                "model": response.model,
                "usage": {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
            })
            yield RuntimeEvent("usage", str(response.usage), self.name, {"usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }})
            yield RuntimeEvent("turn.completed", "ok", self.name)
        except Exception as exc:
            yield RuntimeEvent("error", f"Anthropic API call failed: {exc}", self.name)


@dataclass
class CodexRuntimeAdapter:
    """Codex adapter 占位：Phase 0 不执行沙箱，仅保留统一接口。"""

    name: str = "codex"

    async def run(self, image: AgentImage, goal: str) -> AsyncIterator[RuntimeEvent]:
        yield RuntimeEvent("thread.started", "codex adapter placeholder", self.name, {"image_id": image.id})
        yield RuntimeEvent("error", "Codex runtime adapter reserved for Phase 2 sandbox execution", self.name)
