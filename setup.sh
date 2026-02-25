#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo "Setting up MinIO UI Ingress Drift Task"
echo "========================================"

NAMESPACE="bleater"

# ------------------------------------------------
# Create namespace
# ------------------------------------------------
kubectl get namespace ${NAMESPACE} >/dev/null 2>&1 || \
kubectl create namespace ${NAMESPACE}

echo "Namespace ready: ${NAMESPACE}"

# ------------------------------------------------
# Create WRONG backend service (drift)
# ------------------------------------------------
kubectl apply -n ${NAMESPACE} -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: wrong-service
spec:
  selector:
    app: dummy
  ports:
    - port: 80
      targetPort: 80
EOF

echo "Dummy service created"

# ------------------------------------------------
# Create WRONG TLS secret (drift)
# (generate self-signed cert dynamically)
# ------------------------------------------------
TMP_DIR=$(mktemp -d)

openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout ${TMP_DIR}/tls.key \
  -out ${TMP_DIR}/tls.crt \
  -subj "/CN=minio.devops.local"

kubectl create secret tls wrong-secret \
  --cert=${TMP_DIR}/tls.crt \
  --key=${TMP_DIR}/tls.key \
  -n ${NAMESPACE} \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Dummy TLS secret created"

# ------------------------------------------------
# Create DRIFTED ingress
# ------------------------------------------------
kubectl apply -n ${NAMESPACE} -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bleater-ui
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
EOF

echo "Drifted ingress created"

# ------------------------------------------------
# Wait until ingress exists
# ------------------------------------------------
echo "Waiting for ingress readiness..."

for i in {1..30}; do
  if kubectl get ingress bleater-ui -n ${NAMESPACE} >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

# ------------------------------------------------
# Capture ORIGINAL UID (ANTI-CHEAT)
# IMPORTANT: DO NOT USE VARIABLE NAME UID
# ------------------------------------------------
INGRESS_UID=$(kubectl get ingress bleater-ui \
  -n ${NAMESPACE} \
  -o jsonpath='{.metadata.uid}')

echo "${INGRESS_UID}" > /tmp/bleater-ui-original-uid

echo "Original ingress UID saved:"
cat /tmp/bleater-ui-original-uid

# ------------------------------------------------
# Cleanup temp cert files
# ------------------------------------------------
rm -rf ${TMP_DIR}

echo "========================================"
echo "Setup completed successfully"
echo "========================================"