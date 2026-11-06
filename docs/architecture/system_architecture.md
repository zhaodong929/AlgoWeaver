# AlgoWeaver 系统架构

## 当前可运行切片

```mermaid
flowchart LR
  A[Markdown/text/CSV/JSON] --> B[SourceIngestor]
  B --> C[CapabilityExtractor]
  C --> D[Pydantic AlgorithmCapability]
  D --> E[EvidenceRef + JSON]
  C -. optional .-> F[LangGraph]
  C -. offline .-> G[Fallback runner]
```

Source ingestion currently supports UTF-8 text, Markdown, Python, CSV, JSON and YAML. CSV is normalized to Markdown for downstream extraction while the original bytes are hashed for provenance. Unsupported binary formats return an explicit `unsupported` result until their adapter is added.

## Target workflow

```mermaid
flowchart TD
  U[用户能力描述与资料] --> I[多源接入]
  I --> K[知识抽取与证据绑定]
  K --> R[混合检索与重排]
  R --> P[复刻计划]
  P --> G[代码与测试生成]
  G --> S[隔离沙箱执行]
  S --> V{验证通过?}
  V -- 否 --> F[错误分析与有界修复]
  F --> S
  V -- 是 --> C[能力卡片版本化沉淀]
  C --> R
```

The model interprets and proposes; deterministic code validates schemas, routes states, enforces retry limits and records evidence. `verified` is reserved for an independent validation step.
