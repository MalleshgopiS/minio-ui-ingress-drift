FROM us-central1-docker.pkg.dev/bespokelabs/nebula-devops-registry/nebula-devops:1.0.0
WORKDIR /workspace
# Copying all scripts into workspace
COPY . /workspace/
RUN chmod +x /workspace/*.sh