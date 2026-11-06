# Local retrieval baseline

The first retrieval implementation is intentionally dependency-free. `SourceChunker` creates line-addressable `EvidenceChunk` records from normalized sources. Each chunk keeps source ID, type, format, path, line range and copied ingestion metadata.

`LocalLexicalRetriever` indexes chunks by ID and ranks a query using deterministic token overlap. It supports source-type and exact metadata filters and returns `RetrievalHit` objects containing the full evidence chunk, score, matched terms and rank. Empty queries and invalid limits fail fast.

This is a correctness and provenance baseline, not a semantic retrieval claim. Qdrant, sparse/dense hybrid search, embeddings and reranking remain adapter milestones; they must preserve the same chunk and hit provenance contract.
