#!/bin/bash
set -e

NS=bleater
ING=bleater

echo "Discover ingress IP..."

ING_IP=$(kubectl get ingress $ING -n $NS \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Ingress IP = $ING_IP"

echo "Fix DNS mapping..."

# Apex containers allow writing hosts without sudo
echo "$ING_IP bleater.devops.local" >> /etc/hosts


echo "Fix ingress backend..."

kubectl get ingress $ING -n $NS -o json | \
jq '
.spec.rules[0].http.paths[0].backend.service.name="bleater-minio" |
.spec.rules[0].http.paths[0].backend.service.port.number=9001 |
.spec.tls[0].secretName="bleater-ui-tls"
' | kubectl apply -f -

echo "Fix MinIO bucket policy..."

mc anonymous set download local/ui

echo "✅ Drift fixed"