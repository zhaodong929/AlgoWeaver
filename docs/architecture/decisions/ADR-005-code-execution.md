# ADR-005：生成代码默认进入隔离执行器

- 状态：Accepted for planned execution milestone
- 日期：2026-11-06

参考 SWE-agent ACI 与 OpenHands Workspace/Sandbox，生成代码不得直接在宿主机运行。执行器必须有超时、CPU/内存、文件目录和网络策略，且不注入 API Key。Docker 可用性确认前只提供 dry-run 或安全的静态检查。
