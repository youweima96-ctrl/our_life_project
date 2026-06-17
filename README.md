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

## 小程序配置

用微信开发者工具打开 `miniprogram/`。本地调试时后端地址默认为：

```text
http://127.0.0.1:8000/api
```

可在 `miniprogram/utils/config.js` 修改 `BASE_URL`。该值是后端地址，不是密钥。
