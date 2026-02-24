#!/usr/bin/env bash
set -e

echo "Fixing DNS..."
INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.spec.clusterIP}')

sudo sed -i "s|10.10.10.10|$INGRESS_IP|" \
  /etc/dnsmasq.d/devops.local.conf

sudo systemctl restart dnsmasq || true


echo "Fix ingress backend..."
kubectl patch ingress bleater -n bleater --type=json -p='[
 {"op":"replace","path":"/spec/rules/0/http/paths/1/backend/service/name","value":"bleater-minio"},
 {"op":"replace","path":"/spec/rules/0/http/paths/1/backend/service/port/number","value":9001},
 {"op":"replace","path":"/spec/tls/0/secretName","value":"bleater-ui-tls"}
]'


echo "Fix MinIO policy..."
mc anonymous set download local/ui

echo "Done."