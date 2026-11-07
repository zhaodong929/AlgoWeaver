# Office parsing fallback

When Docling is unavailable, `SourceIngestor` can extract basic text from DOCX, PPTX and XLSX with Python's standard-library ZIP/XML tools. The fallback preserves the source hash and records `parser=stdlib-office`; it is intended for plain text, slide text and simple spreadsheet cells.

PDF remains explicitly unsupported without Docling because a reliable general PDF parser requires layout, encoding and table handling beyond a safe small fallback. The adapter never executes macros or imports Office-specific code.
