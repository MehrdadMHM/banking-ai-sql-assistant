# Banking AI SQL Assistant

**A metadata-aware, RAG-powered Text-to-SQL prototype for synthetic banking analytics.**

This project translates natural-language analytics questions into PostgreSQL SQL using a local language model, a business-knowledge retrieval layer, and a multi-stage validation and repair pipeline.

It demonstrates how business definitions, database metadata, SQL parsing, and auditability can be combined to build a more controlled Text-to-SQL workflow. **The generated SQL is not automatically executed by the generation pipeline.**

> **Status:** Local research and engineering prototype—not production-approved software. All examples and business rules are intended for a synthetic banking environment.

## Highlights

- **Business-aware generation:** Retrieve relevant KPI definitions and business rules from a vector knowledge base before generating SQL.
- **Metadata-aware prompting:** Supply the model with database schema context.
- **Multi-layer validation:** Check SQL safety, semantics, supported business metrics, and referenced PostgreSQL metadata.
- **Self-healing workflow:** Attempt SQL repair and revalidation when generation fails checks.
- **Audit logging:** Record requests and generation attempts for diagnosis and evaluation.
- **Comparative testing:** Evaluate SQL generation with and without retrieved knowledge.

## Architecture

```text
 Natural-language banking question
                |
                v
         SQL pipeline
          /         \
         v           v
 Schema & metadata   RAG retrieval
                     |        
              Embedding model
                     |
              PostgreSQL + pgvector
                     |
              Business definitions
          \         /
           v       v
        Local SQL-generating LLM
                  |
                  v
             Generated SQL
                  |
                  v
          Validation engine
          |  AST safety
          |  Semantics
          |  Business metrics
          |  PostgreSQL metadata
                  |
           +------+------+
           |             |
          Pass          Fail
           |             |
           |       Repair & retry
           |             |
           +-------------+
                  |
             Audit logging
                  |
            Validated SQL output
```

**Validation and retrieval are different responsibilities.** RAG supplies context to the model; it does not independently guarantee that SQL complies with a business rule. The current business validator checks supported Gross/Net metrics, while dynamic validation of arbitrary retrieved rules remains a future enhancement.

## Technology stack

| Area | Technology | Role |
|---|---|---|
| Language model | Qwen2.5-Coder 7B via **Ollama** | Local SQL generation and repair |
| Embeddings | EmbeddingGemma via Ollama | 768-dimensional semantic representations |
| Relational database | PostgreSQL | Analytics data, metadata, and audit storage |
| Vector search | pgvector | Semantic retrieval of business knowledge |
| Language | Python | Workflow and integration |
| PostgreSQL driver | psycopg | Database access |
| SQL parser | pglast | PostgreSQL AST-based checks |
| Development | Windows PowerShell; Docker-based local database | Local lab environment |

No external hosted LLM API is required for the demonstrated local model path.

## Example: business-aware Text-to-SQL

**Question:**

> How many high-value transactions do we have?

For this **synthetic lab**, the knowledge base defines a high-value transaction as one with `amount > 10000` and `currency = 'EUR'`.

**Observed SQL output with RAG:**

```sql
SELECT COUNT(*) AS high_value_transactions_count
FROM analytics.fact_transactions
WHERE amount > 10000
  AND currency = 'EUR';
```

The pipeline retrieved `RULE_002` as the most similar document (similarity `0.5119`) and reported `Generation validation: PASSED` for the observed run. The SQL was generated and validated, not automatically executed.

### With vs. without RAG: one observed test

| Criterion | Without RAG | With RAG |
|---|---|---|
| `amount > 10000` | Yes | Yes |
| `currency = 'EUR'` | No | Yes |
| Overall count rather than count by customer | No | Yes |
| Matches this lab's business definition | No | Yes |

Without RAG, the model generated a customer-level grouped query and omitted the EUR filter. With RAG, it generated the aggregate query shown above. **This is one illustrative comparison, not a statistically meaningful performance benchmark.**

## Knowledge base and retrieval

The current knowledge base is in [`knowledge/banking_knowledge.json`](knowledge/banking_knowledge.json). It contains the following *synthetic* definitions:

| Key | Definition |
|---|---|
| `KPI_001` | Gross Transaction Volume (`SUM(amount)`) |
| `KPI_002` | Net Transaction Flow (`SUM(signed_amount)`) |
| `RULE_001` | EUR currency filter |
| `RULE_002` | High-value transaction threshold and EUR constraint |

[`rag_loader.py`](rag_loader.py) creates embeddings and upserts documents in `rag.documents`. [`rag_retriever.py`](rag_retriever.py) searches for relevant documents and formats context for SQL generation.

The retriever currently uses a top-k retrieval strategy. Retrieval scores and document ranking should be evaluated across more questions before being used as confidence estimates.

## SQL generation, validation, and repair

[`sql_pipeline.py`](sql_pipeline.py) coordinates schema discovery, retrieval, generation, validation, repair, and audit logging.

The validation components are separated by responsibility:

