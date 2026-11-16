#!/usr/bin/env python3
"""本机 Jenkins 状态与构建助手；凭据从受限本地文件读取，不打印。"""
import argparse
import base64
import http.cookiejar
import json
from pathlib import Path
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BASE = 'http://127.0.0.1:8080/'
JOB = 'realworld-api-tests'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'run'])
    parser.add_argument('--markers', default='')
    parser.add_argument('--repo', default='git@github.com:red-sap/apitest.git')
    parser.add_argument('--branch', default='main')
    parser.add_argument('--api-url', default='http://host.docker.internal:8000/api')
    args = parser.parse_args()
    config = dict(line.split('=', 1) for line in (ROOT / '.ci-local/jenkins.env').read_text().splitlines() if line and not line.startswith('#'))
    token = base64.b64encode((config['JENKINS_ADMIN_USER'] + ':' + config['JENKINS_ADMIN_PASSWORD']).encode()).decode()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    auth = {'Authorization': 'Basic ' + token}

    def request(path, data=None, headers=None):
        url = path if path.startswith(BASE) else BASE + path.lstrip('/')
        if not url.startswith(BASE):
            raise ValueError('Refusing to send local credentials to another server')
        return opener.open(urllib.request.Request(url, data=data, headers={**auth, **(headers or {})}), timeout=15)

    def get(path):
        with request(path) as response:
            return json.load(response)

    if args.action == 'status':
        status = get('computer/api-docker/api/json?tree=displayName,offline,temporarilyOffline,numExecutors')
        print(json.dumps(status, ensure_ascii=False))
        print(json.dumps(get(f'job/{JOB}/api/json?tree=name,lastBuild[number,result,url,building]'), ensure_ascii=False))
        return 0

    crumb = get('crumbIssuer/api/json')
    crumb_headers = {crumb['crumbRequestField']: crumb['crumb']}
    # 首次 Declarative Pipeline 执行前尚未注册参数，先设置相同的参数元数据。
    with request(f'job/{JOB}/config.xml') as response:
        job_xml = ET.fromstring(response.read())
    properties = job_xml.find('properties')
    if properties is None:
        properties = ET.SubElement(job_xml, 'properties')
    if properties.find('hudson.model.ParametersDefinitionProperty') is None:
        prop = ET.SubElement(properties, 'hudson.model.ParametersDefinitionProperty')
        definitions = ET.SubElement(prop, 'parameterDefinitions')
        for name, default in [('APP_BASE_URL','http://host.docker.internal:8000/api'), ('TEST_REPO_URL','git@github.com:red-sap/apitest.git'), ('TEST_BRANCH','main'), ('TEST_MARKERS','')]:
            definition = ET.SubElement(definitions, 'hudson.model.StringParameterDefinition')
            ET.SubElement(definition, 'name').text = name
            ET.SubElement(definition, 'defaultValue').text = default
            ET.SubElement(definition, 'trim').text = 'true'
        with request(f'job/{JOB}/config.xml', ET.tostring(job_xml, encoding='utf-8', xml_declaration=True), {**crumb_headers, 'Content-Type':'application/xml; charset=UTF-8'}) as response:
            response.read()
    payload = urllib.parse.urlencode({'APP_BASE_URL': args.api_url, 'TEST_REPO_URL': args.repo, 'TEST_BRANCH': args.branch, 'TEST_MARKERS': args.markers}).encode()
    with request(f'job/{JOB}/buildWithParameters', payload, {crumb['crumbRequestField']: crumb['crumb'], 'Content-Type': 'application/x-www-form-urlencoded'}) as response:
        queue_url = response.headers['Location']
    # 某些代理会返回相同控制器的不同主机名，只沿用 Location 中的路径。
    queue_path = urllib.parse.urlsplit(queue_url).path.rstrip('/') + '/api/json'
    print('Build queued.', flush=True)
    deadline = time.monotonic() + 1260
    build = None
    while time.monotonic() < deadline:
        item = get(queue_path)
        if item.get('cancelled'):
            raise RuntimeError('Build was cancelled in queue')
        if item.get('executable'):
            build = item['executable']['number']
            break
        time.sleep(2)
    if build is None:
        raise TimeoutError('Build did not start')
    print(f'Build #{build}: {BASE}job/{JOB}/{build}/', flush=True)
    path = f'job/{JOB}/{build}/'
    while time.monotonic() < deadline:
        state = get(path + 'api/json?tree=number,result,building,artifacts[fileName,relativePath]')
        if not state['building']:
            state['artifact_count'] = len(state.pop('artifacts', []))
            print(json.dumps(state, ensure_ascii=False), flush=True)
            try:
                report = get(path + 'testReport/api/json?tree=failCount,passCount,skipCount')
                print('Tests:', json.dumps(report), flush=True)
            except urllib.error.HTTPError:
                pass
            return 0 if state['result'] == 'SUCCESS' else 1
        time.sleep(3)
    raise TimeoutError('Build did not finish within the local waiting period; inspect Jenkins')


if __name__ == '__main__':
    sys.exit(main())
