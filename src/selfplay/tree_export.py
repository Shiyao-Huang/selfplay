"""Evolution tree export: SVG, Markdown, and Mermaid diagram output."""
from __future__ import annotations

from typing import Any


def _build_tree_data(images: list[Any]) -> list[dict[str, Any]]:
    """Convert AgentImage list to tree node dicts."""
    nodes: dict[str, dict[str, Any]] = {}
    for img in images:
        nodes[img.id] = {
            "id": img.id,
            "version": img.version,
            "runtime": img.runtime_adapter,
            "parent_id": img.parent_id,
            "score": img.eval.score,
            "prompt_preview": (img.prompt[:60] + "...") if len(img.prompt) > 60 else img.prompt,
        }
    return list(nodes.values())


def export_mermaid(images: list[Any]) -> str:
    """Export evolution tree as Mermaid flowchart (renders on GitHub)."""
    nodes = _build_tree_data(images)
    lines = ["flowchart TD"]
    id_map: dict[str, str] = {}
    for i, n in enumerate(nodes):
        safe = f"n{i}"
        id_map[n["id"]] = safe
        score_str = f"{n['score']:.2f}" if n["score"] else "—"
        label = f"v{n['version']} [{n['runtime']}]\\nscore={score_str}"
        lines.append(f'    {safe}["{label}"]')

    for n in nodes:
        if n["parent_id"] and n["parent_id"] in id_map:
            lines.append(f"    {id_map[n['parent_id']]} --> {id_map[n['id']]}")

    # Styling
    lines.append("")
    lines.append("    classDef root fill:#e1f5fe,stroke:#0288d1")
    lines.append("    classDef evolved fill:#e8f5e9,stroke:#388e3c")
    # Mark root (no parent)
    for n in nodes:
        if not n["parent_id"]:
            lines.append(f"    class {id_map[n['id']]} root")
        else:
            lines.append(f"    class {id_map[n['id']]} evolved")

    return "\n".join(lines) + "\n"


def export_markdown(images: list[Any]) -> str:
    """Export evolution tree as Markdown table + ASCII tree."""
    nodes = _build_tree_data(images)
    lines = ["# SelfPlay Evolution Tree", ""]

    # Table
    lines.append("| Version | ID | Runtime | Score | Parent |")
    lines.append("|---------|-----|---------|-------|--------|")
    for n in nodes:
        score_str = f"{n['score']:.2f}" if n["score"] else "—"
        lines.append(
            f"| v{n['version']} | `{n['id'][:16]}` | {n['runtime']} | {score_str} | "
            f"{n['parent_id'][:16] if n['parent_id'] else 'root'} |"
        )

    # ASCII tree
    lines.append("")
    lines.append("```")
    id_set = {n["id"] for n in nodes}
    children: dict[str, list[dict]] = {}
    roots: list[dict] = []
    for n in nodes:
        if n["parent_id"] and n["parent_id"] in id_set:
            children.setdefault(n["parent_id"], []).append(n)
        else:
            roots.append(n)

    def _draw(node: dict, prefix: str = "", is_last: bool = True) -> list[str]:
        connector = "└── " if is_last else "├── "
        score_str = f"{node['score']:.2f}" if node["score"] else "—"
        result = [f"{prefix}{connector}v{node['version']} [{node['runtime']}] score={score_str}"]
        kids = children.get(node["id"], [])
        for i, child in enumerate(kids):
            ext = "    " if is_last else "│   "
            result.extend(_draw(child, prefix + ext, i == len(kids) - 1))
        return result

    for i, root in enumerate(roots):
        score_str = f"{root['score']:.2f}" if root["score"] else "—"
        lines.append(f"v{root['version']} [{root['runtime']}] score={score_str}")
        kids = children.get(root["id"], [])
        for j, child in enumerate(kids):
            lines.extend(_draw(child, "", j == len(kids) - 1))

    lines.append("```")
    return "\n".join(lines) + "\n"


