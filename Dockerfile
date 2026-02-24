FROM nebula-devops:1.0.0

WORKDIR /workspace

COPY setup.sh /workspace/setup.sh
COPY solution.sh /workspace/solution.sh
COPY grader.py /workspace/grader.py
COPY task.yaml /workspace/task.yaml

RUN chmod +x /workspace/setup.sh /workspace/solution.sh