# Banking AI SQL Assistant
### Local LLM · Retrieval-Augmented Generation · PostgreSQL · SQL Validation

A local, AI-powered Text-to-SQL assistant designed for a synthetic banking analytics environment.

This project combines **Ollama, Qwen2.5-Coder, PostgreSQL, pgvector, and Retrieval-Augmented Generation (RAG)** to translate natural-language banking questions into SQL queries.

Unlike a basic Text-to-SQL application, the system integrates business knowledge retrieval, database metadata awareness, multi-layer SQL validation, automated SQL repair, and audit logging.

The goal is to explore how local language models can support reliable, explainable, and business-aware SQL generation without relying on external LLM APIs.

> **Project status:** Working local prototype. Not certified for production banking workloads. Use synthetic or non-sensitive data only.

---

## 1. Project Objectives

The project investigates several challenges commonly encountered when integrating language models with enterprise data platforms:

- Translating natural-language business questions into SQL.
- Incorporating organization-specific business definitions into SQL generation.
- Reducing hallucinated tables, columns, and business logic.
- Validating SQL syntax, semantics, and metadata before execution.
- Recovering from certain SQL generation errors through automated repair.
- Evaluating the impact of RAG on SQL generation quality.
- Maintaining an auditable record of generated SQL and validation attempts.

## 2. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Local LLM | Ollama + Qwen2.5-Coder 7B | Natural language to SQL |
| Embedding model | EmbeddingGemma | Semantic embeddings |
| Relational database | PostgreSQL | Banking analytics data |
| Vector database | pgvector | Knowledge retrieval |
| Application language | Python 3.12 | Pipeline orchestration |
| PostgreSQL driver | psycopg | Database connectivity |
| SQL parser | pglast | PostgreSQL AST analysis |
| Knowledge Base | JSON + PostgreSQL | Banking business definitions |
| Evaluation | Python + CSV/JSON | Baseline and RAG comparisons |
| Local environment | Windows + Docker | Development and database hosting |

The project is designed to run locally, with LLM inference and embedding generation handled through Ollama.

## 3. High-Level Architecture

```text
                Natural Language Question
                            |
                            v
                    SQL Pipeline
                            |
              +-------------+-------------+
              |                           |
              v                           v
       Schema & Metadata             RAG Retriever
              |                           |
              |                    EmbeddingGemma
              |                           |
              |                    pgvector Search
              |                           |
              |                    Business Knowledge
              |                           |
              +-------------+-------------+
                            |
                            v
                   Qwen2.5-Coder
                            |
                            v
                      Generated SQL
                            |
                            v
                  Multi-Layer Validation
                            |
                 +----------+----------+
                 |                     |
               PASSED                FAILED
                 |                     |
                 |                     v
                 |               SQL Repair
                 |                     |
                 |                 Revalidate
                 |                     |
                 +----------+----------+
                            |
                            v
                   Audit / Attempt Logs
                            |
                            v
                      SQL Output
```

Generated SQL is validated but is **not automatically executed by the SQL generation pipeline**.

## 4. Core Features

### 4.1 Natural Language to SQL

The system accepts banking analytics questions in natural language and generates PostgreSQL-compatible SQL.

Example:

**Question**

```text
How many high-value transactions do we have?
```

**Generated SQL**

```sql
SELECT COUNT(*) AS high_value_transactions_count
FROM analytics.fact_transactions
WHERE amount > 10000
  AND currency = 'EUR';
```

The definition of a high-value transaction is supplied through the project Knowledge Base rather than being treated as a universal banking standard.

### 4.2 Retrieval-Augmented Generation (RAG)

The system retrieves relevant business knowledge before generating SQL.

The retrieval process consists of:

1. Loading banking definitions from the Knowledge Base.
2. Generating 768-dimensional embeddings using EmbeddingGemma.
3. Storing embeddings in PostgreSQL with pgvector.
4. Converting the user's question into an embedding.
5. Searching for semantically similar business definitions.
6. Passing relevant knowledge to the SQL generator.

**Knowledge Base example**

```json
{
  "document_key": "RULE_002",
  "title": "High-Value Transaction",
  "content": "For this banking lab, a High-Value Transaction is defined as a transaction with amount greater than 10000 and currency = 'EUR' in analytics.fact_transactions."
}
```

