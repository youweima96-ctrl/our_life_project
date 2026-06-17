# 人生项目组 MVP

微信小程序 + FastAPI 的 MVP 工程骨架，用于验证“AI 快速记录 + 人工确认 + 双人冲突复盘”的核心闭环。

## 目录

- `backend/`：FastAPI API、AI 编排、内存仓储、数据库迁移草案。
- `miniprogram/`：微信小程序页面与 API client。
- `docs/`：实施计划、接口与数据说明。
- `人生项目组_AI优先版_产品需求与设计说明书_MVP.md`：原始 PRD。

## 本地启动后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

默认使用内存数据，便于快速验证交互。配置 `LLM_API_KEY` 后可替换 `app/services/ai.py` 中的启发式实现为真实模型调用。

真实 LLM 有两种本地配置方式：

- 在浏览器版 MVP 的“AI 设置”页填写 `Base URL`、`Model`、`API Key`。
- 在后端环境变量中配置 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL`。

当前使用 OpenAI-compatible Chat Completions 协议，默认地址是 `https://api.openai.com/v1`。没有配置 key 或调用失败时，后端会自动回退到本地启发式整理，保证演示流程不中断。

浏览器版 MVP：

```text
http://127.0.0.1:8000/
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

安全约定：

- `LLM_API_KEY`、数据库密码、对象存储密钥只允许放在后端环境变量或部署平台 Secret 中。
- 微信小程序前端只保存后端 API 地址，不保存任何模型、数据库或第三方服务密钥。
- `.env` 和 `.env.*` 已加入 `.gitignore`，提交前不要移除该规则。
- 后端负责代理所有 AI 调用，前端不得直连 LLM API。
- 浏览器设置页仅用于本地开发：key 发送给本机后端并存于内存，刷新后端进程会丢失；生产环境应改用部署平台 Secret。

## 小程序配置

用微信开发者工具打开 `miniprogram/`。本地调试时后端地址默认为：

```text
http://127.0.0.1:8000/api
```

可在 `miniprogram/utils/config.js` 修改 `BASE_URL`。该值是后端地址，不是密钥。
