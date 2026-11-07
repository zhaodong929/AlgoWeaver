# Office parsing fallback

When Docling is unavailable, `SourceIngestor` can extract basic text from DOCX, PPTX and XLSX with Python's standard-library ZIP/XML tools, and simple PDF literal text operators with a constrained byte parser. The fallback preserves the source hash and parser metadata.

This remains a narrow text extraction path. It does not claim layout, tables, images, formulas, OCR or compressed/encoded PDF streams. The adapter never executes macros or imports Office-specific code; Docling remains the preferred parser.
