# Accio 多账号管理面板

基于 FastAPI 的本地管理面板，支持：

- 多账号本地保存
- 登录链接生成
- 登录成功回调保存 Token
- 账号 JSON 下载与导入
- 查看额度与重置时间
- 单账号 / 批量刷新 Token
- 配置公开回调地址
- 手动启用 / 禁用账号
- 额度耗尽自动禁用，额度恢复自动启用
- 单后台调度器按账号下次检查时间自动巡检额度
- Anthropic 兼容 API：`/v1/models`、`/v1/messages`
- 多账号 API 调度策略：优先填充 / 轮询
- 支持全局上游代理：HTTP / HTTPS / SOCKS4 / SOCKS5
- 内置统计界面：模型调用次数、输入 / 输出 Tokens、账号维度统计

## 启动

```bash
uv sync
uv run accio-panel
```

也可以使用：

```bash
uv sync
uv run python main.py
```

启动后访问：

- `http://127.0.0.1:4097/dashboard`
- `http://127.0.0.1:4097/login`
- `http://127.0.0.1:4097/v1/models`
- `http://127.0.0.1:4097/v1/messages`

## Docker

本地构建：

```bash
docker build -t accio-panel:latest .
```

本地运行：

```bash
docker run -d \
  --name accio-panel \
  -p 4097:4097 \
  -v accio-panel-data:/app/data \
  -e ACCIO_CALLBACK_HOST=127.0.0.1 \
  accio-panel:latest
```

说明：

- 容器内服务监听 `0.0.0.0:4097`
- 默认数据目录是 `/app/data`
- 如果部署到服务器域名，建议在面板配置区填写 `publicBaseUrl`

## GitHub Packages

仓库已添加 GitHub Actions 工作流：

- 文件：`.github/workflows/docker-publish.yml`
- 触发方式：`push` 到 `main`、`workflow_dispatch` 手动触发
- 推送目标：`ghcr.io/<owner>/<repo>`

首次推送成功后，可以在仓库的 `Packages` 页面看到镜像。

首次管理员密码默认值为：

```text
admin
```

可在 `data/config.json` 或面板内配置区中修改。

仓库默认只保留示例配置，不提交真实运行数据：

- `data/config.json`
- `data/stats.json`
- `data/accounts/*.json`
- `.env`

示例文件：

- `data/config.example.json`
- `.env.example`

Anthropic 兼容 API 调用时：

- 使用 `x-api-key` 或 `Authorization: Bearer`
- 值填写当前管理员密码
- `/v1/models` 和 `/v1/messages` 都需要这个鉴权
- 目前仅支持模型：`claude-sonnet-4-6`、`claude-opus-4-6`
- 其他模型会直接返回错误
- 默认调度策略是 `优先填充`，会优先使用顺序靠前且有额度的账号
- 可在面板配置区设置全局上游代理，例如：
  `http://127.0.0.1:7890`、`https://127.0.0.1:7890`、`socks5://127.0.0.1:1080`、`socks5h://127.0.0.1:1080`
- 代理只影响服务端访问 Accio 网关，不影响浏览器登录页

最小调用示例：

```bash
curl http://127.0.0.1:4097/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: admin" \
  -d "{\"model\":\"claude-sonnet-4-6\",\"max_tokens\":256,\"stream\":false,\"messages\":[{\"role\":\"user\",\"content\":\"你好\"}]}"
```

## 数据目录

当前数据结构：

```text
data/
  config.json
  stats.json
  accio-accounts.json
  accounts/
    <account_id>.json
```

- `config.json`：全局配置、管理员密码、会话密钥
- `stats.json`：`/v1/messages` 的累计调用统计
- `accounts/*.json`：每个账号单独一个文件
- `accio-accounts.json`：旧版单文件账号列表，首次启动会自动迁移到 `accounts/` 目录
- 面板支持导入单账号 JSON，也支持直接导入旧版 `accio-accounts.json` 数组文件

## 自动调度

- 系统使用单个后台调度器，不为每个账号单独创建定时器
- 启用中的账号会低频巡检额度
- 自动禁用账号会基于接口返回的重置倒计时安排下次恢复检查