| Component | Purpose |
|---|---|
| [`sql_validator.py`](sql_validator.py) | SQL statement safety checks |
| [`semantic_validator.py`](semantic_validator.py) | Supported semantic constraints |
| [`business_metric_validator.py`](business_metric_validator.py) | Supported Gross/Net metric checks |
| [`postgres_validator.py`](postgres_validator.py) | PostgreSQL table/column metadata checks |
| [`validation_engine.py`](validation_engine.py) | Validation orchestration |

[`sql_orchestrator.py`](sql_orchestrator.py) and [`sql_repair.py`](sql_repair.py) support correction attempts when validation fails. The pipeline configuration currently limits repair attempts to three.

**Known limitation:** The current `business_metric_validator.py` does not automatically interpret every rule retrieved from RAG. For example, a high-value-transaction query lacking `currency = 'EUR'` can pass that specific validator. Governed, structured rule validation is on the roadmap.

## Repository layout

```text
banking-ai-sql-assistant/
├── app.py
├── sql_pipeline.py
├── sql_generator.py
├── sql_orchestrator.py
├── sql_repair.py
├── sql_validator.py
├── semantic_validator.py
├── business_metric_validator.py
├── postgres_validator.py
├── validation_engine.py
├── schema_context.py
├── schema_metadata.json
├── metadata_provider.py
├── rag_loader.py
├── rag_retriever.py
├── ai_logger.py
├── evaluation_runner.py
├── evaluation/
│   ├── evaluation_dataset.json
│   └── evaluation_results.csv
├── knowledge/
│   └── banking_knowledge.json
├── tests/
├── Modelfile
├── Modelfile.qwen
├── requirements.txt
└── README.md
```

## Running the project locally

### Requirements

- Python 3.12 (used in the development lab)
- PostgreSQL with pgvector installed and configured
- Local Ollama service with the necessary generation and embedding models
- Database objects required by the application, including the analytics schema and `rag.documents`
- A restricted PostgreSQL account with appropriate access

### 1. Clone and install Python dependencies

```powershell
git clone https://github.com/MehrdadMHM/banking-ai-sql-assistant.git
cd banking-ai-sql-assistant
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a local `.env` file (do not commit it):

```dotenv
PGHOST=localhost
PGPORT=5432
PGDATABASE=bank_analytics
PGUSER=your_database_user
PGPASSWORD=your_database_password
```

### 3. Prepare the local models

```powershell
ollama pull qwen2.5-coder:7b
ollama pull embeddinggemma
```

The pipeline uses the configured local model name `bank-sql-qwen`. Create that model from the appropriate repository `Modelfile` after reviewing its contents and configuration.

### 4. Provision the database

Provision the required schemas, tables, and pgvector extension **before** loading knowledge. The repository currently does **not** contain a complete reproducible database initialization script or a synthetic data seed; database setup remains a prerequisite.

### 5. Load knowledge

```powershell
python rag_loader.py
```

The current JSON knowledge file contains four documents. Loading them should save or update entries identified by `KPI_001`, `KPI_002`, `RULE_001`, and `RULE_002`.

### 6. Generate and validate SQL

```powershell
python -c "from sql_pipeline import run_sql_pipeline; run_sql_pipeline('How many high-value transactions do we have?')"
```

The pipeline prints generation and validation status. It does **not** automatically execute generated SQL.

## Evaluation

The repository includes an evaluation dataset, recorded output, and an evaluation runner:

- [`evaluation/evaluation_dataset.json`](evaluation/evaluation_dataset.json)
- [`evaluation/evaluation_results.csv`](evaluation/evaluation_results.csv)
- [`evaluation_runner.py`](evaluation_runner.py)

These materials support experimentation, not a claim of production-grade business correctness. Stronger evaluation will require verified expected query semantics, additional questions, repeated runs, and negative tests.

## Security and data policy

- Use **synthetic or explicitly authorized non-sensitive** banking data only.
- Keep `.env`, credentials, database backups, and local development artifacts out of Git.
- Do not publish real customer records, internal bank schemas, or organization-specific policy documents without permission.
- Treat generated SQL as untrusted until independently reviewed and checked.
- Read-only permissions and SQL validation reduce risk but do not constitute a production security guarantee.
- Restrict database roles and review any code paths that might execute SQL outside the generation pipeline.

## Roadmap

1. **Reproducible database setup:** Schema-only DDL, pgvector table initialization, and deterministic synthetic data seeds.
2. **Dynamic business rule validation:** Structured, versioned rules evaluated independently against the SQL AST.
3. **Knowledge governance:** Rule ownership, approval workflow, provenance, and change history.
4. **Better evaluation:** Semantic ground truth, retrieval-quality metrics, negative cases, and repeatable A/B tests.
5. **Packaging and observability:** Reproducible Docker deployment, traceability, and operational monitoring.

---

**Disclaimer:** This repository is an independent synthetic banking analytics experiment. It is not affiliated with or endorsed by a financial institution.
