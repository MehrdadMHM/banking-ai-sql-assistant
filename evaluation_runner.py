
import argparse
import csv
import json
import re
import time
from pathlib import Path

from schema_context import get_schema_context
from metadata_provider import get_table_columns
from sql_generator import generate_sql
from rag_retriever import retrieve_rules, format_rag_context
from validation_engine import validate_generated_sql


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "evaluation" / "evaluation_dataset.json"
RESULTS_PATH = BASE_DIR / "evaluation" / "evaluation_results.csv"


def metric_matches(sql, expected):
    match = re.fullmatch(
        r"SUM\((amount|signed_amount)\)",
        expected,
        flags=re.IGNORECASE
    )

    if not match:
        raise ValueError(f"Unsupported metric: {expected}")

    column = match.group(1)

    pattern = (
        r"\bSUM\s*\(\s*"
        r"(?:[a-z_][a-z_0-9]*\s*\.\s*)?"
        + re.escape(column)
        + r"\s*\)"
    )

    return bool(re.search(pattern, sql, re.IGNORECASE))


def filter_matches(sql, expected):
    match = re.fullmatch(
        r"currency\s*=\s*'([A-Z]{3})'",
        expected,
        flags=re.IGNORECASE
    )

    if not match:
        raise ValueError(f"Unsupported filter: {expected}")

    currency = match.group(1)

    pattern = (
        r"\bcurrency\s*=\s*'"
        + re.escape(currency)
        + r"'"
    )

    return bool(re.search(pattern, sql, re.IGNORECASE))


def evaluate_sql(sql, test_case):
    checks = {}

    if "expected_metric" in test_case:
        checks["metric"] = metric_matches(
            sql, test_case["expected_metric"]
        )

    if "expected_filter" in test_case:
        checks["filter"] = filter_matches(
            sql, test_case["expected_filter"]
        )

    if "expected_tables" in test_case:
        checks["tables"] = all(
            re.search(
                r"\b" + re.escape(table) + r"\b",
                sql,
                re.IGNORECASE
            )
            for table in test_case["expected_tables"]
        )

    if "expected_limit" in test_case:
        limit = test_case["expected_limit"]

        checks["limit"] = bool(
            re.search(
                rf"\bLIMIT\s+{limit}\b",
                sql,
                re.IGNORECASE
            )
        )

    if "expected_order" in test_case:
        direction = test_case["expected_order"]

        checks["order"] = bool(
            re.search(
                rf"\bORDER\s+BY\b[\s\S]*?\b{direction}\b",
                sql,
                re.IGNORECASE
            )
        )

    return checks


def run_case(test_case, mode, schema_context, metadata):
    question = test_case["question"]
    rag_context = None
    retrieved_keys = []

    start = time.perf_counter()

    try:
        if mode == "RAG":
            rules = retrieve_rules(question, top_k=3)
            rag_context = format_rag_context(rules)
            retrieved_keys = [
                rule["document_key"] for rule in rules
            ]

        sql = generate_sql(
            question,
            schema_context,
            rag_context=rag_context
        )

        checks = evaluate_sql(sql, test_case)

        validation = validate_generated_sql(
            question,
            sql,
            metadata=metadata
        )

        # A pass requires all expected checks AND validation.
        passed = all(checks.values()) and validation["valid"]

        error = "; ".join(validation["errors"])

    except Exception as exc:
        sql = ""
        checks = {}
        passed = False
        error = f"{type(exc).__name__}: {exc}"

    elapsed = round(time.perf_counter() - start, 2)

    return {
        "test_id": test_case["id"],
        "mode": mode,
        "passed": passed,
        "duration_seconds": elapsed,
        "checks": json.dumps(checks),
        "retrieved_keys": ",".join(retrieved_keys),
        "validation_error": error,
        "generated_sql": sql,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Number of test cases to run"
    )
    args = parser.parse_args()

    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")

    with DATASET_PATH.open("r", encoding="utf-8-sig") as f:
        dataset = json.load(f)

    if not isinstance(dataset, list) or not dataset:
        raise ValueError("Evaluation dataset must be a nonempty list")

    if args.limit is not None:
        dataset = dataset[:args.limit]

    schema_context = get_schema_context()
    metadata = get_table_columns()

    results = []

    for test_case in dataset:
        print(f"\n{'=' * 60}")
        print(f"{test_case['id']}: {test_case['question']}")

        for mode in ("BASELINE", "RAG"):
            result = run_case(
                test_case, mode, schema_context, metadata
            )
            results.append(result)

            status = "PASS" if result["passed"] else "FAIL"
            print(
                f"{mode}: {status} "
                f"({result['duration_seconds']} sec)"
            )

            if result["validation_error"]:
                print("  Error:", result["validation_error"])

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with RESULTS_PATH.open(
        "w", newline="", encoding="utf-8-sig"
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=list(results[0].keys())
        )
        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")

    for mode in ("BASELINE", "RAG"):
        subset = [r for r in results if r["mode"] == mode]
        passed = sum(r["passed"] for r in subset)
        total = len(subset)
        accuracy = 100 * passed / total

        print(f"{mode}: {passed}/{total} ({accuracy:.1f}%)")

    print(f"\nResults saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
