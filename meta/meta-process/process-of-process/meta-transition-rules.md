# Meta-Transition Rules

Rules governing how the architecture changes its own structure.

---

## 1. Expansion Rules
A new layer is added only if:
- there is persistent structural need  
- no existing layer can absorb the function  
- adding the layer reduces overall complexity  

---

## 2. Reduction Rules
A layer or primitive is removed if:
- duplicated by another layer  
- destabilising  
- unused  
- producing unnecessary recursion  

---

## 3. Consolidation Rules
Two layers merge if:
- they perform overlapping functions  
- coherence increases when combined  
- global dynamics stabilise  

---

## 4. Correction Rules
Structural drift is corrected when:
- responsibilities blur  
- transitions fail  
- global state oscillates unnecessarily  
