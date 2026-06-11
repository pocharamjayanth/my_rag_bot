\# Skill: Clinical Document Synthesis \& Insights Extraction



\## Objective

Analyze retrieved medical text segments to extract diagnostic criteria, treatment steps, dosages, or general answers, organizing them into a high-utility medical layout.



\## Execution Workflow Steps

When a query is received along with retrieved document contexts, execute the following steps:

1\. \*\*Relevance Mapping:\*\* Scan the context blocks for exact terms matching the user's query.

2\. \*\*Evidence Extraction:\*\* Pinpoint sections detailing dosages, contraindications, clinical procedures, or guidelines.

3\. \*\*Synthesis:\*\* Combine facts from multiple document sections into a cohesive answer without repeating information.



\## Response Formatting Guidelines

Your final output to the user must follow this specific structural blueprint:

\- \*\*### 🩺 Clinical Summary:\*\* A brief 2-3 sentence overview answering the core question.

\- \*\*### 📋 Core Insights \& Guidelines:\*\* A clean bulleted list detailing precise medical instructions, metrics, or data extracted from the text.

\- \*\*### ⚠️ Clinical Caveats / Considerations:\*\* Any limitations, age restrictions, warnings, or required medical disclaimers mentioned directly in the document.

