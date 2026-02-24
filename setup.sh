#!/bin/bash
set -e

# --- Standard Header ---
echo "Ensuring supervisord is running..."
/usr/bin/supervisord -c /etc/supervisor/supervisord.conf 2>/dev/null || true
sleep 5
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

until kubectl get nodes &>/dev/null; do
    sleep 2
done

# --- Task Specific Setup ---
kubectl create namespace minio --dry-run=client -o yaml | kubectl apply -f -

# GRANT PERMISSIONS TO UBUNTU USER (Fixes the Forbidden error)
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: minio-ingress-admin
  namespace: minio
rules:
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: minio-ingress-admin-binding
  namespace: minio
subjects:
- kind: User
  name: system:serviceaccount:default:ubuntu-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: minio-ingress-admin
  apiGroup: rbac.authorization.k8s.io
EOF

# Create the Service
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

# Ensure the drift
kubectl delete ingress minio-ui-ingress -n minio --ignore-not-found=true

echo "Setup complete. RBAC permissions granted and service created."