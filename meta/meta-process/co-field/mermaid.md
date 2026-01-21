flowchart TD

A[Pattern Layer] --> B[Topology Layer]
B --> C[Co-Field Layer]

C -->|Merge| C1[Merged Field]
C -->|Coexist| C2[Parallel Fields]
C -->|Isolation| C3[Isolated Field]
C -->|Collapse| C4[Collapsed Field]
C -->|Promotion| D[Integration Layer]

C4 --> TR[Transient Reservoir]
