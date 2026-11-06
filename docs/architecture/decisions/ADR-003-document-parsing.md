# ADR-003：分阶段接入文档解析

- 状态：Accepted
- 日期：2026-11-06

第一阶段使用零依赖接入器覆盖文本、Markdown、Python、CSV、JSON、YAML，并记录不支持格式。PDF、DOCX、PPTX、XLSX 在确认 Docling 版本和 Windows 兼容性后再加入适配器，不把未验证的解析器标记为完成。
