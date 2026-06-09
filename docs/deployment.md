# SentinelX AI-SOC — Deployment Guide

This guide describes how to run SentinelX locally for development and how to deploy the platform in a production cloud environment.

---

## 1. Local Development Deployment (Docker Compose)

The entire SentinelX stack (microservices + database + cache + message stream + SIEM + monitoring) can be run locally using the provided `docker-compose.yml` file.

### Prerequisites
* Docker & Docker Compose installed.
* At least 8GB of RAM allocated to Docker.

### Running the Stack
Use the root `Makefile` helper commands:
```bash
# Start all infrastructure and microservices
make dev

# Check logs of a specific service
docker-compose logs -f auth
```

Exposed Services:
* **Frontend Dashboard**: `http://localhost:3000`
* **API Gateway**: `http://localhost:8080`
* **Kafka UI (Topic Monitor)**: `http://localhost:8090`
* **Grafana Dashboards**: `http://localhost:3001`
* **Prometheus**: `http://localhost:9090`

---

## 2. Production Deployment (AWS + Kubernetes)

For production scale, SentinelX uses **Terraform** for cloud infrastructure and **Kubernetes** for service orchestration.

### Phase 1: Infrastructure Provisioning (Terraform)
1. Initialize and apply the root Terraform configuration:
   ```bash
   cd infra/terraform
   terraform init
   terraform apply -var="environment=prod"
   ```
2. Terraform will provision the following cloud services:
   * **VPC**: 3 Public, 3 Private Subnets, NAT Gateways.
   * **EKS Cluster**: Managed Kubernetes cluster for services.
   * **RDS MySQL**: Master/Replica database for auth/alert data.
   * **ElastiCache Redis**: High-performance caching and rate-limiting store.
   * **AWS OpenSearch**: SIEM logging cluster.
   * **AWS MSK (Kafka)**: Event streaming bus.

### Phase 2: Deploy to Kubernetes
1. Connect kubectl to the EKS cluster:
   ```bash
   aws eks update-kubeconfig --name sentinelx-prod --region us-east-1
   ```
2. Apply Kubernetes Secrets & ConfigMaps (DB Credentials, API keys):
   ```bash
   kubectl apply -f infra/k8s/secrets/
   ```
3. Deploy all microservices and the Next.js frontend:
   ```bash
   kubectl apply -f infra/k8s/services/auth/deployment.yml
   kubectl apply -f infra/k8s/sentinelx-services.yml
   ```
4. Verify the deployments:
   ```bash
   kubectl get pods -n sentinelx
   ```
