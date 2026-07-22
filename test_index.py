"""Quick sanity check for build_index()."""

from docubot import DocuBot


def main():
    bot = DocuBot()
    index = bot.index

    print(f"Total unique words in index: {len(index)}")
    print()

    # Look up a few specific words to see which docs they appear in
    words_to_check = [
        "token",
        "database",
        "authentication",
        "endpoint",
        "payment",       # 应该不存在！
        "processing",    # 应该不存在！
    ]

    for word in words_to_check:
        if word in index:
            print(f"'{word}' -> {index[word]}")
        else:
            print(f"'{word}' -> (not found in any document)")


if __name__ == "__main__":
    main()
