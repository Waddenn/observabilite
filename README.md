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
