#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys


def load_template(template_dir: Path, name: str) -> str:
    path = template_dir / name
    if not path.exists():
        print(f"[ERROR] Template not found: {path}", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def write_file(path: Path, content: str, force: bool = False):
    if path.exists() and not force:
        print(f"[SKIP] {path} already exists (use --force to overwrite)")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"[OK]   wrote {path}")


def build_placeholders(args) -> dict:
    # Keywords
    keywords = [k.strip() for k in (args.keywords or "").split(",") if k.strip()]
    if not keywords:
        keywords = ["EFC", "Paper"]

    # For JSON arrays
    keywords_json = ", ".join(f"\"{k}\"" for k in keywords)
    keywords_list_md = "\n- " + "\n- ".join(keywords)

    # Short title fallback
    title_short = args.title_short if args.title_short else args.title

    # Bibtex key
    if args.bibkey:
        bibkey = args.bibkey
    else:
        # e.g. cem_consciousness_ego_mirror_2025
        normalized = args.id.lower().replace(" ", "-").replace("–", "-").replace("—", "-")
        normalized = normalized.replace("_", "-")
        bibkey = f"{normalized}_{args.year}"

    # Generic relations (kan finpusses manuelt etterpå)
    theory_rel = args.theory_rel or "Connects to the formal EFC theoretical layer."
    dynamics_rel = args.dynamics_rel or "Relates to entropy, flow and grid-level dynamics."
    meta_rel = args.meta_rel or "Links to the meta / cognition layer where applicable."
    data_rel = args.data_rel or "May relate to validation or external data where relevant."

    return {
        "PLACEHOLDER_ID": args.id,
        "PLACEHOLDER_TITLE": args.title,
        "PLACEHOLDER_TITLE_SHORT": title_short,
        "PLACEHOLDER_VERSION": args.version,
        "PLACEHOLDER_KEYWORDS": keywords_json,
        "PLACEHOLDER_KEYWORDS_LIST": keywords_list_md,
        "PLACEHOLDER_BIBKEY": bibkey,
        "PLACEHOLDER_THEORY_REL": theory_rel,
        "PLACEHOLDER_DYNAMICS_REL": dynamics_rel,
        "PLACEHOLDER_META_REL": meta_rel,
        "PLACEHOLDER_DATA_REL": data_rel,
    }


def render_template(raw: str, placeholders: dict) -> str:
    out = raw
    for key, value in placeholders.items():
        out = out.replace("{" + key + "}", value)
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Generate EFC paper files from templates."
    )
    parser.add_argument(
        "--id",
        required=True,
        help="Paper ID / directory name, e.g. CEM-Consciousness-Ego-Mirror",
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Full title, e.g. 'CEM – Consciousness Ego Mirror'",
    )
    parser.add_argument(
        "--title-short",
        dest="title_short",
        help="Optional short title used in README text.",
    )
    parser.add_argument(
        "--version",
        default="1.0",
        help="Paper version (default: 1.0)",
    )
    parser.add_argument(
        "--keywords",
        help="Comma-separated keywords, e.g. 'EFC, Consciousness, Ego, Mirror, CEM'",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2025,
        help="Year for BibTeX entry (default: 2025)",
    )
    parser.add_argument(
        "--bibkey",
        help="Optional BibTeX key. If not set, generated from id+year.",
    )
    parser.add_argument(
        "--theory-rel",
        help="Relation to theory layer (for README).",
    )
    parser.add_argument(
        "--dynamics-rel",
        help="Relation to dynamics / entropy layer (for README).",
    )
    parser.add_argument(
        "--meta-rel",
        help="Relation to meta / cognition layer (for README).",
    )
    parser.add_argument(
        "--data-rel",
        help="Relation to data / validation (for README).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files.",
    )

    args = parser.parse_args()

    # Finn repo-root fra denne filen: <root>/scripts/generate_paper.py
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    template_dir = repo_root / "scripts" / "templates" / "paper_template"
    target_dir = repo_root / "docs" / "papers" / "efc" / args.id

    if not template_dir.exists():
        print(f"[ERROR] Template directory not found: {template_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Repo root:    {repo_root}")
    print(f"[INFO] Template dir: {template_dir}")
    print(f"[INFO] Target dir:   {target_dir}")

    placeholders = build_placeholders(args)

    # Malfilene
    templates = {
        "README.md": "template_readme.md",
        f"{args.id}.jsonld": "template.jsonld",
        "index.json": "template_index.json",
        "schema.json": "template_schema.json",
        "citations.bib": "template.bib",
    }

    for output_name, template_name in templates.items():
        raw = load_template(template_dir, template_name)
        rendered = render_template(raw, placeholders)
        out_path = target_dir / output_name
        write_file(out_path, rendered, force=args.force)

    print("\n[INFO] Done.")
    print("      Remember to:")
    print("      - Add or update the PDF and MD for this paper.")
    print("      - Optionally update global indexes / semantic graph if required.")


if __name__ == "__main__":
    main()
