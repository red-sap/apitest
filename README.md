# Real World API 接口自动化测试

基于本地 Swagger（`http://127.0.0.1:8000/swagger/`，Swagger 2.0，13 path / 22 操作）构建的 Pytest 接口测试工程，
按 Glazero 参考工程分层（apis 封装 / cases/api YAML / tests/api 测试 / utils 公共组件 / fixture 承载关联）。

## 知识匹配状态

**没有对应的知识库。** 已读取知识库总索引 `/Users/redsap/agent-workspace/knowledge/INDEX.md`，
其中仅含「商城」「OTA」（学习用模拟案例）与「云存储」（真实业务），与本项目的「博客/文章/评论/关注」业务均不匹配。
因此本次测试**当前依据接口文档 + 后端实现源码（/Users/redsap/pycharm/realWorld-DjangoRestFramework）+ 实测验证生成**，
全部 22 个操作的知识状态为 `not_found`，业务规则断言覆盖待补充（详见 `reports/knowledge_gaps.md`）。

## 目录结构

```
realworld-api/
├── apis/                 # 接口封装（users/user/profiles/articles/tags）
├── cases/api/            # 参数化 YAML 用例（顶层 cases 列表）
├── tests/api/            # 测试（各域 conftest/helpers/test_*.py）
├── utils/                # rest_client / yaml_loader / case_utils / config / assertions 等
├── conftest.py           # 根 fixture：api_client / test_user / second_user / auth_headers + 会话清理
├── fixtures.yaml         # 自定义 fixture 声明（本工程关联用纯 Python fixture，保留空列表）
├── config.yaml           # 配置（base_url，支持 APP_BASE_URL 环境变量覆盖）
├── specs/                # Swagger 快照 + SHA256
├── reports/              # 结构校验 / 知识匹配 / 文档缺口 / 关联图 / 覆盖 / 执行 / 清理报告
├── pytest.ini / requirements.txt / .env.example
```

## 安装与运行

```bash
cd /Users/redsap/api-automation-projects/realworld-api
# 首次使用时创建项目自己的虚拟环境（已有 venv 则跳过）
/Library/Frameworks/Python.framework/Versions/3.10/bin/python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt   # requests / PyYAML / pytest
python -m pytest -q                         # 全量运行
python -m pytest tests/api/articles -q      # 单模块运行
```

终端显示 `(venv)` 不能确认当前使用的是哪个项目的环境。运行
`python -c "import sys; print(sys.executable)"`，路径应位于本项目的 `venv/bin` 下。
若仍指向 `glazero/venv` 等其他项目，请重新执行 `source venv/bin/activate`。
也可以直接运行 `./venv/bin/python -m pytest -q`，无需激活环境。
PyCharm 的项目解释器应选择本项目的 `venv/bin/python`。
运行接口测试前，确保后端服务已在 `http://127.0.0.1:8000` 启动。

## 鉴权依赖

- 注册 `POST /users` → 登录 `POST /users/login`（返回 token）→ 请求头 `Authorization: Token <token>`。
- 由根 `conftest.py` 的 `test_user`/`second_user` fixture 承载，session 级复用，会话结束自动清理账号。

## 接口覆盖

覆盖全部 22 个操作（正常 / 边界异常 / 权限 / 链路），含一条端到端链路
（创建文章→读取→评论→收藏→取消收藏→删除）。详见 `reports/coverage.md`。

## 发现的缺陷（详见 reports/document_gaps.md）

1. GET /articles/feed 响应结构错误（文章被塞入 `comments` 键）。
2. GET /profiles 恒返回 `Invalid User`。
3. POST /profiles 仅首次成功（空 email 唯一冲突）。
4. PUT /user 缺字段抛 500。
5. DELETE 评论无鉴权 / 无归属校验。
6. DELETE /profiles/{username} 无归属校验。
7. 多处错误码滥用 404。

## 结构验收

已通过技能结构校验脚本（`reports/layout_validation.json`，status=passed），与 pytest 均通过。

## Jenkins 与 Docker 接入

运行镜像、独立执行节点、参数化 Pipeline、报告与 Git 分支配置见 [ci/README.md](ci/README.md)。
# apitest
