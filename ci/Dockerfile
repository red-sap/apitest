FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt-get update && apt-get install -y --no-install-recommends git openssh-client ca-certificates bash \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /opt/runner/requirements.txt
COPY ci/requirements-ci.txt /opt/runner/requirements-ci.txt
RUN python -m pip install --no-cache-dir -r /opt/runner/requirements.txt -r /opt/runner/requirements-ci.txt
COPY ci/run-tests.sh /usr/local/bin/run-tests.sh
RUN chmod +x /usr/local/bin/run-tests.sh
WORKDIR /work
ENTRYPOINT ["/usr/local/bin/run-tests.sh"]
