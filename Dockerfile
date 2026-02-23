FROM us-central1-docker.pkg.dev/bespokelabs/nebula-devops-registry/nebula-devops:1.0.0
WORKDIR /workspace
# Copy all files to ensure grader.py and solution.sh are available
COPY . /workspace/
RUN chmod +x /workspace/*.sh