#!/usr/bin/env bash
set -e

echo "Discover ingress controller..."

INGRESS_IP=$(kubectl get svc -n ingress-nginx \
  -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.clusterIP}{"\n"}{end}' \
  | grep ingress | awk '{print $2}' | head -n1)

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


echo "Fix bucket..."
mc anonymous set download local/ui

echo "Done."