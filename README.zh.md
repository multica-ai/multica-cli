# Multica CLI Skill

> 为 [Multica](https://github.com/multica-ai/multica) 打造 —— 一个开源的、用于运行和管理编码 agent 的可复用 skill 平台。

一个可移植的 skill，教任意本地编码 agent（Claude Code、Codex、Cursor 等）通过已认证的
`multica` CLI 操作 [Multica](https://github.com/multica-ai/multica)：读取与
triage issue、安全地回复评论、管理 metadata，以及处理 mention / status 等副作用。

[English](./README.md) | 简体中文

## 它不会做什么

本仓库**本身不会**授予任何 Multica 访问权限。权限只来自用户本机已登录的 CLI、所选
profile、当前 workspace，以及对每条命令的显式授权。这个 skill 教的是「如何安全地」
操作 Multica，绝不会绕过 workspace 权限，也不会保存任何密钥。

## 覆盖范围

- 检查 CLI 登录、profile、workspace 状态（以及如何登录）
- 读取 issue、comment、metadata、label、自定义 property、subscriber、project、
  agent、squad、runtime、repo、skill、autopilot、attachment
- 跨标题、描述与评论正文搜索 issue
- 低成本地读评论历史 —— 线程扫描、`--compact`、已解决线程的折叠行为
- 用 `--content-file` 安全地写 issue 评论，含文件参数的工作目录限制
- 创建 / 更新 issue 和高价值 metadata
- 处理 mention、status、assignment、rerun、子 issue 等副作用，并用 `--no-start`
  避免误触发 agent run
- 查看 run 历史与 token 用量；在被要求时取消 run
- 把 pull request 关联回 Multica issue
- CLI 做不到的事直说，并指向 Multica Web，而不是假装已完成
- 针对开放式业务目标，定向检索 workspace 内相关资源并形成可执行方案
- 归纳团队已有业务信息，匹配 Agent、Skill 等现有能力
- 优先复用已有成果、避免重复建设，并根据共享风险决定是否新建隔离资源
- 在聊天中展示完整业务编排方案，用户一次确认后按依赖顺序执行（Agent / Skill
  变更仍需单独确认）

## 安装

skill 位于 `skills/multica-cli/`，按你使用的工具选择安装方式。

### Claude Code（插件市场）

```text
/plugin marketplace add multica-ai/multica-cli
/plugin install multica-cli@multica-cli
```

### Codex（skill 安装器）

```bash
install-skill-from-github.py --repo multica-ai/multica-cli --path skills/multica-cli
```

安装新 skill 后请重启 Codex。

### Cursor

把 skill 复制到你的 Cursor 个人 skills 目录：

```bash
mkdir -p ~/.cursor/skills/multica-cli
cp -R skills/multica-cli/* ~/.cursor/skills/multica-cli/
```

或者把项目规则 [`.cursor/rules/multica-cli.mdc`](.cursor/rules/multica-cli.mdc)
放进某个项目的 `.cursor/rules/` 目录。详见 [CURSOR.md](./CURSOR.md)。

### 其他 agent

把 [`skills/multica-cli/SKILL.md`](skills/multica-cli/SKILL.md) 复制到你的工具
加载 skill / 指令的位置即可。

## 前置条件

- 本机已安装 `multica` CLI，且版本 **不低于 v0.4.26**。更早的版本缺少本 skill 依赖的
  命令（尤其是 `--no-start`），会直接报错。可用 `multica version` 确认。
- 用户已通过 `multica login`（或 `multica setup`）完成认证。
- 已选择目标 workspace / profile，或通过 `--workspace-id`、`--profile` 显式传入。

## 用法

安装后，让你的 agent 操作 Multica，例如：

```text
用 multica CLI 读一下 MUL-123，帮我起草一条回复让我 review。
```

也可以直接描述业务目标，让 agent 先查找 workspace 内已有信息和能力：

```text
查找团队已有的数据送标流程和能力，设计每周雨天数据送标方案，等我确认后执行。
```

对于写操作（评论、状态变更、mention、新建 issue），除非用户已经明确授权这个具体动作，
否则 agent 应在改动状态前先确认。更多示例见 [EXAMPLES.md](./EXAMPLES.md)。

## 参与开发

这个 skill 只有在与它所描述的 CLI 保持一致时才有价值，所以文档会对着真实的
`multica` 二进制做 lint：

```bash
scripts/lint-skill-commands.py            # 加 --verbose 可看到每一条检查
python3 scripts/test-orchestration-contract.py
```

当文档里写的命令或 flag 已经不存在、或者 CLI 里有 `SKILL.md` 从未提及的命令时，
lint 会失败。有意不写的部分请加进该脚本的 `UNDOCUMENTED_OK` 并注明原因。CI 在每次
push 和每日定时任务中运行它，让漂移以失败的形式暴露出来，而不是变成一个过期的 skill。

## 许可证

[MIT](./LICENSE)
