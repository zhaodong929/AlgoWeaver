# Python 历史代码解析

当前 Phase 2 使用 Python 标准库 `ast`，不执行输入代码。`PythonCodeParser` 将文件或文本转换为 `PythonSourceFile`，记录来源 ID、路径、SHA-256、行数、导入、类、方法、函数、装饰器、参数、返回注解、文档字符串和源码行号。

语法错误仍返回带 `status="failed"` 和 `syntax_error` 的结构化对象，便于后续 Agent 将错误作为外部 observation；缺失文件或空输入属于调用错误并直接抛出异常。后续可在不改变 schema 的情况下增加 Tree-sitter 适配器，用于更大规模仓库和增量解析。
