# Kubernetes manifests (placeholder)

Deploy order:

1. `namespace.yaml`
2. `secrets/` — from vault; never commit real values
3. `configmap.yaml` — non-secret env
4. `postgres/`, `redis/`, `elasticsearch/` — or use managed services
5. `backend-deployment.yaml`, `worker-deployment.yaml`, `frontend-deployment.yaml`
6. `ingress.yaml` — TLS termination

Use Helm chart wrapping `docker-compose` services for parity.
