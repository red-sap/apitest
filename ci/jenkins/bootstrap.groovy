import jenkins.model.Jenkins
import hudson.security.HudsonPrivateSecurityRealm
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import hudson.slaves.DumbSlave
import hudson.slaves.JNLPLauncher
import hudson.slaves.RetentionStrategy
import hudson.model.Node
import hudson.model.ParametersDefinitionProperty
import hudson.model.StringParameterDefinition
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition

Jenkins j = Jenkins.get()
File marker = new File(j.rootDir, '.realworld-bootstrap-complete')
if (!marker.exists()) {
    String username = System.getenv('JENKINS_ADMIN_USER')
    String password = System.getenv('JENKINS_ADMIN_PASSWORD')
    if (!username || !password) throw new IllegalStateException('Bootstrap admin credentials required')
    def realm = new HudsonPrivateSecurityRealm(false)
    realm.createAccount(username, password)
    j.setSecurityRealm(realm)
    def auth = new FullControlOnceLoggedInAuthorizationStrategy()
    auth.setAllowAnonymousRead(false)
    j.setAuthorizationStrategy(auth)
    j.setNumExecutors(0)
    def node = new DumbSlave('api-docker', '本机接口自动化执行节点，使用 Docker 运行 Pytest',
        System.getenv('JENKINS_AGENT_WORKDIR'), '1', Node.Mode.EXCLUSIVE, 'api-docker',
        new JNLPLauncher(), new RetentionStrategy.Always(), [])
    j.addNode(node)
    def job = j.createProject(WorkflowJob, 'realworld-api-tests')
    job.setDisplayName('原野接口自动化')
    job.setDescription('在 api-docker 节点启动测试容器，通过 SSH 拉取指定分支，运行 Pytest 并归档 JUnit、Allure 原始结果和日志。')
    job.setDefinition(new CpsFlowDefinition(new File('/opt/realworld/Jenkinsfile').getText('UTF-8'), true))
    job.addProperty(new ParametersDefinitionProperty([
        new StringParameterDefinition('APP_BASE_URL', 'http://host.docker.internal:8000/api', '测试环境 API 根地址，包含 /api'),
        new StringParameterDefinition('TEST_REPO_URL', 'git@github.com:red-sap/apitest.git', 'SSH 测试代码仓库，留空使用本地代码'),
        new StringParameterDefinition('TEST_BRANCH', 'main', '测试分支'),
        new StringParameterDefinition('TEST_MARKERS', '', '筛选表达式，留空运行全部用例')
    ]))
    job.save()
    j.save()
    marker.text = 'Configured with authentication and one dedicated agent.\n'
}
// Agent 凭据仅写到专用共享卷，不打印到日志。
File secret = new File('/var/jenkins_agent_secret/secret')
secret.text = j.getComputer('api-docker').getJnlpMac()
secret.setReadable(false, false)
secret.setReadable(true, true)
println('RealWorld bootstrap ready: authentication enabled, api-docker node configured.')
