#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo "Setting up MinIO UI Ingress Drift Task"
echo "========================================"

NAMESPACE="bleater"
INGRESS_NAME="bleater-ui"

# --------------------------------------------------
# Ensure namespace exists
# --------------------------------------------------

kubectl get ns ${NAMESPACE} >/dev/null 2>&1 || \
kubectl create namespace ${NAMESPACE}

echo "Namespace ready: ${NAMESPACE}"

# --------------------------------------------------
# Create placeholder backend service
# (needed so ingress is valid)
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
# Create TLS secret placeholder
# --------------------------------------------------

kubectl create secret tls wrong-secret \
  --cert=/etc/ssl/certs/ssl-cert-snakeoil.pem \
  --key=/etc/ssl/private/ssl-cert-snakeoil.key \
  -n ${NAMESPACE} \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Dummy TLS secret created"

# --------------------------------------------------
# Create DRIFTED ingress (INTENTIONALLY WRONG)
# --------------------------------------------------

kubectl apply -n ${NAMESPACE} -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ${INGRESS_NAME}
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
# Wait for ingress availability
# --------------------------------------------------

echo "Waiting for ingress readiness..."

for i in {1..20}; do
  if kubectl get ingress ${INGRESS_NAME} -n ${NAMESPACE} >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

# --------------------------------------------------
# Capture ORIGINAL UID (ANTI-CHEAT BASELINE)
# --------------------------------------------------

kubectl get ingress ${INGRESS_NAME} -n ${NAMESPACE} \
  -o jsonpath='{.metadata.uid}' \
  > /tmp/bleater-ui-original-uid

echo "Original ingress UID saved:"
cat /tmp/bleater-ui-original-uid

echo "========================================"
echo "Setup complete — drift ready for fixing"
echo "========================================"