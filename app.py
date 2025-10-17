import os
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager
from redis.exceptions import ConnectionError as RedisConnectionError
from redis import Redis

import uvicorn

import logging
import sys
logger = logging.getLogger()




###################################################################
#   Configuration des METRIQUES: DEBUT
###################################################################

from prometheus_client import generate_latest   # Pour sérioalizer les métriques au format openmetrics
from opentelemetry import metrics


from fastapi.responses import PlainTextResponse


# Obtenir un Meter pour créer des instruments
meter = metrics.get_meter(__name__)

# Ici, nous créons un instrument pour compter les ping
ping_request_counter = meter.create_counter(
    "ping_count",
    description="Total number of PING Request",
    unit="1"
)
###################################################################
#   METRIQUES: FIN
###################################################################

app = FastAPI()

REDIS_HOST = "redis"
REDIS_PORT = 6379

# Initialisation du client Redis (sera créé au démarrage de l'application)
redis_client: Redis = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire d'événements de cycle de vie (lifespan) pour l'application FastAPI.
    Se connecte à Redis au démarrage et se déconnecte à l'arrêt.
    """
    global redis_client
    try:
        redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT)
        redis_client.ping()
        logger.info("Connexion à Redis établie avec succès !")
        # Stocker le client Redis dans l'état de l'application pour un accès facile
        app.state.redis = redis_client
    except RedisConnectionError as e:
        logger.error(f"Erreur de connexion à Redis au démarrage : {e}")
        # En production, vous pourriez vouloir lever une exception ou arrêter l'application
        # pour éviter qu'elle ne démarre sans une connexion essentielle.
        # Pour cet exemple, nous continuons mais les routes échoueront.
        app.state.redis = None # S'assurer que l'état est clair en cas d'échec
    except Exception as e:
        logger.error(f"Une erreur inattendue est survenue lors de la connexion à Redis : {e}")
        app.state.redis = None

    # Le code avant le 'yield' s'exécute au démarrage de l'application
    yield
    # Le code après le 'yield' s'exécute à l'arrêt de l'application
    if app.state.redis:
        app.state.redis.close()
        logger.info("Connexion redis fermée")

# Initialisation de l'application FastAPI avec le gestionnaire de lifespan
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    logger.info("GET /")
    return {"message": "Hello World 2!"}


@app.get("/echo/{item_id}")
async def echo_item(item_id: str):
    if item_id == "500":
        logger.error("Error 500 forcée")
        raise HTTPException(status_code=500, detail="Error 500")
    if item_id == "400":
        logger.error("Error 400 forcée")
        raise HTTPException(status_code=404, detail="Item not found")
    return {"echo": item_id}



# Exposer le endpoints
@app.get("/metrics", response_class=PlainTextResponse)
async def metrics_endpoint():
    """
    Cet endpoint sert les métriques au format Prometheus.
    OpenTelemetry s'occupe de la sérialisation des métriques enregistrées.
    """
    return generate_latest().decode("utf-8")


@app.get("/ping")
async def ping_redis():
    logger.info("GET /ping redis")
    
    ping_request_counter.add(1, {"endpoint": "/ping", "method": "GET"})

    """Vérifie la connexion à Redis."""
    redis_conn: Redis = app.state.redis
    if not redis_conn:
        return {"status": "disconnected", "message": "Non connecté à Redis. Veuillez vérifier la configuration et le statut de Redis."}
    try:
        redis_conn.ping()
        logger.info("Pong")
        return {"status": "connected", "message": "Pong!"}
    except RedisConnectionError as e:
        logger.error(f"Erreur de ping Redis : {e}. Le serveur Redis est peut-être inaccessible.")
        return {"status": "error", "message": f"Erreur de ping Redis : {e}. Le serveur Redis est peut-être inaccessible."}
    except Exception as e:
        logger.error(f"Erreur inattendue lors du ping : {e}")
        return {"status": "error", "message": f"Erreur inattendue lors du ping : {e}"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    uvicorn.run(app, host="0.0.0.0", port=8000)
