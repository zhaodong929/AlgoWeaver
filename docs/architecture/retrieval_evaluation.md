# Retrieval evaluation and score fusion

`RetrievalEvaluator` computes deterministic Recall@k, mean reciprocal rank and provenance coverage over a small `RetrievalCase` dataset. Provenance coverage measures how many returned hits retain a source ID, path and line location.

`combine_lexical_and_dense_scores` is only a score-fusion primitive. It accepts externally supplied dense scores, but does not load an embedding model or claim that dense retrieval has been validated. Qdrant, embeddings and reranking remain separate adapters evaluated against this contract.
