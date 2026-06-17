# 安全说明

## 密钥管理

- 禁止将 `LLM_API_KEY`、数据库密码、Redis 密码、对象存储密钥提交到 Git。
- 本地使用 `backend/.env` 保存真实密钥；仓库只保留 `backend/.env.example`。
- 生产环境使用 GitHub Actions Secrets、云平台 Secret Manager 或容器运行时环境变量注入。

## 前端边界

- 微信小程序只允许保存 `BASE_URL` 这类非敏感配置。
- 小程序不得保存、拼接或转发任何 LLM API key。
- 所有 AI 请求必须先到业务后端，再由后端读取环境变量调用模型服务。

## 后端边界

- 后端记录 AI 调用时只能保存 `input_hash`、`prompt_version`、`model_name` 和结构化输出，不记录真实密钥。
- 生成房间报告时必须在后端过滤权限：`private` 不进入房间上下文，`summary_only` 不暴露原文。
- 删除事件后，后续报告不得继续引用该事件。

## 提交前检查

运行：

```bash
rg -n "sk-|API_KEY|SECRET|TOKEN|PASSWORD|DATABASE_URL|REDIS_URL" .
```

若发现真实密钥，先从 Git 历史和本地文件中移除，再推送。

