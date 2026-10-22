from redis import Redis

from app import celery
from app.europmc.europmc import run_spider
from app.pubmed.args_pubmed import pubmed_main_scarper
from config import Config

redis_client = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)


@celery.task(bind=True)
def async_start_scraping(self, data: dict):
    """
    Background task to start scraping based on selected site.
    """
    try:
        self.update_state(state="STARTED", meta={"message": "Scraping started"})

        site = data.get("site")
        data.pop("site", None)

        if site == "pubmed":
            print(site)
            pubmed_main_scarper(**data)
        elif site == "europmc":
            print(site)
            run_spider(**data)
        else:
            raise ValueError(f"Unsupported site: {site}")

        return {"status": "SUCCESS", "message": f"Scraping completed for {site}"}

    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise
