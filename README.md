# Observabilité – FastAPI + OpenTelemetry + Alloy + Grafana Stack

Ce projet met en place une **stack complète d’observabilité** autour d’une application **FastAPI instrumentée OpenTelemetry**, déployée via **Docker Compose**.  
Elle expose des métriques Prometheus, des traces Tempo et des logs Loki collectés par **Grafana Alloy**.

---

## Stack déployée

| Service | Rôle | Port |
|----------|------|------|
| **app** | Application FastAPI instrumentée OTEL (metrics/logs/traces) | 8000 |
| **redis** | Cache / backend de test pour `/ping` | 6379 |
| **alloy** | Collecteur OpenTelemetry → Loki / Tempo / Mimir | 4318 / 12345 |
| **loki** | Stockage et exploration des logs | 3100 |
| **tempo** | Traces distribuées | 3200 |
| **mimir** | Métriques Prometheus centralisées | 9009 |
| **grafana** | Interface d’observabilité unique | 3000 |

---

## Déploiement

```bash
# Build et lancement complet
docker compose build app
docker compose up -d
````

### Vérification

```bash
docker compose ps        # Tous les conteneurs doivent être en "running"
docker compose logs app  # Logs de l’application
```

## Application FastAPI

### Endpoints principaux

| Endpoint   | Description                     |
| ---------- | ------------------------------- |
| `/`        | Retourne un message de test     |
| `/ping`    | Vérifie la connexion Redis      |
| `/metrics` | Expose les métriques Prometheus |

Exemples :

```bash
curl -s http://localhost:8000/ping | jq .
```

<img width="336" height="89" alt="screenshot-2025-10-17_14-53-37" src="https://github.com/user-attachments/assets/e8c0c7bd-0bff-4619-8a2f-a0dc7ee80bd7" />


```bash
curl -s http://localhost:8000/metrics | head -n 30
```

<img width="688" height="478" alt="screenshot-2025-10-17_14-53-22" src="https://github.com/user-attachments/assets/c53c5a49-2094-4f39-9852-ff2e438d65b7" />


---

## Observabilité dans Grafana

Accède à Grafana sur [http://localhost:3000](http://localhost:3000)

* Login : `admin` / `admin`
* Ajoute les datasources :

  * **Loki** → `http://loki:3100`
  * **Tempo** → `http://tempo:3200`
  * **Prometheus (Mimir)** → `http://mimir:9009/prometheus`

## Structure du projet

```
.
├── app.py
├── Dockerfile
├── requirements.txt
├── docker-compose.yml
├── config/
│   ├── loki/config.yaml
│   ├── tempo/config.yaml
│   └── mimir/config.yaml
├── config.alloy
└── captures/
    ├── lazydocker.png
    ├── ping.png
    └── metrics.png
```
<img width="1536" height="1022" alt="image" src="https://github.com/user-attachments/assets/bd96b7b3-abaf-4b5d-908d-df9334934e2e" />



