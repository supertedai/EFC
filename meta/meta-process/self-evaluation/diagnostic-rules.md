# Diagnostic Rules

These rules govern how the system flags structural issues.

---

## 1. Coherence Diagnostics
Trigger if:
- CLC < 0.6  
- BI unstable  
- alignment inconsistent across layers  

---

## 2. Overload Diagnostics
Trigger if:
- SL > threshold  
- TL spikes  
- RL approaching fragmentation zone  

---

## 3. Drift Diagnostics
Trigger if:
- LD > threshold  
- RD indicates loops beyond allowed depth  
- conceptual overlap exceeds tolerance  

---

## 4. Failure Diagnostics
Trigger if:
- CF increases across cycles  
- IM becomes recurrent  
- collapse cascades detected  

---

## 5. Resolution Pathways
When diagnostics trigger:
- report to Process-of-Process  
- do not attempt self-correction  
- do not modify structures  
