from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import aiomysql
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Hybride MongoDB/MySQL")

MONGO_URL = os.getenv("MONGO_URL", "mongodb://admin:password@db_mongo:27017")
mongo_client = AsyncIOMotorClient(MONGO_URL)
mongo_db = mongo_client.blog_db

MYSQL_HOST = os.getenv("MYSQL_HOST", "db_mysql")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD", "rootpassword")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "app_db")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))

mysql_pool = None


async def get_mysql_pool():
    """Obtenir ou créer le pool de connexions MySQL"""
    global mysql_pool
    if mysql_pool is None:
        try:
            mysql_pool = await aiomysql.create_pool(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                db=MYSQL_DATABASE,
                autocommit=True
            )
            logger.info("Pool MySQL créé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la création du pool MySQL: {e}")
            raise
    return mysql_pool


@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'application"""
    logger.info("Démarrage de l'API...")
    try:
        await mongo_client.admin.command('ping')
        logger.info("Connexion MongoDB établie")

        await get_mysql_pool()
        logger.info("Connexion MySQL établie")

    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt de l'application"""
    logger.info("Arrêt de l'API...")
    if mysql_pool:
        mysql_pool.close()
        await mysql_pool.wait_closed()
    mongo_client.close()


@app.get("/")
async def root():
    """Route de bienvenue"""
    return {
        "message": "API Hybride MongoDB/MySQL",
        "endpoints": {
            "posts": "/posts (MongoDB)",
            "users": "/users (MySQL)",
            "health": "/health"
        }
    }


@app.get("/posts")
async def get_posts():
    """Récupérer tous les articles depuis MongoDB"""
    try:
        cursor = mongo_db.posts.find({}, {"_id": 0})
        posts = await cursor.to_list(length=100)
        logger.info(f"{len(posts)} posts récupérés depuis MongoDB")
        return {
            "source": "MongoDB",
            "count": len(posts),
            "data": posts
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des posts: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur MongoDB: {str(e)}")


@app.get("/users")
async def get_users():
    """Récupérer tous les utilisateurs depuis MySQL"""
    try:
        pool = await get_mysql_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM utilisateurs")
                users = await cursor.fetchall()
                logger.info(f"{len(users)} utilisateurs récupérés depuis MySQL")
                return {
                    "source": "MySQL",
                    "count": len(users),
                    "data": users
                }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur MySQL: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Healthcheck métier : vérifie que les deux bases sont accessibles
    et contiennent les données attendues
    """
    status = {
        "mongodb": {"status": "unhealthy", "posts_count": 0, "expected": 5},
        "mysql": {"status": "unhealthy", "users_count": 0, "expected": 4},
        "overall": "unhealthy"
    }

    try:
        await mongo_client.admin.command('ping')
        posts_count = await mongo_db.posts.count_documents({})
        status["mongodb"]["posts_count"] = posts_count
        if posts_count == 5:
            status["mongodb"]["status"] = "healthy"
        else:
            status["mongodb"]["status"] = f"unhealthy: expected 5 posts, got {posts_count}"
    except Exception as e:
        status["mongodb"]["error"] = str(e)
        logger.error(f"MongoDB healthcheck failed: {e}")

    try:
        pool = await get_mysql_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT COUNT(*) as count FROM utilisateurs")
                result = await cursor.fetchone()
                users_count = result[0] if result else 0
                status["mysql"]["users_count"] = users_count
                if users_count == 4:
                    status["mysql"]["status"] = "healthy"
                else:
                    status["mysql"]["status"] = f"unhealthy: expected 4 users, got {users_count}"
    except Exception as e:
        status["mysql"]["error"] = str(e)
        logger.error(f"MySQL healthcheck failed: {e}")

    # Statut global
    if status["mongodb"]["status"] == "healthy" and status["mysql"]["status"] == "healthy":
        status["overall"] = "healthy"
        logger.info("Healthcheck: OK")
        return status
    else:
        logger.warning(f"Healthcheck: FAILED - {status}")
        raise HTTPException(status_code=503, detail=status)
