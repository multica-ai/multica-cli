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
- 读取 issue、comment、metadata、project、agent、squad、runtime、repo、skill、
  autopilot、attachment
- 用 `--content-file` 安全地写 issue 评论
- 创建 / 更新 issue 和高价值 metadata
- 处理 mention、status、assignment、rerun、子 issue 等副作用
- 把 pull request 关联回 Multica issue

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

- 本机已安装 `multica` CLI。
- 用户已通过 `multica login`（或 `multica setup`）完成认证。
- 已选择目标 workspace / profile，或通过 `--workspace-id`、`--profile` 显式传入。

## 用法

安装后，让你的 agent 操作 Multica，例如：

```text
用 multica CLI 读一下 MUL-123，帮我起草一条回复让我 review。
```

对于写操作（评论、状态变更、mention、新建 issue），除非用户已经明确授权这个具体动作，
否则 agent 应在改动状态前先确认。更多示例见 [EXAMPLES.md](./EXAMPLES.md)。

## 许可证

[MIT](./LICENSE)
