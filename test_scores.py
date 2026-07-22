"""Diagnose: what scores do our 8 sample queries actually get for their BEST chunk?"""

from docubot import DocuBot
from dataset import SAMPLE_QUERIES


def main():
    bot = DocuBot()

    print("For each sample query, show the top chunk's score at min_score=0")
    print("(this tells us what threshold we can safely use)")
    print()

    for q in SAMPLE_QUERIES:
        # Retrieve with no threshold, top 1
        results_raw = []
        for filename, chunk_id, chunk_text in bot.chunks:
            score = bot.score_document(q, chunk_text)
            results_raw.append((score, filename, chunk_text))
        results_raw.sort(reverse=True)
        top_score, top_file, top_chunk = results_raw[0]

        preview = top_chunk[:70].replace("\n", " ")
        print(f"  score={top_score:3d}  {top_file:20s}")
        print(f"    Q: {q}")
        print(f"    top: {preview}...")
        print()


if __name__ == "__main__":
    main()
