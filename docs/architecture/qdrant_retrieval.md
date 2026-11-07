# Qdrant vector adapter

`QdrantVectorRetriever` is an optional adapter over the existing `EvidenceChunk` and `RetrievalHit` schemas. It accepts externally supplied vectors, stores them in an in-memory or injected Qdrant client, and returns the original source ID, path and line range with every hit.

The test uses Qdrant's local in-memory client and synthetic vectors. It validates the storage/provenance contract only. No embedding model, remote Qdrant service or semantic quality claim is included.
