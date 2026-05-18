# Complyance: Intelligent E-Invoice Transcoder

Complyance is a production-grade, microservices-based engine designed to solve the complexity of international e-invoice interoperability. It enables seamless transcoding between global standards like **Peppol BIS 3.0 (UBL)**, **XRechnung (CII/UBL)**, **Factur-X**, and **PINT**, using a hybrid Deterministic + Machine Learning architecture.

## 🌟 Product Overview

- **Standard Compliance:** Dynamically maps fields to standard UBL and CII hierarchical paths.
- **Structural Intelligence:** Bidirectional restructuring of line items (Flat ↔ Nested assembly groups).
- **ML Supervisor:** XGBoost multi-output classifier detects 7 mandatory error types with high precision.
- **Auto-Correction:** Intelligent deterministic engine repairs tax mismatches, currency inconsistencies, and missing fields using real-time data.
- **Enterprise Ready:** Thread-safe API, PostgreSQL persistence via Prisma ORM, and a professional analytics dashboard.

---

## 🚀 Quick Start (Docker - Recommended)

Deploy the entire stack (Database, API, and UI) with a single command.

1.  **Launch Ecosystem:**
    ```bash
    docker-compose up --build -d
    ```
2.  **Initialize Database:**
    ```bash
    docker exec -it complyance_api prisma db push --schema=prisma/schema.prisma
    ```
3.  **Access Services:**
    - **Dashboard:** `http://localhost:80`
    - **API Documentation:** `http://localhost:3001/docs`

---

## 🛠️ Manual Setup (Local Development)

### 1. Database
Ensure you have a PostgreSQL instance running (e.g., Neon.tech or local).
Set your connection string in `services/api/.env`:
```env
DATABASE_URL="postgresql://user:pass@host:5432/db"
```

### 2. Backend API
```bash
cd services/api
python3 -m pip install -r requirements.txt
prisma generate --schema=prisma/schema.prisma
python3 main.py
```

### 3. Frontend Dashboard
```bash
cd services/frontend
npm install
npm run dev
```
The UI will be available at `http://localhost:5173`.

---

## 🏗️ Technical Architecture

- **Core Engine:** Pure Python implementation of international tax and syntax rules.
- **ML Layer:** Pre-trained XGBoost models for anomaly detection and validation.
- **Service Layer:** FastAPI for high-performance, asynchronous request handling.
- **Data Layer:** Prisma ORM for type-safe interaction with PostgreSQL.
- **UI Layer:** React with Tailwind CSS and Recharts for real-time monitoring.

## 🧩 Key Execution Flow
`Input Payload` ➔ `Parsing` ➔ `ML Feature Extraction` ➔ `XGBoost Prediction` ➔ `Deterministic Correction` ➔ `UBL/CII Syntax Mapping` ➔ `PostgreSQL Persistence`

---

**Developed for PS-4: E-Invoice Format Transcoder.**
