"""Quick sanity check for retrieve()."""

from docubot import DocuBot


def main():
    bot = DocuBot()

    queries = [
        "Where is the auth token generated?",
        "How do I connect to the database?",
        "Which endpoint lists all users?",
        "Is there any mention of payment processing?",
    ]

    for q in queries:
        print(f"\n--- Query: {q!r}")
        results = bot.retrieve(q, top_k=3)
        if not results:
            print("  (no candidates — no query word found in index)")
        else:
            for i, (filename, text) in enumerate(results, start=1):
                preview = text[:80].replace("\n", " ")
                print(f"  #{i}  {filename:20s} preview: {preview}...")


if __name__ == "__main__":
    main()
