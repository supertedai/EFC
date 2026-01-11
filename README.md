# Energyflow-Cosmology (cosmos-only)

This folder is the **cosmos-only storage** for Energy-Flow Cosmology artifacts (e.g. theory documents, schema, and related materials).

Development lives in the separate AGI repo.

## Use from AGI

```bash
export EFC_COSMOS_REPO_PATH="$HOME/energyflow-cosmology-cosmos"
python tools/cosmos_write.py --dest theory/notes/example.md --text "hello" --mkdir
```
