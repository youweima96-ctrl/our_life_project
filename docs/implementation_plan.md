# MVP 实施说明

## 当前实现

本仓库已落地一个可运行的 MVP 骨架：

- `backend/` 提供 FastAPI 接口、真实 LLM/启发式双模式 AI 整理、内存仓储和 PostgreSQL 初始迁移草案。
- `miniprogram/` 提供微信小程序页面：首页快速记录、AI 确认、记录时间线、房间、我的。
- `backend/tests/` 覆盖 AI 结构化与房间隐私过滤的核心规则。

当前后端默认使用内存仓储，适合本地串通流程。正式联调时将 `InMemoryRepository` 替换为 PostgreSQL repository，API schema 不需要变化。

## P0 行为边界

- AI 结果不直接成为正式记录，必须调用 `POST /api/events/{event_id}/confirm`。
- `private` 事件只对创建者可见。
- `summary_only` 对房间其他成员隐藏 `raw_content`，只展示标题和摘要。
- 房间周报只使用 `summary_only` 和 `room_visible` 事件。
- AI 高风险标记会保存在 extraction 输出中，后续 UI 应进入安全提示流程，而不是普通复盘流程。

## 下一步替换点

1. 接入真实微信登录，替换小程序中的 `demo-user`。
2. 增加 PostgreSQL repository，并执行 `backend/migrations/001_initial.sql`。
3. 将 `app/services/ai.py` 的 OpenAI-compatible 调用升级为生产级模型路由、重试、日志脱敏和 JSON Schema 失败修复。
4. 增加异步队列处理周报、月报和 AI 重试任务。
5. 完善冲突复盘页，支持对方视角提交和共同复盘展示。

## 验收路径

1. 启动后端：`uvicorn app.main:app --reload --port 8000`。
2. 打开小程序首页，输入一条自然语言记录。
3. 进入 AI 整理确认页，确认保存。
4. 在记录 Tab 看到已确认事件。
5. 创建房间，后续将事件绑定到房间并验证权限过滤。
6. 在我的 Tab 生成个人周报。
