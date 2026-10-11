# CueAudit 核心框架

[English documentation](README.md)

CueAudit 将候选捷径线索、可执行统计测量、固定阈值筛查和模型验证连接起来，
分别保留数据关联、模型响应与待人工审查线索。

本仓库是从原始脚本整理的核心框架公开版本，包含通用测量模块、确定性流程、
配对模型证据解析接口及五角色模板。它不是历史实验的完整复现包。
仓库不提供论文、实验结果、数据集、模型权重、私人 OpenClaw 配置或会话记录。

## 安装与试运行

需要 Python 3.10 或更新版本。在你选择的 Python 环境中运行：

```powershell
git clone https://github.com/PeiYuanHao/CueAudit-github.git
cd CueAudit-github
python -m pip install -e .
python examples/make_toy_request.py
python -m cueaudit.cli data/toy/request.json --output outputs/toy-audit.json
python -m unittest discover -s tests -v
```

示例仅生成虚构输入，用于检查框架能否运行，不包含任何论文实验数据。
生成的数据和报告保留在本地，并被 Git 忽略。

图像测量和颜色干预需要额外依赖：

```powershell
python -m pip install -e ".[images]"
```

## 核心组件

- 元数据线索：Cramer's V、按预先声明映射计算的 alignment。
- 图像线索：主导 RGB 通道、角落亮度区域、前景覆盖率代理。
- 模型证据：解析用户评估脚本产生的配对 ID/OOD 准确率，计算百分点下降。
- 颜色干预：LAB 灰度归一化及基于掩码的颜色迁移。
- 五角色：Identify、Executive、Quantitative、Qualitative、Summarize。

默认数据筛查规则为 alignment > 0.80、V > 0.50 或前景类别均值差 > 0.10；
模型升级规则为平均配对下降 > 30 个百分点。这些是操作阈值，不是显著性检验。
缺少输入、执行失败、预算终止与低于阈值分别记录，不被合并为“没有捷径”。

Python 流程可独立运行。`openclaw/workspaces/` 提供五个角色的完整公开模板，
并附有独立配置生成器、交接协议和受限接入程序。原始方法摘录与本次新增模板
分别标注。训练与数据集特定验证脚本由使用者提供。

生成上述示例输入后，可运行无模型的五角色交接检查：

```powershell
python examples/run_five_roles.py --mode offline --output outputs/five-role-demo
```

该模式使用固定回复检查流程，不调用语言模型，也不证明历史实验结果。
真实 OpenClaw 模式需要自行配置模型与认证；本次未执行真实模型调用。

详见[接口说明](docs/interface.md)、[OpenClaw 配置说明](docs/openclaw.md)
和[公开范围](docs/release-scope.md)。初始版本尚未选择软件复用许可证。
