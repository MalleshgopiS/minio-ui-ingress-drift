#!/bin/bash
set -e

# --- Standard Header ---
/usr/bin/supervisord -c /etc/supervisor/supervisord.conf 2>/dev/null || true
sleep 5
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

until kubectl get nodes &>/dev/null; do
    sleep 2
done

# --- Custom Setup ---
kubectl create namespace minio --dry-run=client -o yaml | kubectl apply -f -

# Create the Minio Service (The target)
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: minio-console
  namespace: minio
spec:
  ports:
  - port: 9001
    targetPort: 9001
    protocol: TCP
    name: http
  selector:
    app: minio
EOF

# Ensure NO ingress exists initially (the "drift")
kubectl delete ingress minio-ui-ingress -n minio --ignore-not-found=true

echo "Setup complete. Minio console service is at port 9001, but Ingress is missing."