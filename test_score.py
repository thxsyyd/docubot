"""Quick sanity check for score_document()."""

from docubot import DocuBot


def main():
    bot = DocuBot()

    queries = [
        "Where is the auth token generated?",
        "How do I connect to the database?",
        "Is there any mention of payment processing?",
        "Which endpoint lists all users?",
    ]

    for q in queries:
        print(f"\n--- Query: {q!r}")
        for filename, text in bot.documents:
            score = bot.score_document(q, text)
            print(f"  {filename:20s} score={score}")


if __name__ == "__main__":
    main()
