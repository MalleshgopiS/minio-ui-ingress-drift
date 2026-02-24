#!/usr/bin/env bash
set -e

echo "Injecting cascading drift..."

sudo mkdir -p /etc/dnsmasq.d

cat <<EOF | sudo tee /etc/dnsmasq.d/devops.local.conf
address=/.devops.local/10.10.10.10
EOF

sudo systemctl restart dnsmasq || true

kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: bleater-minio
  namespace: bleater
spec:
  selector:
    app: minio
  ports:
  - name: console
    port: 9001
    targetPort: 9001
EOF

kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bleater
  namespace: bleater
spec:
  tls:
  - hosts:
    - bleater.devops.local
    secretName: old-tls-secret
  rules:
  - host: bleater.devops.local
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: old-minio
            port:
              number: 9000
EOF

sleep 5

mc alias set local http://bleater-minio:9000 minio minio123 || true
mc anonymous set none local/ui || true