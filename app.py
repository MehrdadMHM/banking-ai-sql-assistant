
from sql_pipeline import run_sql_pipeline


def main():
    print("=" * 55)
    print("           BANKING AI SQL ASSISTANT")
    print("             RAG + LLM + VALIDATION")
    print("=" * 55)
    print("Ask questions in natural language.")
    print("Type 'exit' or 'quit' to close the application.")
    print("Generated SQL is validated but NOT executed.\n")

    while True:
        try:
            question = input("Banking AI > ").strip()

            if question.lower() in ("exit", "quit"):
                print("\nGoodbye!")
                break

            if not question:
                print("Please enter a question.\n")
                continue

            print("\nProcessing your question...\n")

            run_sql_pipeline(question)

            print("\n" + "-" * 55)
            print("Ready for your next question.\n")

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        except Exception as exc:
            print(f"\nError: {exc}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()
