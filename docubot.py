"""
Core DocuBot class responsible for:
- Loading documents from the docs/ folder
- Building a simple retrieval index (Phase 1)
- Retrieving relevant snippets (Phase 1)
- Supporting retrieval only answers
- Supporting RAG answers when paired with Gemini (Phase 2)
"""

import os
import glob

class DocuBot:
    # Common English words that carry little meaning for keyword matching.
    # Skipping them stops noisy words like "the" or "is" from inflating scores.
    STOP_WORDS = {
        "a", "an", "and", "are", "as", "at", "be", "by", "do", "does",
        "for", "from", "how", "i", "in", "is", "it", "of", "on", "or",
        "that", "the", "there", "these", "this", "to", "was", "what",
        "when", "where", "which", "who", "why", "with", "you", "your",
        "any", "mention", "me", "my", "can", "will", "would", "should",
    }

    def __init__(self, docs_folder="docs", llm_client=None):
        """
        docs_folder: directory containing project documentation files
        llm_client: optional Gemini client for LLM based answers
        """
        self.docs_folder = docs_folder
        self.llm_client = llm_client

        # Load documents into memory
        self.documents = self.load_documents()  # List of (filename, text)

        # Build a retrieval index (implemented in Phase 1)
        self.index = self.build_index(self.documents)

        # Build paragraph-level chunks (Phase 2)
        self.chunks = self.build_chunks(self.documents)

    # -----------------------------------------------------------
    # Document Loading
    # -----------------------------------------------------------

    def load_documents(self):
        """
        Loads all .md and .txt files inside docs_folder.
        Returns a list of tuples: (filename, text)
        """
        docs = []
        pattern = os.path.join(self.docs_folder, "*.*")
        for path in glob.glob(pattern):
            if path.endswith(".md") or path.endswith(".txt"):
                with open(path, "r", encoding="utf8") as f:
                    text = f.read()
                filename = os.path.basename(path)
                docs.append((filename, text))
        return docs

    # -----------------------------------------------------------
    # Chunking (Phase 2)
    # -----------------------------------------------------------

    def build_chunks(self, documents):
        """
        Split each document into paragraph-level chunks.
        Returns a list of (filename, chunk_id, chunk_text) tuples.
        Empty paragraphs are skipped.
        """
        chunks = []
        for filename, text in documents:
            paragraphs = text.split("\n\n")
            for i, para in enumerate(paragraphs):
                para = para.strip()
                if para:
                    chunks.append((filename, i, para))
        return chunks

    # -----------------------------------------------------------
    # Index Construction (Phase 1)
    # -----------------------------------------------------------

    def build_index(self, documents):
        """
        TODO (Phase 1):
        Build a tiny inverted index mapping lowercase words to the documents
        they appear in.

        Example structure:
        {
            "token": ["AUTH.md", "API_REFERENCE.md"],
            "database": ["DATABASE.md"]
        }

        Keep this simple: split on whitespace, lowercase tokens,
        ignore punctuation if needed.
        """
        index = {}
        # TODO: implement simple indexing
        for filename, text in documents:
            words = text.lower().split()
            for word in words:
                if word not in index:
                    index[word] = []
                if filename not in index[word]:
                    index[word].append(filename)
        return index

    # -----------------------------------------------------------
    # Scoring and Retrieval (Phase 1)
    # -----------------------------------------------------------

    def score_document(self, query, text):
        """
        Return a simple relevance score for how well the text matches the query.

        Baseline:
        - Convert query into lowercase words
        - Skip common stop words (the, is, how, ...) so they don't inflate scores
        - Count how many meaningful query words appear in the text
        - Return the total count as the score
        """
        query_words = query.lower().split()
        text_lower = text.lower()

        score = 0
        for word in query_words:
            # Strip surrounding punctuation from the query word
            clean_word = word.strip("?.,!:;()<>/")
            if not clean_word or clean_word in self.STOP_WORDS:
                continue
            score += text_lower.count(clean_word)

        return score

    def retrieve(self, query, top_k=3, min_score=1):
        """
        Retrieve the top_k most relevant paragraph chunks whose score is at
        least min_score. Returns a list of (filename, chunk_text) tuples.

        If no chunk scores >= min_score, returns an empty list so the caller
        can respond with "I do not know."
        """
        scored = []
        for filename, chunk_id, chunk_text in self.chunks:
            score = self.score_document(query, chunk_text)
            if score >= min_score:
                scored.append((score, filename, chunk_text))

        scored.sort(reverse=True)

        results = []
        for score, filename, chunk_text in scored[:top_k]:
            results.append((filename, chunk_text))
        return results

    # -----------------------------------------------------------
    # Answering Modes
    # -----------------------------------------------------------

    def answer_retrieval_only(self, query, top_k=5):
        """
        Phase 1 retrieval only mode.
        Returns raw snippets and filenames with no LLM involved.
        """
        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        formatted = []
        for filename, text in snippets:
            formatted.append(f"[{filename}]\n{text}\n")

        return "\n---\n".join(formatted)

    def answer_rag(self, query, top_k=3):
        """
        Phase 2 RAG mode.
        Uses student retrieval to select snippets, then asks Gemini
        to generate an answer using only those snippets.
        """
        if self.llm_client is None:
            raise RuntimeError(
                "RAG mode requires an LLM client. Provide a GeminiClient instance."
            )

        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        return self.llm_client.answer_from_snippets(query, snippets)

    # -----------------------------------------------------------
    # Bonus Helper: concatenated docs for naive generation mode
    # -----------------------------------------------------------

    def full_corpus_text(self):
        """
        Returns all documents concatenated into a single string.
        This is used in Phase 0 for naive 'generation only' baselines.
        """
        return "\n\n".join(text for _, text in self.documents)
