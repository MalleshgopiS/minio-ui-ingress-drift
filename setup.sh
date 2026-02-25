#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo "Setting up MinIO UI Ingress Drift Task"
echo "========================================"

NAMESPACE="bleater"

# --------------------------------------------------
# Namespace
# --------------------------------------------------
kubectl get ns ${NAMESPACE} >/dev/null 2>&1 || kubectl create ns ${NAMESPACE}
echo "Namespace ready: ${NAMESPACE}"

# --------------------------------------------------
# Dummy backend service (WRONG service)
# --------------------------------------------------
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

# --------------------------------------------------
# Generate TLS certs (NEBULA SAFE)
# --------------------------------------------------
TMP_DIR=$(mktemp -d)

openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout ${TMP_DIR}/tls.key \
  -out ${TMP_DIR}/tls.crt \
  -subj "/CN=minio.devops.local"

kubectl delete secret wrong-secret -n ${NAMESPACE} --ignore-not-found

kubectl create secret tls wrong-secret \
  --cert=${TMP_DIR}/tls.crt \
  --key=${TMP_DIR}/tls.key \
  -n ${NAMESPACE}

echo "Dummy TLS secret created"

# --------------------------------------------------
# Create DRIFTED ingress
# --------------------------------------------------
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

# --------------------------------------------------
# Save ORIGINAL UID (ANTI-CHEAT)
# --------------------------------------------------
UID=$(kubectl get ingress bleater-ui -n ${NAMESPACE} -o jsonpath='{.metadata.uid}')

echo "${UID}" > /tmp/bleater-ui-original-uid

echo "Original UID stored"

echo "========================================"
echo "Setup complete"
echo "========================================"