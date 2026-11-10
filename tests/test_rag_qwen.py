
from schema_context import get_schema_context
from rag_retriever import retrieve_rules, format_rag_context
from sql_generator import generate_sql


def main():
    question = (
        "Show top 5 customers by net transaction flow in EUR"
    )

    print("=" * 60)
    print("USER QUESTION")
    print(question)

    # Step 1: Retrieve relevant banking knowledge
    rules = retrieve_rules(question, top_k=3)

    print("\nRETRIEVED RAG KNOWLEDGE")
    for rule in rules:
        print(
            f"{rule['document_key']}: "
            f"{rule['title']} "
            f"(similarity={rule['similarity']:.4f})"
        )

    rag_context = format_rag_context(rules)

    # Step 2: Load database metadata
    schema_context = get_schema_context()

    print("\nSCHEMA CONTEXT")
    print(f"Loaded {len(schema_context)} characters")

    # Step 3: Generate SQL using Qwen + RAG
    print("\nGENERATING SQL WITH QWEN + RAG...")

    sql = generate_sql(
        question=question,
        schema_context=schema_context,
        rag_context=rag_context
    )

    print("\nGENERATED SQL")
    print(sql)

    # Step 4: Basic checks
    normalized = " ".join(sql.lower().split())

    checks = {
        "SELECT statement": normalized.startswith("select"),
        "Net flow metric": "signed_amount" in normalized,
        "EUR currency": "'eur'" in normalized,
        "Top 5": "limit 5" in normalized,
        "Transaction table": "fact_transactions" in normalized,
        "Customer table": "dim_customers" in normalized,
    }

    print("\nBASIC CHECKS")

    for name, passed in checks.items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")

    if not all(checks.values()):
        raise AssertionError(
            "Generated SQL did not pass all basic checks."
        )

    print("\nRAG + QWEN TEST PASSED")


if __name__ == "__main__":
    main()
