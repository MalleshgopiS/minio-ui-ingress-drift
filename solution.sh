#!/usr/bin/env bash
set -e

echo "Discover ingress IP..."

INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.spec.clusterIP}')

echo "Fixing dnsmasq..."

sudo sed -i "s|address=/.devops.local/.*|address=/.devops.local/${INGRESS_IP}|" \
  /etc/dnsmasq.d/devops.local.conf

sudo systemctl restart dnsmasq || true


echo "Fix ingress routing..."

kubectl get ingress bleater -n bleater -o json | \
jq '
.spec.rules[0].http.paths |= map(
  if .path == "/" then
    .backend.service.name="bleater-minio" |
    .backend.service.port.number=9001
  else .
  end
)
| .spec.tls[0].secretName="bleater-ui-tls"
' | kubectl apply -f -


echo "Fix MinIO bucket policy..."
mc anonymous set download local/ui || true

echo "All fixes applied."