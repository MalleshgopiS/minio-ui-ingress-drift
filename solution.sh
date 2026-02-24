#!/bin/bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: minio-ui-ingress
  namespace: minio
spec:
  rules:
  - host: minio-ui.devops.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: minio-console
            port:
              number: 9001
EOF