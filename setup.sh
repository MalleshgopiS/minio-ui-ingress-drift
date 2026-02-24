#!/usr/bin/env bash
set -e

echo "Injecting cascading drift..."

########################################
# Break DNS wildcard
########################################
cat <<EOF > /etc/dnsmasq.d/devops.local.conf
address=/.devops.local/10.10.10.10
EOF

########################################
# Break ingress routing
########################################
kubectl patch ingress bleater -n bleater --type=json -p='[
  {"op":"replace","path":"/spec/rules/0/http/paths/0/backend/service/name","value":"old-minio"},
  {"op":"replace","path":"/spec/rules/0/http/paths/0/backend/service/port/number","value":9000}
]' || true

########################################
# Wrong TLS secret
########################################
kubectl patch ingress bleater -n bleater --type=json -p='[
  {"op":"replace","path":"/spec/tls/0/secretName","value":"old-secret"}
]' || true

########################################
# Make bucket private
########################################
mc anonymous set none local/ui || true

echo "Drift injected."