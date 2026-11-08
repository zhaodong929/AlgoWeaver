# 预测性维护高风险筛查

## 业务场景

根据设备运行传感器记录筛查可能需要维护的设备，减少人工巡检范围。
本示例使用 UCI AI4I 2020 Predictive Maintenance Dataset，并保留原始
`Machine failure` 标签用于离线评估。

## 输入与输出

- 输入：一行设备记录中的 `Torque [Nm]` 和 `Tool wear [min]`。
- 参数：扭矩阈值 `torque_threshold` 和磨损阈值 `wear_threshold`。
- 输出：风险分数、`is_high_risk` 标记以及原始设备编号。

## 算法步骤

1. 读取并校验扭矩和工具磨损字段。
2. 当扭矩不低于 70 Nm 且工具磨损不低于 180 分钟时标记高风险。
3. 使用数据集的 `Machine failure` 标签计算 precision、recall 和高风险数量。

## 验证要求

- 空数据和非法阈值必须报错。
- 数据集全部 10,000 行可在本地完成推理。
- 记录高风险数量、precision、recall 和运行时间。
