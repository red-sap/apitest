# RealWorld API 的 Jenkins Docker 接入

结构为 Jenkins 控制器、常驻 `api-docker` 执行节点、每次构建创建的一次性 Pytest 容器。
控制器不执行测试，也不挂载 Docker socket；执行节点通过宿主机 Docker 启动测试容器。Jenkins 界面强制使用简体中文，配置与脚本按 UTF-8 保存。

## 本机启动

在 `/Users/redsap/api-automation-projects/realworld-api` 中执行：

```bash
docker compose --env-file .ci-local/jenkins.env -f ci/jenkins/compose.yml up -d --build
```

Jenkins 地址：`http://127.0.0.1:8080/`。
任务：`realworld-api-tests`；节点：`api-docker`；节点标签：`api-docker`。
管理员账号和随机密码保存在 `.ci-local/jenkins.env`，文件权限为 600，不应提交到 Git。
该文件还保存本机项目与 Agent 工作目录。移动项目目录后需要同步修改这两项路径。

本配置需要明确授权执行节点持久访问 Docker socket。拥有此 Jenkins 管理权限、任务修改权限或可运行任意分支代码的人，可以通过该节点控制宿主机 Docker；只运行自己信任的测试代码，不将此节点开放给不受信任的仓库或 PR。

Jenkins 保留登录认证和 CSRF 防护，HTTP 端口仅绑定到 127.0.0.1。控制器执行器数量为 0，独立节点执行器数量为 1。同一任务禁止并发运行，避免重复清理测试数据。重启容器不会删除 Jenkins 数据卷。首次初始化创建账号、节点和 Pipeline；再次启动不重置已有任务和密码。

## 运行测试

在任务页面选择构建或参数化构建。首次启动即提供参数入口。

| 参数 | 用途 |
| --- | --- |
| APP_BASE_URL | 测试环境 API 根地址，默认 `http://host.docker.internal:8000/api` |
| TEST_REPO_URL | 留空时复制本地测试代码；以后填写 Git 仓库地址 |
| TEST_BRANCH | Git 分支，默认 main，实际分支可修改 |
| TEST_MARKERS | 留空运行全量；填写 smoke、articles、e2e 等 Pytest 表达式 |

后端必须已经启动。测试容器的 127.0.0.1 是容器自己，访问 Mac 上的后端使用 `host.docker.internal`。Django 的 ALLOWED_HOSTS 已加入这个主机名。没有自动部署后端或 MySQL，也没有配置定时任务。

首次或运行器依赖发生变化时会重新构建镜像。镜像内包含 Python、Git、Pytest、Allure Pytest 插件和启动脚本。容器启动后读取所选测试代码的 requirements.txt 同步依赖，避免分支依赖与镜像不一致。

## Git 配置预留

已配置 SSH 仓库 `git@github.com:red-sap/apitest.git`，默认分支 `main`。启动脚本在每次测试容器内 shallow clone 指定分支，并将实际提交号写入报告。留空 TEST_REPO_URL 仍可运行本地代码快照。

当前 GitHub SSH 认证通过 Docker Desktop 的 `/run/host-services/ssh-auth.sock` 转发本机 SSH agent，socket 只挂载到本次测试容器。私钥不复制到 Jenkins、镜像或仓库。主机 known_hosts 文件只包含已核验的 GitHub 主机密钥，保存在 `.ci-local/ssh/known_hosts`。

重启 Mac 或 SSH agent 后，需要先在 Mac 终端执行 `ssh-add ~/.ssh/id_rsa` 重新加载已获授权的身份；可以通过 `ssh-add -l` 检查。不要运行不受信任的分支代码，因为容器在测试期间可以使用 agent 中已加载的身份。

私有 HTTPS 仓库认证暂未配置，不能把 token 或密码放入仓库 URL。迁移到其他执行环境时，SSH 私有仓库也可通过 Jenkins SSH 私钥凭据提供 `GIT_KEY_FILE`，并通过 `GIT_KNOWN_HOSTS_FILE` 提供事先核验的 known_hosts。`ci/run-container.sh` 只把这两个文件以只读方式挂入本次测试容器；入口强制校验主机密钥，不自动关闭 StrictHostKeyChecking。此私钥文件备用方式需要将凭据绑定加入 Jenkinsfile 后才能使用；不要把密钥写入 Dockerfile 或镜像。

