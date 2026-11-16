pipeline {
    agent { label 'api-docker' }
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }
    parameters {
        string(name: 'APP_BASE_URL', defaultValue: 'http://host.docker.internal:8000/api', description: '仅测试环境；包含 /api，不能使用容器自己的 127.0.0.1')
        string(name: 'TEST_REPO_URL', defaultValue: 'git@github.com:red-sap/apitest.git', description: 'SSH 测试仓库地址；留空时使用本地代码，不在 URL 中填写密码')
        string(name: 'TEST_BRANCH', defaultValue: 'main', description: '容器内拉取的测试分支')
        string(name: 'TEST_MARKERS', defaultValue: '', description: '留空全量；例如 smoke 或 articles and not e2e')
    }
    environment {
        RUNNER_IMAGE = 'realworld-api-runner:local'
    }
    stages {
        stage('准备环境') {
            steps {
                sh '''#!/usr/bin/env bash
set -euo pipefail
: "${LOCAL_TEST_SOURCE_DIR:?Node must provide LOCAL_TEST_SOURCE_DIR}"
docker version
mkdir -p "$WORKSPACE/reports/$BUILD_NUMBER"
'''
            }
        }
        stage('构建测试镜像') {
            steps {
                sh '''#!/usr/bin/env bash
set -euo pipefail
docker build -f "$LOCAL_TEST_SOURCE_DIR/ci/Dockerfile" -t "$RUNNER_IMAGE" "$LOCAL_TEST_SOURCE_DIR"
'''
            }
        }
        stage('运行接口测试') {
            steps {
                withEnv(["REPORT_HOST_DIR=${env.WORKSPACE}/reports/${env.BUILD_NUMBER}"]) {
                    sh '''#!/usr/bin/env bash
set -euo pipefail
bash "$LOCAL_TEST_SOURCE_DIR/ci/run-container.sh"
'''
                }
            }
        }
    }
    post {
        always {
            // 测试失败仍归档；缺少 XML 时不能默认为成功。
            junit testResults: "reports/${env.BUILD_NUMBER}/junit.xml", allowEmptyResults: false
            archiveArtifacts artifacts: "reports/${env.BUILD_NUMBER}/**", allowEmptyArchive: true
        }
    }
}
