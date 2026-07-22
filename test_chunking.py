"""Quick sanity check for Part 3: chunking + guardrail with tighter threshold."""

from docubot import DocuBot


def main():
    bot = DocuBot()

    # 1. Verify chunks were built
    print(f"Total chunks: {len(bot.chunks)}")

    # 2. Retrieve for real queries with default threshold
    print("\n" + "=" * 60)
    print("Retrieval test (default threshold):")
    print("=" * 60)
    queries = [
        "Where is the auth token generated?",
        "How does a client refresh an access token?",
    ]
    for q in queries:
        print(f"\n--- Query: {q!r}")
        results = bot.retrieve(q, top_k=3)
        for i, (filename, chunk_text) in enumerate(results, start=1):
            preview = chunk_text[:100].replace("\n", " ")
            print(f"  #{i}  {filename:20s}  ({len(chunk_text)} chars)")
            print(f"        {preview}...")

    # 3. Guardrail test at different thresholds
    print("\n" + "=" * 60)
    print("Guardrail test — payment query at different min_score thresholds:")
    print("=" * 60)
    payment_q = "Is there any mention of payment processing in these docs?"

    for threshold in [1, 5, 10, 20]:
        results = bot.retrieve(payment_q, top_k=3, min_score=threshold)
        status = "✅ empty (guardrail works)" if not results else f"❌ still returned {len(results)} chunk(s)"
        print(f"  min_score={threshold:3d}: {status}")
        if results:
            top_score_chunk = results[0]
            preview = top_score_chunk[1][:60].replace("\n", " ")
            print(f"    top result: {top_score_chunk[0]}: {preview}...")


if __name__ == "__main__":
    main()
