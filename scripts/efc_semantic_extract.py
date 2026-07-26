#!/usr/bin/env python3
"""
EFC Semantic Extractor

Leser gjennom theory/formal/*, henter ut essens pr. modul,
og bygger:
- schema/modules/<module-id>.json
- schema/efc_master.json
- schema/efc_graph.json

Ingen eksterne avhengigheter – kun stdlib.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List


ROOT = Path(__file__).resolve().parents[1]
FORMAL_ROOT = ROOT / "theory" / "formal"
SCHEMA_ROOT = ROOT / "schema"
MODULES_ROOT = SCHEMA_ROOT / "modules"


def read_text_if_exists(path: Path) -> str:
    if path.is_file():
        return path.read_text(encoding="utf-8", errors="ignore")
    return ""


def load_json_if_exists(path: Path) -> Any:
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def extract_title_from_markdown(text: str) -> str:
    # first "# ..." line
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return ""


def extract_title_from_tex(text: str) -> str:
    # first \section*{...} or \section{...}
    m = re.search(r"\\section\*?\{([^}]*)\}", text)
    if m:
        return m.group(1).strip()
    return ""


def extract_first_paragraph(text: str) -> str:
    # very simple: first non-empty block of 2–6 lines
    lines = [l.rstrip() for l in text.splitlines()]
    blocks: List[List[str]] = []
    current: List[str] = []
    for line in lines:
        if line.strip():
            current.append(line.strip())
        else:
            if current:
                blocks.append(current)
                current = []
    if current:
        blocks.append(current)

    if not blocks:
        return ""

    # join first block, short-cropped
    para = " ".join(blocks[0])
    return para[:800]


def extract_tokens(text: str, max_tokens: int = 25) -> List[str]:
    text = text.lower()
    # simple split on non-alpha
    words = re.split(r"[^a-z0-9_]+", text)
    freq: Dict[str, int] = {}
    for w in words:
        if len(w) < 2:
            continue
        if w in {"the", "and", "for", "with", "this", "that", "from", "of"}:
            continue
        freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    return [w for w, _ in sorted_words[:max_tokens]]


def classify_layer(module_id: str, title: str) -> str:
    lid = module_id.lower()
    t = title.lower()
    if "efc-s" in lid or "efc–s" in t or "structural" in t:
        return "EFC-S"
    if "efc-d" in lid or "efc–d" in t or "dynamic" in t or "dynamics" in t:
        return "EFC-D"
    if "efc-h" in lid or "halo" in t:
        return "EFC-H"
    if "c0" in lid or "c₀" in t or "entropy–information" in t or "entropy-information" in t:
        return "EFC-C0"
    if "notation" in lid:
        return "notation"
    if "parameter" in lid:
        return "parameters"
    if "header" in lid:
        return "header"
    if "flow-diagram" in lid:
        return "diagram"
    if "formal-spec" in lid:
        return "formal-master"
    return "other"


def infer_dependencies(layer: str) -> List[str]:
    """
    Grov modell av avhengigheter mellom lag.
    Dette kan finjusteres senere.
    """
    if layer == "EFC-D":
        return ["EFC-S", "EFC-C0"]
    if layer == "EFC-H":
        return ["EFC-S", "EFC-D", "EFC-C0"]
    if layer == "EFC-C0":
        return ["EFC-S"]
    if layer == "notation":
        return ["header"]
    if layer == "formal-master":
        return ["EFC-S", "EFC-D", "EFC-H", "EFC-C0", "notation", "parameters", "header"]
    return []


def build_module_descriptor(module_dir: Path) -> Dict[str, Any]:
    module_id = module_dir.name
    readme_md = read_text_if_exists(module_dir / "README.md")
    index_md = read_text_if_exists(module_dir / "index.md")
    index_tex = read_text_if_exists(module_dir / "index.tex")
    index_json = load_json_if_exists(module_dir / "index.json")

    # Title
    title = ""
    if readme_md:
        title = extract_title_from_markdown(readme_md)
    if not title and index_md:
        title = extract_title_from_markdown(index_md)
    if not title and index_tex:
        title = extract_title_from_tex(index_tex)
    if not title and isinstance(index_json, dict):
        title = index_json.get("title", "") or index_json.get("model", "")

    if not title:
        title = module_id

    # Summary: prefer README, then index.md, then tex
    source_text_for_summary = readme_md or index_md or index_tex
    summary = extract_first_paragraph(source_text_for_summary)

    # Keywords: grep over all text we have
    combined_text = "\n".join(
        t for t in [readme_md, index_md, index_tex] if t
    )
    keywords = extract_tokens(combined_text)

    layer = classify_layer(module_id, title)
    dependencies = infer_dependencies(layer)

    descriptor: Dict[str, Any] = {
        "id": module_id,
        "name": title,
        "path": str(module_dir.relative_to(ROOT)),
        "layer": layer,
        "summary": summary,
        "keywords": keywords,
        "dependencies": dependencies,
        "raw": {
            "has_readme": bool(readme_md),
            "has_index_md": bool(index_md),
            "has_index_tex": bool(index_tex),
            "has_index_json": isinstance(index_json, dict),
        },
    }

    # If index.json exists, merge some fields
    if isinstance(index_json, dict):
        descriptor["index_json"] = index_json

    return descriptor


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False), encoding="utf-8")


def main() -> None:
    if not FORMAL_ROOT.is_dir():
        print(f"[WARN] {FORMAL_ROOT} does not exist. Nothing to do.")
        return

    MODULES_ROOT.mkdir(parents=True, exist_ok=True)
    SCHEMA_ROOT.mkdir(parents=True, exist_ok=True)

    modules: List[Dict[str, Any]] = []

    for module_dir in sorted(FORMAL_ROOT.iterdir()):
        if not module_dir.is_dir():
            continue
        # Skip hidden or irrelevant dirs if needed
        if module_dir.name.startswith("."):
            continue

        descriptor = build_module_descriptor(module_dir)
        modules.append(descriptor)

        # write per-module file
        module_json_path = MODULES_ROOT / f"{descriptor['id']}.json"
        write_json(module_json_path, descriptor)

    # Global master schema
    master = {
        "name": "Energy-Flow Cosmology — Formal Semantic Schema",
        "version": "1.0",
        "modules": modules,
    }
    write_json(SCHEMA_ROOT / "efc_master.json", master)

    # Graph representation: nodes + edges
    nodes = []
    edges = []
    id_to_layer = {m["id"]: m["layer"] for m in modules}

    for m in modules:
        nodes.append(
            {
                "id": m["id"],
                "label": m["name"],
                "layer": m["layer"],
                "path": m["path"],
            }
        )

    # layer-based edges (coarse)
    # we build edges both from explicit dependencies and inferred layers
    for m in modules:
        src_id = m["id"]
        for dep_layer in m.get("dependencies", []):
            for other in modules:
                if other["layer"] == dep_layer:
                    edges.append(
                        {
                            "from": src_id,
                            "to": other["id"],
                            "type": "depends_on_layer",
                        }
                    )

    graph = {
        "nodes": nodes,
        "edges": edges,
    }
    write_json(SCHEMA_ROOT / "efc_graph.json", graph)

    print(f"[INFO] Processed {len(modules)} modules.")
    print(f"[INFO] Written: {SCHEMA_ROOT / 'efc_master.json'}")
    print(f"[INFO] Written: {SCHEMA_ROOT / 'efc_graph.json'}")


if __name__ == "__main__":
    main()
