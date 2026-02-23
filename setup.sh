#!/bin/bash
set -e

# ---------------------- DO NOT CHANGE ----------------------
echo "Ensuring supervisord is running..."
/usr/bin/supervisord -c /etc/supervisor/supervisord.conf 2>/dev/null || true
sleep 5

export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

echo "Waiting for k3s..."
until kubectl get nodes &>/dev/null; do
    sleep 2
done
echo "k3s ready"
# ------------------------------------------------------------


# ===== CUSTOM TASK SETUP =====

echo "Waiting for bleater namespace..."
until kubectl get ns bleater &>/dev/null; do
    sleep 3
done

echo "Waiting for MinIO deployment..."
until kubectl get deployment bleater-minio -n bleater &>/dev/null; do
    sleep 5
done

echo "Waiting for MinIO ingress..."
until kubectl get ingress bleater-ui -n bleater &>/dev/null; do
    sleep 5
done

echo "Introducing ingress drift..."

kubectl patch ingress bleater-ui -n bleater --type='merge' -p '
spec:
  tls:
  - hosts:
    - minio.devops.local
    secretName: wrong-secret
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
'

echo "Ingress drift created successfully."