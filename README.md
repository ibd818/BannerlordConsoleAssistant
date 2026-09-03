# Bannerlord Console Assistant

一个用于《Mount & Blade II: Bannerlord》官方控制台的命令管理与生成工具。它不会修改游戏文件、注入游戏进程或读取游戏内存，只生成命令并复制到剪贴板。

## 功能

- 面向 Bannerlord v1.4.8.119303 / War Sails v1.2.8.119303
- 163 条命令直接提取自本机 Shipping Client DLL，另含 3 条内置控制台工具命令
- 按经济、角色、军队、政治、领地、任务、战斗、航海、多人等分类浏览
- 搜索命令名称、说明、模板与关键词
- 根据参数实时生成完整控制台命令
- 对英雄、兵种、物品、领地、势力、王国、文化、技能、特性、建筑、工坊、船体、场景等固定目标提供下拉列表和中英文模糊匹配
- 候选项显示为“英文 ID/名称（中文名）”，生成命令始终使用英文原始值；任务名、部队名等随存档变化的目标仍可手动输入
- 一键复制命令到剪贴板
- 独立的 UTF-8 `commands.json`，支持不改源码扩展
- 独立的 UTF-8 `entities.json`，按目标游戏版本保存候选目录
- 深色中文界面，高 DPI 适配

## 项目结构

```text
src/bannerlord_assistant/
├── app.py                 # PySide6 界面
├── core.py                # 数据校验、搜索和命令生成
├── data/commands.json     # 默认命令库与参数目录引用
└── data/entities.json     # 当前版本目标 ID、英文名和中文显示标签
tests/test_core.py         # 核心逻辑测试
build.ps1                  # Windows 单文件构建脚本
run.ps1                    # 源码运行脚本
```

## 源码运行

需要 Python 3.10 或更高版本。在 PowerShell 中执行：

```powershell
python -m pip install -r requirements.txt
.\run.ps1
```

## 构建 Windows 单文件 EXE

```powershell
.\build.ps1
```

构建脚本会在 `work/build-venv` 中创建隔离环境，不会修改系统 Python。若默认 PyPI 网络较慢，可以指定镜像：

```powershell
.\build.ps1 -IndexUrl https://pypi.tuna.tsinghua.edu.cn/simple
```

构建产物为 `outputs/BannerlordConsoleAssistant.exe`，目标电脑不需要安装 Python。

推送到 `main`、提交 Pull Request 或手动运行 GitHub Actions 的 `Build Windows EXE` 工作流时，GitHub Windows runner 会自动安装依赖、运行核心测试并构建 EXE。构建成功后，可从工作流运行页面下载 `BannerlordConsoleAssistant-windows` artifact。

## 编辑命令库

程序首次运行时，会把默认命令库复制到：

```text
%LOCALAPPDATA%\Bannerlord Console Assistant\commands.json
```

点击界面左下角的“打开命令库”即可编辑。保存后点击“重新加载”，无需重启程序。这样 EXE 可以单文件运行，同时命令数据仍可独立维护。

新版内置命令库版本发生变化时，程序会先将旧库备份为 `commands.backup-日期时间.json`，再安装新版完整库；同一版本内不会覆盖你的手工修改。

多参数控制台命令使用 ` | ` 分隔，例如：

```text
campaign.add_troops imperial_legionary | 50
```

本版本命令库不再使用跨版本网页清单。命令名称直接来自本机 v1.4.8 `Win64_Shipping_Client` 程序集的 `CommandLineArgumentFunction` 属性，参数优先取自对应方法内置的 Format/Usage 文本。命令详情会显示来源 DLL 和适用场景；游戏内 `help` 输出仍是最终依据。

最简格式兼容以下写法：

```json
{
  "name": "增加金币",
  "description": "增加玩家金币",
  "command": "campaign.add_gold_to_hero {amount}",
  "parameters": ["amount"],
  "category": "经济"
}
```

推荐使用扩展参数格式，以显示中文标签和默认值：

```json
{
  "name": "增加金币",
  "description": "增加玩家金币",
  "command": "campaign.add_gold_to_hero {amount}",
  "parameters": [
    {
      "key": "amount",
      "label": "金币数量",
      "default": "100000",
      "placeholder": "例如：100000",
      "type": "integer"
    }
  ],
  "category": "经济",
  "keywords": ["金币", "gold", "钱"]
}
```

有限目标参数可增加 `catalog` 字段，例如：

```json
{
  "key": "troop_id",
  "label": "兵种 ID",
  "catalog": "troops"
}
```

目录项的 `value` 是最终写入命令的原始值，`label` 只用于界面显示，`aliases` 用于英文 ID、英文名和中文名的包含匹配。当前版本的中文标签来自版本化中文文本数据，作为辅助参考；游戏内 `help` 和实际模块数据仍是命令是否可用的最终依据。

模板中每个 `{参数名}` 都必须在 `parameters` 中声明，反之亦然。命令可能随游戏版本变化；默认库中的版本提示可直接通过数据文件修订。

## 扩展预留

数据访问与界面已分层，后续可在不改命令渲染核心的情况下加入远程命令库更新、兵种/装备/城镇 ID 数据源、收藏列表，以及开局配置批量生成。
