\# Skill: Precision Pharmacology \& Dosage Auditing



\## Objective

Scan medical documentation to isolate exact pharmaceutical parameters, titration paths, specific dosages, and explicit contraindications.



\## Execution Workflow Steps

1\. \*\*Compound Mapping:\*\* Identify the primary chemical or drug name mentioned in the user query.

2\. \*\*Metric Extraction:\*\* Isolate numerical metrics regarding safe starting dose, maximum thresholds, and age/weight restrictions.

3\. \*\*Risk Cross-Referencing:\*\* Look for warnings regarding drug-drug interactions or organ toxicity flags in the context.



\## Response Formatting Guidelines

\- \*\*### 💊 Pharmacological Blueprint:\*\* Name of the agent, drug class, and primary indication.

\- \*\*### 📊 Direct Dosing Guidance:\*\* A strict table with columns `Patient Class (Adult/Pediatric)`, `Standard Dose`, `Frequency`, and `Max 24h Threshold`.

\- \*\*### ⚠️ Critical Alerts \& Counter-indications:\*\* Bolded, bulleted safety restrictions regarding when \*not\* to administer this treatment.

