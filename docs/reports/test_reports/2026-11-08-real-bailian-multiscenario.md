# 真实百炼多场景验证记录

日期：2026-11-08（Asia/Shanghai）

## 结论

本记录区分真实百炼调用、隔离运行和离线测试。当前工作区 `.env` 默认仍为 `mock`，因此普通启动不会消耗额度；下面的真实烟测在单次 PowerShell 进程中临时覆盖 provider mode，没有把密钥写入源码或提交到 Git。

## Provider 烟测

临时环境变量：

```powershell
$env:ALGOWEAVER_LLM_MODE="litellm"
$env:ALGOWEAVER_EMBEDDING_MODE="dashscope"
$env:ALGOWEAVER_RERANKER_MODE="dashscope"
```

实际返回证据：

- `qwen3.8-max-0902`：真实返回结构化 JSON，用于移动平均材料的能力理解和计划生成。
- `deepseek-v4.1-flash-1017`：真实返回结构化 Python 源码和测试源码，用于异常检测、预测性维护和库存预测复刻。
- `qwen3.7-text-embedding-flash`：2 条向量，真实维度为 1024。
- `qwen3-rerank`：返回真实排序分数；`inventory demand forecast` 得分高于无关图像分类材料。

## 多场景端到端结果

| 场景 | 真实模型路径 | 隔离执行 | 结果 |
|---|---|---:|---|
| 移动平均/库存预测 | Qwen 抽取 + DeepSeek 代码生成 | 未执行完整代码 | 生成模式为 `llm`，产物和静态接口检查已保存 |
| 设备传感器 Z-score 异常检测 | DeepSeek 代码生成 | WSL Docker | 生成的 `detect_anomalies` 通过全部隔离测试，运行状态 `passed` |
| AI4I 预测性维护 | DeepSeek 代码生成 | WSL Docker | 第一轮真实生成暴露定制阈值失败；第二轮在明确 entrypoint 后通过 8 项隔离测试 |
| AI4I 原始示例 | 审核基线代码 | 本地 pytest | 2 passed，覆盖阈值、精度/召回和输入错误 |
| 传感器异常原始示例 | 审核基线代码 | 本地 pytest | 3 passed，覆盖尖峰、常数序列和非法输入 |

## 真实失败与修复

第一轮预测性维护真实生成在 8 项测试中 7 项通过，定制阈值测试失败。失败信息来自隔离 WSL Docker 执行，不是人工补写答案。随后将失败的生成产物交给真实 `deepseek-v4.1-flash-1017` 修复边界，修复器只允许替换已有 `algorithm.py`，并再次在同一隔离策略下执行：

- `repair_applied`: `True`
- 最终状态：`passed`
- 退出码：`0`
- 最大修复次数：由 `BoundedRepairLoop` 限制

同时修复了 WSL UTF-16 诊断输出在 Windows GBK 控制台中引发 `UnicodeEncodeError` 的问题；现在失败原因会被保留并安全打印。

## 可复现产物

运行输出位于本地 `data/processed/real_api_*`，该目录被 `.gitignore` 排除，避免提交真实响应、运行日志和本地数据。可按本报告中的命令重新生成；最终交付文档和截图已提交到 GitHub。
