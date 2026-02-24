FROM nebula-devops:1.0.0

WORKDIR /task

COPY setup.sh .
COPY solution.sh .
COPY grader.py .
COPY task.yaml .

RUN chmod +x setup.sh solution.sh