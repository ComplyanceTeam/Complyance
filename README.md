# Complyance: Scalable E-Invoice Transcoder

A containerized, microservice-ready e-invoice mapping and validation engine.

## 🏗️ Architecture
- **`core/`**: Shared Python library containing the transcoding engine and pre-trained XGBoost models.
- **`services/api/`**: FastAPI backend providing real-time transcoding and history endpoints.
- **`services/frontend/`**: React dashboard for visualization and analytics.
- **`docker-compose.yml`**: Unified orchestration for local development and deployment.

## 🚀 Quick Start (Docker)

Ensure you have **Docker** and **Docker Compose** installed.

1.  **Clone and Start:**
    ```bash
    docker-compose up --build
    ```
2.  **Initialize Database (First time only):**
    ```bash
    docker exec -it complyance_api prisma db push --schema=prisma/schema.prisma
    ```
3.  **Access Services:**
    - **Dashboard:** `http://localhost:80`
    - **API Docs:** `http://localhost:3001/docs`

## 🛠️ Deployment
This structure is ready for cloud deployment:
- **API:** Deploy the `services/api/Dockerfile` to AWS App Runner, Cloud Run, or a Kubernetes cluster.
- **Frontend:** The `services/frontend/Dockerfile` builds a production-ready Nginx container for static hosting.
- **Database:** Use a managed service like AWS RDS or Google Cloud SQL.

## 🧩 Technology Stack
- **Engine:** Python, XGBoost, scikit-learn.
- **API:** FastAPI, Prisma ORM.
- **Frontend:** React, Tailwind CSS, Recharts.
- **DevOps:** Docker, Docker Compose.
