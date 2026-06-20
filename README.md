# 🩺 MediBot: Advanced Private & Secure Medical RAG Assistant

An enterprise-grade, 100% offline Retrieval-Augmented Generation (RAG) assistant system engineered to parse complex clinical literature and provide secure, locally-synthesized insights without external cloud API dependencies.

## 🧠 Core System Design Philosophy
* **On-Premise Computational Boundary:** No third-party cloud API keys, network payload transfers, or external tracking telemetry loops. All analytical assets stay local.
* **Compliance Standards Engine:** Architecture structure matches modern sandbox deployment validation rules for high-security medical dataset exploration.
* **Layout-Aware Parsing:** Integrates advanced markdown extraction workflows to transform raw multi-page medical PDFs into accessible corpora while preserving explicit table and paragraph hierarchies.

## 🛠️ Complete Technical Architecture
* **Interface Layer:** Reactive Streamlit UI web application with component state retention.
* **Parsing Automation:** PyMuPDF4LLM structural layout extraction pipeline.
* **Execution Engine:** Local Llama-cpp high-performance quantized inference backend bindings.
* **Foundational Model:** Qwen-2.5-7B-Instruct 4-bit quantized baseline model.

## 🔒 Automated Software Quality Verification Gates
To maintain stable code deployment parameters, the codebase runs multiple automated code quality evaluation controls across its lifecycle:
1. **Stage 1: Code Linting (Ruff):** Analyzes logical code flow, removing dead imports or syntax smells.
2. **Stage 2: Automatic Formatting (Ruff-Format):** Enforces strict PEP8 line structures.
3. **Stage 3: Strict Type Checking (Mypy):** Asserts variable assignment type contracts.
4. **Stage 4: Unit Testing Metrics (Pytest):** Runs test suites under the tests directory.
5. **Stage 5: Vulnerability Static Analysis (Bandit):** Identifies potential shell injections or weak method references.
6. **Stage 6: Dependency Verification (Pip-Audit):** Validates package versions against global vulnerability registries.
7. **Stage 7: Secret Scanning (Gitleaks):** Audits indices to prevent accidental token tracking.