The Knowledge Base currently includes definitions for Gross Transaction Volume, Net Transaction Flow, EUR filtering, and high-value transactions.

These definitions are illustrative and belong to the synthetic banking lab.

### 4.3 Metadata-Aware SQL Generation

The application retrieves database schema information to provide the LLM with context about available tables and columns.

This helps reduce references to nonexistent database objects and improves the relevance of generated SQL.

Metadata-aware generation is combined with PostgreSQL metadata validation.

### 4.4 Multi-Layer SQL Validation

Generated SQL passes through a validation pipeline:

| Validation layer | Responsibility |
|---|---|
| AST Safety Validation | Checks SQL safety and permitted statement structure |
| Semantic Validation | Applies supported semantic checks |
| Business Metric Validation | Checks supported metric definitions and aggregation columns |
| PostgreSQL Metadata Validation | Verifies references against database metadata |

Business metric validation currently includes explicit checks for Gross and Net transaction calculations.

**Current limitation:** Business rules retrieved from RAG are not yet dynamically translated into independent validation constraints. Extending the validator with structured business rules is a planned enhancement.

### 4.5 Automated SQL Repair

When validation fails, the pipeline can request a corrected SQL statement from the local model.

The repair process uses available schema and knowledge context and performs validation again.

The pipeline is configured with a maximum of three repair attempts.

The goal is to recover from selected generation errors while keeping the SQL validation boundary in place.

### 4.6 Audit Logging

The project includes request and attempt logging.

The pipeline records information about SQL generation and validation attempts, supporting troubleshooting and evaluation of model behavior.

### 4.7 Evaluation Framework

The repository contains an evaluation framework for comparing SQL generation with and without RAG.

Relevant files:

```text
evaluation/
├── evaluation_dataset.json
└── evaluation_results.csv

evaluation_runner.py
```

Initial tests demonstrate structurally valid outputs for a small evaluation set. These results should not be interpreted as comprehensive proof of business correctness.

## 5. RAG Experiment: With vs. Without Knowledge Retrieval

A controlled example was performed using the question:

```text
How many high-value transactions do we have?
```

The Knowledge Base defines high-value transactions as transactions with:

```sql
amount > 10000
AND currency = 'EUR'
```

### Without RAG

The model generated a query that grouped high-value transactions by customer and omitted the EUR currency filter.

### With RAG

The model generated:

```sql
SELECT COUNT(*) AS high_value_transactions_count
FROM analytics.fact_transactions
WHERE amount > 10000
  AND currency = 'EUR';
```

The result matched the intended business definition for this test.

| Evaluation criterion | Without RAG | With RAG |
|---|---|---|
| Amount threshold applied | Yes | Yes |
| EUR filter applied | No | Yes |
| Overall transaction count | No | Yes |
| Matches experimental definition | No | Yes |

This is a **single illustrative experiment**, not a statistically significant benchmark. Repeated testing with a larger, independently verified dataset is required to establish generalizable performance differences.

## 6. Project Structure

```text
banking-ai-sql-assistant/
├── app.py
├── sql_pipeline.py
├── sql_generator.py
├── sql_orchestrator.py
├── sql_repair.py
├── rag_loader.py
├── rag_retriever.py
├── schema_context.py
├── schema_metadata.json
├── metadata_provider.py
├── validation_engine.py
├── sql_validator.py
├── semantic_validator.py
├── business_metric_validator.py
├── postgres_validator.py
├── ai_logger.py
├── evaluation_runner.py
├── knowledge/
│   └── banking_knowledge.json
├── evaluation/
│   ├── evaluation_dataset.json
│   └── evaluation_results.csv
├── tests/
├── Modelfile
├── Modelfile.qwen
├── requirements.txt
├── .gitignore
└── README.md
```

## 7. Local Setup

### Prerequisites

- Python 3.12 or a compatible Python environment
- PostgreSQL with the pgvector extension
- Ollama installed and running locally
- The required LLM and embedding models
- A PostgreSQL user with appropriately restricted permissions

### Python environment

