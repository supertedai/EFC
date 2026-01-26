# Reproducibility Guide  
### Standards for Transparent and Repeatable EFC Research  
**Version 1.0 — M. Magnusson**

---

## 1. Purpose
This guide defines how reproducibility is maintained across all stages of Energy-Flow Cosmology (EFC).  
It ensures that any independent researcher can recreate:
- the dataset  
- the assumptions  
- the transformations  
- the model outputs  
- the validation results  

without requiring undocumented knowledge.

---

## 2. Core Requirements

### 2.1 Complete Input Transparency
All inputs must be accessible:
- raw observational data  
- processed datasets  
- parameter files  
- transformation scripts  
- JSON-LD concept nodes  

No hidden preprocessing is allowed.

---

### 2.2 Deterministic Computation
EFC code must be:
- deterministic  
- seed-controlled  
- free from implicit randomness  

All modules define explicit seeds and reproducible operations.

---

### 2.3 Traceable Model Definitions
Every equation, relation, and parameter must map to:
- a file  
- a version  
- a documented reasoning step  

If an equation changes, the cause must be visible in version history.

---

## 3. Code Structure Requirements

### 3.1 Modular organization
Core functions must remain isolated:
- `/core/`  
- `/entropy/`  
- `/potential/`  
- `/validation/`  
- `/simulator/`  

This prevents silent propagation of changes.

---

### 3.2 Verified outputs
Each module must output:
- figures  
- JSON arrays  
- intermediate states  
- validation results  

so the entire chain can be inspected.

---

## 4. Documentation Requirements

### 4.1 Minimum required documentation
Each theoretical or computational module needs:
- a README  
- an `index.md`  
- a JSON-LD node  

### 4.2 Machine-readable records
Reproducibility demands:
- schema nodes  
- semantic maps  
- site-graphs  
- methodology indices  

These allow automated systems to reconstruct the pipeline.

---

## 5. Validation Requirements

### 5.1 Internal validation
Before results are accepted:
- gradients must be correct  
- array shapes must match  
- Ef/S relationships must hold  
- rotation curves must be deterministic  

### 5.2 External validation
Model outputs must be comparable to:
- SPARC rotation curves  
- lensing datasets  
- profile slopes  
- entropy distributions  

Consistency is mandatory.

---

## 6. Revision and Versioning

### 6.1 Version increments
A revision must trigger:
- version bump  
- semantic update  
- schema regeneration  
- new validation run  

### 6.2 Change logs
Every update must document:
- what changed  
- why it changed  
- which layer it affects  

---

## 7. Reproducibility Checklist
A result is reproducible when:

- [ ] all inputs are accessible  
- [ ] all dependencies are versioned  
- [ ] parameters are explicit  
- [ ] code paths are deterministic  
- [ ] validation steps are provided  
- [ ] no hidden transformations exist  
- [ ] semantic nodes reference all major components  

If a single item fails, the result is not considered reproducible.

---

## 8. Outcome
The reproducibility guide ensures:
- transparent research  
- external verifiability  
- stable results across versions  
- trust in the entire EFC pipeline  

It formalizes how the EFC system remains open, structured, and repeatable.
