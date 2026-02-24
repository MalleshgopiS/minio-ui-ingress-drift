#!/usr/bin/env bash
set -e

echo "Discover ingress controller IP..."

INGRESS_IP=$(kubectl get ingress bleater -n bleater \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Ingress IP: $INGRESS_IP"

echo "Fix DNS..."

DNS_FILE="/etc/dnsmasq.d/devops.local.conf"

sudo sed -i "s|address=/.devops.local/.*|address=/.devops.local/${INGRESS_IP}|" $DNS_FILE || \
sed -i "s|address=/.devops.local/.*|address=/.devops.local/${INGRESS_IP}|" $DNS_FILE

# restart dnsmasq without sudo
killall dnsmasq || true
dnsmasq

echo "Fix ingress routing..."

kubectl get ingress bleater -n bleater -o json \
| jq '
.spec.tls[0].secretName="bleater-ui-tls"
| .spec.rules[0].http.paths |=
  map(
    if .path=="/"
    then .backend.service.name="bleater-minio"
    | .backend.service.port.number=9001
    else .
    end
  )
' \
| kubectl apply -f -

echo "Fix MinIO bucket policy..."

mc anonymous set download local/ui

echo "Done."