```powershell
git clone https://github.com/MehrdadMHM/banking-ai-sql-assistant.git
cd banking-ai-sql-assistant

py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Environment variables

Create a local `.env` file and configure the PostgreSQL connection:

```dotenv
PGHOST=localhost
PGPORT=5432
PGDATABASE=bank_analytics
PGUSER=your_database_user
PGPASSWORD=your_database_password
```

The `.env` file must not be committed to Git.

### Ollama models

Pull the base models:

```powershell
ollama pull qwen2.5-coder:7b
ollama pull embeddinggemma
```

The SQL pipeline uses the local model name:

```text
bank-sql-qwen
```

Create or configure this model using the appropriate project Modelfile and Ollama model commands.

### Database and knowledge initialization

The application requires existing banking analytics tables and the `rag.documents` table with its vector column.

Once PostgreSQL, pgvector, the required schema, and the embedding model are available, load the business knowledge:

```powershell
python rag_loader.py
```

An expected loader result for the current Knowledge Base is:

```text
Saved: KPI_001 (768 dimensions)
Saved: KPI_002 (768 dimensions)
Saved: RULE_001 (768 dimensions)
Saved: RULE_002 (768 dimensions)

RAG LOAD PASSED: 4 documents
```

**Setup limitation:** The repository does not currently provide a complete one-command database bootstrap. The necessary schemas and tables must be provisioned separately.

## 8. Running the SQL Pipeline

For a direct local pipeline test:

```powershell
python -c "from sql_pipeline import run_sql_pipeline; run_sql_pipeline('How many high-value transactions do we have?')"
```

Example observed output:

```text
Database metadata loaded.
Available tables: 4
Created request: 23

RAG knowledge retrieved:
RULE_002 (similarity=0.5119)
KPI_001 (similarity=0.4675)
KPI_002 (similarity=0.4577)

Generated SQL:
SELECT COUNT(*) AS high_value_transactions_count
FROM analytics.fact_transactions
WHERE amount > 10000 AND currency = 'EUR';

Created attempt: 37
Generation validation: PASSED

Pipeline PASSED
```

The output shows knowledge retrieval, SQL generation, and validation. Actual execution results are not returned by this pipeline.

## 9. Security Considerations

This project is an experimental prototype, not a production-approved banking SQL gateway.

Important design considerations include:

- Local LLM inference without a required external AI API.
- Restricted PostgreSQL account permissions.
- Read-only SQL generation and AST-based statement checks.
- Metadata validation and semantic business checks.
- Audit logging for SQL generation attempts.
- No automatic SQL execution within the generation pipeline.
- Exclusion of secrets and backups through `.gitignore`.
- Synthetic or non-sensitive datasets for experimentation.

Production deployment would require additional controls, including access management, policy enforcement, secure configuration, data protection review, monitoring, and adversarial testing.

## 10. Roadmap

Future development areas include:

- **Dynamic Business Rule Validation:** Validate SQL using structured rules stored alongside Knowledge Base definitions.
- **Knowledge Management:** Add controlled creation, review, versioning, and approval of business definitions.
- **Expanded Evaluation:** Add more test cases, verified SQL expectations, and repeated RAG vs. baseline benchmarks.
- **Retrieval Quality:** Improve semantic ranking and handling of irrelevant or ambiguous knowledge.
- **Business Glossary Integration:** Introduce governed business terminology and metadata mapping.
- **Observability:** Expand tracing, metrics, and model evaluation.
- **Reproducible Deployment:** Provide Docker Compose configuration and database initialization scripts.

## 11. Technical Perspective

The project demonstrates the integration of several data and AI engineering disciplines:

**Data Engineering:** PostgreSQL, metadata discovery, schema modeling, and SQL processing.

**AI Engineering:** Local LLM inference, embeddings, semantic retrieval, and prompt context engineering.

**Software Engineering:** Modular Python architecture, automated checks, error handling, and testing.

**Data Governance:** Business definitions, SQL safety validation, metadata consistency, and auditability.

The broader objective is to evolve the prototype toward a governed, metadata-aware AI assistant for enterprise analytics.

---

**Disclaimer:** All banking definitions and examples in this repository are intended for a synthetic learning environment. The project is not affiliated with or endorsed by any financial institution.