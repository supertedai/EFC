#!/usr/bin/env python3
from pathlib import Path

def main():
    repo = Path(".").resolve()
    papers = repo / "docs" / "papers" / "efc"

    if not papers.exists():
        print("[ERROR] papers directory not found")
        return

    for paper_dir in papers.iterdir():
        if not paper_dir.is_dir():
            continue

        paper_id = paper_dir.name
        bib_file = paper_dir / "citations.bib"

        bibkey = paper_id.lower().replace(" ", "-").replace("–", "-").replace("—", "-")

        content = f"""@article{{{bibkey}_2025,
  title={{{{{ {paper_id} }}}}},
  author={{Magnusson, Morten}},
  year={{2025}},
  note={{Energy-Flow Cosmology Project}},
  url={{https://github.com/supertedai/EFC}}
}}
"""

        bib_file.write_text(content, encoding="utf-8")
        print(f"[OK] Fixed {bib_file}")

    print("\n[DONE] All citations regenerated.")

if __name__ == "__main__":
    main()
