#!/bin/bash
set -e

echo "Injecting cascading drift..."

# Wrong DNS
echo "address=/.devops.local/10.10.10.10" > /etc/dnsmasq.d/devops.local.conf

# Wrong ingress backend
kubectl -n bleater patch ingress bleater --type=json -p='[
 {
   "op":"replace",
   "path":"/spec/rules/0/http/paths/0/backend/service/port/number",
   "value":9000
 }
]'