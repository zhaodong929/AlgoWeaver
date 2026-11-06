# 数据流与证据边界

1. `SourceIngestor` reads a local file and records source ID, path, format, media type, size and SHA-256.
2. The extraction service sends normalized text to a provider-neutral `ChatModel`.
3. The model response is parsed as `AlgorithmDraft`; invalid or extra fields fail validation.
4. The service attaches `EvidenceRef` from the actual source rather than trusting model-generated citations.
5. Missing required fields produce `needs_review`; Mock output never becomes `verified`.
6. Future retrieval chunks will carry source ID, location, hash and transformation metadata into the reproduction plan.

This separation makes it possible to distinguish raw evidence, model inference, pending review and independently verified results.
