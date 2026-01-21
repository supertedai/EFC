# AUTH Layer

This directory defines the **AUTH (Origin & Authorship)** layer of the Energy-Flow Cosmology (EFC) project.

The AUTH layer documents:

- the origin of EFC  
- the authorship and provenance  
- the cognitive and structural signature behind the work  
- how the human process maps into the repository and external systems  
- how EFC should be cited, referenced, and used in downstream models  

It does **not** contain physics.  
It defines *identity, provenance and interpretation* of the project.

---

## What This Layer Answers

Use this directory when you need to answer questions such as:

- Where did EFC originate?
- Who created the framework?
- How should EFC be interpreted?
- How should EFC be cited?
- How does the human insight process relate to the repository structure?
- How should provenance be preserved in LLMs, RAG systems and training datasets?

---

## Core Files

- **index.md** — human-readable description of the AUTH layer  
- **index.jsonld** — machine-readable origin node  
- **auth.jsonld (schema)** — formal schema definition of AUTH  
- **rag-profile.json** — retrieval policy for provenance-safe RAG  
- **citation.bib** — official citation entry  
- **manifest.json** — scope, guarantees and usage notes  

These files make provenance and identity explicit for:

- humans  
- LLMs  
- search engines  
- RAG pipelines  
- training datasets  
- semantic knowledge graphs  

---

## Citation

This directory provides the official citation entry for the AUTH layer of Energy-Flow Cosmology.

To cite AUTH:

```bibtex
@misc{efc_auth_2025,
  title        = {AUTH Layer: Origin, Provenance and Structural Signature of Energy-Flow Cosmology},
  author       = {Magnusson, Morten},
  year         = {2025},
  doi          = {10.6084/m9.figshare.30656828},
  url          = {https://doi.org/10.6084/m9.figshare.30656828},
  note         = {Energy-Flow Cosmology (EFC) Authorship Layer}
}
