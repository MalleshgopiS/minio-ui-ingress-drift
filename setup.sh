#!/usr/bin/env bash
set -e

echo "Waiting for Kubernetes API + bleater namespace..."

# CLUSTER CONVERGENCE 

for i in {1..60}; do
  if kubectl get namespace bleater >/dev/null 2>&1; then
    echo "Namespace bleater ready"
    break
  fi
  sleep 5
done

kubectl get namespace bleater \
  || { echo "Namespace bleater not ready"; exit 1; }

echo "Injecting ingress drift..."


kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bleater-ui
  namespace: bleater
spec:
  rules:
  - host: minio.devops.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: wrong-service
            port:
              number: 80
  tls:
  - hosts:
    - minio.devops.local
    secretName: wrong-secret
EOF

echo "Drift injected Successfully"