Jenkinsfile 当前由控制器镜像在首次启动时创建为内联 Pipeline。修改 Jenkinsfile 后，需要在任务配置中更新 Pipeline 脚本；重建镜像不会覆盖已存在的任务。接入 Git 后也可将任务切换为 Pipeline from SCM，届时需同时安排运行器构建上下文的来源；当前构建上下文仍是本机测试工程。

## 报告与失败处理

每次构建使用独立目录：`$WORKSPACE/reports/$BUILD_NUMBER/`。
Agent 工作路径与宿主机路径相同，确保 Docker daemon 能正确挂载报告目录。

- `junit.xml`：Jenkins 内置测试结果页，含用例数、失败和错误。
- `allure-results/`：Allure 原始数据，已随构建归档；当前未安装 Jenkins Allure 展示插件及 Allure CLI，不会出现 Allure HTML 页。
- `log/`：测试工程日志。
- `exit-code.txt`：Pytest 或准备阶段的退出码。
- `source-mode.txt`：git 或 local-snapshot。
- `test-commit.txt`：Git 模式下实际提交号；本地模式用 source-files.json 记录文件内容摘要。
- `python-packages.txt`：本轮实际 Python 依赖版本。

Pytest 非零退出码原样传递给容器、docker run、Shell 和 Jenkins，不能通过 echo 或 `|| true` 抹掉。
准备阶段失败也尽可能生成 JUnit 错误记录。测试失败仍执行 post always 并归档报告；没有 XML 的构建不能被当成成功。
默认 Jenkins 超时 20 分钟。测试请求采用连接 5 秒、读取 30 秒的默认超时，可由单次请求显式覆盖。
任务只保留最近 20 次构建。原始报告不包含真实凭据配置，仍应按测试数据访问权限管理。

## 命令行复现

```bash
docker build -f ci/Dockerfile -t realworld-api-runner:local .
bash ci/run-container.sh
TEST_MARKERS=smoke bash ci/run-container.sh
```

命令行报告默认写入 `.ci-local/reports/` 下的独立时间目录。
测试源代码以只读挂载复制到临时目录后执行，不在宿主机源目录写缓存和运行日志。
脚本不会自动读取 .env；配置通过环境变量提供。

## 停止与恢复

```bash
# 停止，不删除账号、任务和构建历史
docker compose --env-file .ci-local/jenkins.env -f ci/jenkins/compose.yml stop
# 恢复
docker compose --env-file .ci-local/jenkins.env -f ci/jenkins/compose.yml up -d
# 查看状态
docker compose --env-file .ci-local/jenkins.env -f ci/jenkins/compose.yml ps
```

不要添加 `down -v`，除非明确要删除 Jenkins 持久数据。管理员密码在 Jenkins 中修改后，旧 env 文件只作为初始化记录，不会自动更新或重置账号。

## 本机命令行触发 Jenkins

```bash
python3 ci/jenkins/manage.py status
python3 ci/jenkins/manage.py run
python3 ci/jenkins/manage.py run --markers smoke
# 临时使用本地快照
python3 ci/jenkins/manage.py run --repo ''
```

助手仅连接本机 8080，从受限本地文件读取认证信息，保留 CSRF 校验，等待构建完成并返回成功或失败退出码。若在 Jenkins 页面修改了管理员密码，请通过安全方式同步本地凭据文件后再用该助手。

## 中文编码

中文插件为 Locale 和 Localization Chinese Simplified，默认语言为 zh_CN，并忽略浏览器的语言偏好。JVM 文件编码为 UTF-8，进程 locale 为 C.UTF-8。通过 API 保存 config.xml 时必须使用 UTF-8 XML 声明及 `Content-Type: application/xml; charset=UTF-8`，避免中文说明被错误解码。已存在的乱码需要用原始中文重新写入，仅调整语言插件不能恢复错误文本。
