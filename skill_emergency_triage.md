\# Skill: High-Velocity Emergency Triage Routing



\## Objective

Evaluate acute clinical logs or patient update scripts to determine instant risk stratification boundaries and immediate life-saving steps.



\## Execution Workflow Steps

1\. \*\*Red Flag Audit:\*\* Immediately check context text for severe red-flag markers (e.g., respiratory failure, unstable vitals, hemorrhage).

2\. \*\*Stability Tiering:\*\* Gauge whether the situation is actively deteriorating or clinically stable.

3\. \*\*Protocol Extraction:\*\* Pull out the immediate emergency medical actions required.



\## Response Formatting Guidelines

\- \*\*### 🚨 TRIAGE STATUS LEVEL:\*\* Output exactly one marker: \*\*\[🔴 CRITICAL STABILIZATION REQ / 🟡 URGENT INTERVENTION / 🟢 ROUTINE EVALUATION]\*\*.

\- \*\*### ⏱️ Immediate Clinical Interventions:\*\* A prioritized, sequential bulleted list of immediate, time-sensitive emergency actions.

\- \*\*### 📉 Physiological Justification:\*\* A structural breakdown explaining the clinical findings that caused this specific triage placement.



