#!/usr/bin/env bash
set -e

echo "Discover ingress IP..."

INGRESS_IP=$(kubectl get svc -n ingress-nginx \
  -o jsonpath='{.items[0].spec.clusterIP}')

echo "Fix DNS..."

sudo sed -i "s|address=/.devops.local/.*|address=/.devops.local/${INGRESS_IP}|" \
  /etc/dnsmasq.d/devops.local.conf

sudo systemctl restart dnsmasq || true


echo "Fix ingress..."

kubectl get ingress bleater -n bleater -o json | jq '
.spec.rules[0].http.paths |= map(
  if .path == "/" then
    .backend.service.name="bleater-minio" |
    .backend.service.port.number=9001
  else .
  end
)
| .spec.tls[0].secretName="bleater-ui-tls"
' | kubectl apply -f -


echo "Fix MinIO policy..."
mc anonymous set download local/ui || true

echo "Done."