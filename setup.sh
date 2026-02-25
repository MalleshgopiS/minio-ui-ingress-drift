#!/bin/bash
set -e

###############################################################################
# TASK INITIALIZATION SCRIPT
#
# PURPOSE
# -------
# This script prepares the Kubernetes environment for the
# "minio-ui-ingress-drift" task.
#
# It intentionally creates a MISCONFIGURED ("drifted") ingress resource.
#
# INITIAL DRIFTED STATE
# ---------------------
# Resource:
#   ingress: bleater-ui
#   namespace: bleater
#
# Incorrect values created intentionally:
#
#   Backend Service Name : wrong-service
#   Backend Service Port : 80
#   TLS Secret           : wrong-secret
#
# Correct values expected AFTER agent fixes:
#
#   Backend Service Name : bleater-minio
#   Backend Service Port : 9001
#   TLS Secret           : bleater-minio-tls
#   Host                 : minio.devops.local (UNCHANGED)
#
# TASK REQUIREMENT
# ----------------
# Agent must MODIFY the existing ingress resource.
# Agent must NOT delete or recreate resources.
#
###############################################################################

echo "Creating namespace..."
kubectl create namespace bleater --dry-run=client -o yaml | kubectl apply -f -

echo "Creating drifted ingress..."

cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bleater-ui
  namespace: bleater
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

echo "Drifted ingress created successfully."