def export_svg(images: list[Any]) -> str:
    """Export evolution tree as a self-contained SVG."""
    nodes = _build_tree_data(images)
    # Build parent→child adjacency
    id_set = {n["id"] for n in nodes}
    children: dict[str, list[dict]] = {}
    roots: list[dict] = []
    node_map: dict[str, dict] = {n["id"]: n for n in nodes}
    for n in nodes:
        if n["parent_id"] and n["parent_id"] in id_set:
            children.setdefault(n["parent_id"], []).append(n)
        else:
            roots.append(n)

    # Layout: BFS for x positions, depth for y
    box_w, box_h, gap_x, gap_y = 220, 50, 30, 25
    positions: dict[str, tuple[int, int]] = {}

    def _count_leaves(nid: str) -> int:
        kids = children.get(nid, [])
        if not kids:
            return 1
        return sum(_count_leaves(c["id"]) for c in kids)

    total_width = max(1, sum(_count_leaves(r["id"]) for r in roots)) * (box_w + gap_x)
    max_depth = 0

    def _layout(nid: str, depth: int, x_offset: int) -> int:
        nonlocal max_depth
        max_depth = max(max_depth, depth)
        kids = children.get(nid, [])
        if not kids:
            positions[nid] = (x_offset, depth * (box_h + gap_y))
            return x_offset + box_w + gap_x
        current_x = x_offset
        for child in kids:
            current_x = _layout(child["id"], depth + 1, current_x)
        # Center parent over children
        child_xs = [positions[c["id"]][0] for c in kids]
        cx = (min(child_xs) + max(child_xs)) // 2
        positions[nid] = (cx, depth * (box_h + gap_y))
        return current_x

    x = (total_width - sum(_count_leaves(r["id"]) for r in roots) * (box_w + gap_x)) // 2
    for root in roots:
        x = _layout(root["id"], 0, x)

    total_h = (max_depth + 1) * (box_h + gap_y) + 40
    total_w = max(p[0] for p in positions.values()) + box_w + 60 if positions else 400
    total_w = max(total_w, 400)
    total_h = max(total_h, 200)

    # Draw SVG
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{total_h}" '
        f'viewBox="0 0 {total_w} {total_h}">',
        '<style>',
        '  text { font-family: -apple-system, monospace; font-size: 11px; }',
        '  .version { font-weight: bold; font-size: 13px; }',
        '</style>',
        '<rect width="100%" height="100%" fill="#fafafa"/>',
    ]

    # Edges
    for nid, pos in positions.items():
        for child in children.get(nid, []):
            cpos = positions[child["id"]]
            x1, y1 = pos[0] + box_w // 2, pos[1] + box_h
            x2, y2 = cpos[0] + box_w // 2, cpos[1]
            parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#90a4ae" stroke-width="1.5"/>')

    # Nodes
    for n in nodes:
        if n["id"] not in positions:
            continue
        x, y = positions[n["id"]]
        score_str = f"{n['score']:.2f}" if n["score"] else "—"
        is_root = not n["parent_id"] or n["parent_id"] not in id_set
        fill = "#e1f5fe" if is_root else "#e8f5e9"
        stroke = "#0288d1" if is_root else "#388e3c"
        parts.append(f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" '
                     f'rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x + 8}" y="{y + 18}" class="version">'
                     f'v{n["version"]} [{n["runtime"]}]</text>')
        parts.append(f'<text x="{x + 8}" y="{y + 35}" fill="#546e7a">'
                     f'score={score_str}</text>')
        # Truncated prompt
        prompt = n["prompt_preview"].replace("&", "&amp;").replace("<", "&lt;")
        parts.append(f'<text x="{x + 8}" y="{y + 48}" fill="#78909c" '
                     f'font-size="9">{prompt}</text>')

    parts.append('</svg>')
    return "\n".join(parts)
