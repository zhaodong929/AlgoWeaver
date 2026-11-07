# ADR-003：分阶段接入文档解析

- 状态：Accepted
- 日期：2026-11-06

第一阶段使用零依赖接入器覆盖文本、Markdown、Python、CSV、JSON、YAML，并记录不支持格式。PDF、DOCX、PPTX、XLSX 优先通过懒加载的 Docling 适配器接入；Docling 不可用时，DOCX/PPTX/XLSX 使用受限的 stdlib ZIP/XML 文本 fallback，PDF 仍明确返回 `unsupported`。解析异常返回 `failed`，不把未验证的解析结果标记为完成。
