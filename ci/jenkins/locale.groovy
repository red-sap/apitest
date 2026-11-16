import hudson.plugins.locale.PluginImpl

def settings = PluginImpl.get()
settings.setSystemLocale('zh_CN')
settings.setIgnoreAcceptLanguage(true)
settings.setAllowUserPreferences(false)
settings.save()
println('Jenkins interface locale configured: zh_CN, UTF-8.')

def j = jenkins.model.Jenkins.get()
j.setSystemMessage('原野接口自动化平台：选择测试环境与分支后运行，报告随构建归档。')
def node = j.getNode('api-docker')
if (node != null) node.setNodeDescription('本机接口自动化执行节点，使用 Docker 运行 Pytest')
j.save()
