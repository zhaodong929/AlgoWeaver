# 04 SWE-agent

- 官方仓库：https://github.com/SWE-agent/SWE-agent
- 研究 SHA：`3ea751c087f32b16e039a2233dd6eefecef325d5`
- 重点官方文档：https://github.com/SWE-agent/SWE-agent/blob/main/docs/background/aci.md

## 解决的问题

SWE-agent 面向陌生代码仓库中的软件工程任务：定位文件和符号、编辑代码、运行测试、读取失败信息并继续迭代。核心观点是 Agent-Computer Interface（ACI）设计会显著影响模型完成率，不能只给模型一个通用 shell。

## ACI 设计与核心流程

官方 ACI 文档列出四个关键设计：

1. 编辑命令触发语法检查；语法不正确时拒绝写入。
2. 使用分页文件查看器，默认每次约 100 行，并支持上下翻页。
3. 使用专门的全目录字符串搜索，仅返回命中文件摘要，避免把大量无关上下文塞给模型。
4. 空输出返回明确的成功消息，避免模型把“无输出”误解为失败。

典型循环是：读取任务与仓库摘要 -> 搜索/查看相关文件 -> 生成小范围编辑 -> 运行静态检查/测试 -> 解析错误 -> 继续编辑 -> 达到通过条件或预算上限。

## AlgoWeaver 可复用模式

把算法复刻 Agent 的工作区工具设计成 ACI：`list_files`、`search_text`、`read_file`、`apply_patch`、`run_check`、`run_tests`、`collect_artifact`。工具返回结构化的路径、行号、退出码、标准输出/错误和测试摘要；默认截断长日志并支持按失败测试重新查看。

编辑采用小补丁并在落盘前做语法检查；拒绝跨工作区路径；每轮记录 diff。测试失败必须作为下一轮输入，不能让模型只凭主观反思宣布成功。

## 不直接采用的部分

SWE-agent 的仓库编辑与执行环境是软件工程场景的特化实现，不能直接替代 AlgoWeaver 的算法能力 Schema、证据链和独立验证器。不要把宿主 shell 直接暴露给 LLM；所有命令都应映射到受控工具并在沙箱执行。

## 可改进点

建立“证据门禁”：生成代码只有通过 syntax/import/unit/property 检查才允许写入能力库；失败案例包含最小复现、环境、命令、退出码和日志摘要。使用最大修复轮数和总时间预算，终止后将状态标记为 `Failed` 或 `Pending`。
