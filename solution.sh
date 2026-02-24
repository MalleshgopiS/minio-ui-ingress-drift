#!/usr/bin/env bash
set -euo pipefail

echo "=== Fixing Bleater UI ==="

############################################
# 1. Discover ingress IP (RBAC SAFE)
############################################

INGRESS_IP=$(kubectl get ingress bleater -n bleater \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Ingress IP: $INGRESS_IP"

############################################
# 2. Fix dnsmasq wildcard
############################################

DNS_FILE="/etc/dnsmasq.d/devops.local.conf"

sed -i "s|address=/.devops.local/.*|address=/.devops.local/${INGRESS_IP}|" "$DNS_FILE"

echo "DNS fixed"

############################################
# 3. Fix ingress routing
############################################

kubectl get ingress bleater -n bleater -o json \
| jq '
.spec.tls[0].secretName="bleater-ui-tls"
| .spec.rules[0].http.paths |=
  map(
    if .path == "/"
    then
      .backend.service.name="bleater-minio"
      | .backend.service.port.number=9001
    else .
    end
  )
' \
| kubectl apply -f -

echo "Ingress fixed"

############################################
# 4. Fix MinIO bucket policy
############################################

mc anonymous set download local/ui

echo "Bucket policy fixed"

echo "✅ Repair complete"