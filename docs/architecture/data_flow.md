# 数据流与证据边界

1. `SourceIngestor` reads one or more local files through `ingest_path()`/`ingest_paths()` and records source ID, path, format, media type, size and SHA-256 for every source. Batch ingestion retains `ingested`, `unsupported` and `failed` results independently.
2. The extraction service sends normalized text to a provider-neutral `ChatModel`.
3. The model response is parsed as `AlgorithmDraft`; invalid or extra fields fail validation.
4. The service attaches `EvidenceRef` from the actual source rather than trusting model-generated citations. When available, application-controlled line range and content SHA-256 are stored alongside the excerpt.
5. Missing required fields produce `needs_review`; Mock output never becomes `verified`.
6. `SourceChunker` creates chunks for every successfully readable source; the reproduction graph and API aggregate those chunks while preserving source ID, path, format, line range and transformation metadata in every retrieval hit.

This separation makes it possible to distinguish raw evidence, model inference, pending review and independently verified results.
