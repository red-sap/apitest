FROM jenkins/jenkins:lts-jdk21
USER root
RUN mkdir -p /var/jenkins_agent_secret && chown jenkins:jenkins /var/jenkins_agent_secret
USER jenkins
RUN jenkins-plugin-cli --plugins workflow-aggregator junit locale localization-zh-cn
COPY ci/jenkins/bootstrap.groovy /usr/share/jenkins/ref/init.groovy.d/realworld-bootstrap.groovy
COPY Jenkinsfile /opt/realworld/Jenkinsfile
COPY ci/jenkins/locale.groovy /usr/share/jenkins/ref/init.groovy.d/20-localization.groovy
