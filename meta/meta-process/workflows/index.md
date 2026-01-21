# Meta-Process Workflows

The Workflows layer defines the standard operational flows used by the meta-process.  
It describes how tasks, transitions, diagnostics, and stabilisation procedures are combined into predictable, repeatable sequences.

Workflows describe **how the system runs**, not how it changes (Process-of-Process) or how it is validated (Validation Plan).

---

## 1. Purpose
- define canonical procedures for meta-process operation  
- ensure consistent execution across layers  
- standardise task sequences  
- provide stable flows for transitions, stabilisation, diagnostics, and load regulation  
- give downstream layers predictable behaviour  

---

## 2. Scope
Workflows cover:

- coherence workflows  
- transition workflows  
- stability workflows  
- diagnostic workflows  
- collapse-handling workflows  
- integration-support workflows  

Workflows do not modify architecture — they orchestrate existing tasks.

---

## 3. Included Files
- `index.jsonld`  
- `core-workflows.md`  
- `transition-workflows.md`  
- `stability-workflows.md`  
- `diagnostic-workflows.md`  
- `examples.md`  

---

## 4. Mermaid Overview

```mermaid
flowchart TD

A[Trigger] --> B[Workflow Start]
B --> C[Task Sequence]
C --> D[Decision Node]
D -->|OK| E[Continue Workflow]
D -->|Fail| F[Diagnostic Workflow]
E --> G[Workflow Output]
