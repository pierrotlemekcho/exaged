import configparser
import logging
import logging.config
from datetime import datetime, timezone

from exaged import database, exact_api_client
from exaged.model.last_sync_success import LastSyncSuccess
from exaged.synchroniser import Synchronizer

EXACT_DIVISION = 17923
EXACT_SYNC_TYPE = "exact_online"

logging.config.fileConfig("exaged.ini")
logger = logging.getLogger("exaged")


config = configparser.ConfigParser()
config.read("exaged.ini")

exact_api_client.configure(config_file=config["exaged"]["exact_api_config_file"])
database.configure(url=config["exaged"]["database_url"])
logger.info("Configuration done")

api = exact_api_client.factory()
db = database.factory()


now = datetime.now(timezone.utc)
last_sync = db.query(LastSyncSuccess).filter_by(sync_type=EXACT_SYNC_TYPE).first()

if not last_sync:
    last_sync = LastSyncSuccess(sync_type=EXACT_SYNC_TYPE)

last_sync_timestamp = last_sync.timestamp
synchronizer = Synchronizer(db, api, EXACT_DIVISION, last_sync_timestamp)

logger.info(f"Start Sync modifed since {synchronizer.since_string}")

logger.info("Start Sync Articles")
counter = synchronizer.synchronize_articles()
logger.info(f"{counter} articles maj")
logger.info("Start Sync Articles")
counter = synchronizer.synchronize_gammes()
logger.info(f"{counter} gammes maj")
logger.info("Start Sync Tiers")
counter = synchronizer.synchronize_tiers()
logger.info(f"{counter} tiers maj")
logger.info("Start Sync Devis")
counter = synchronizer.synchronize_devis()
logger.info(f"{counter} devis maj")
logger.info("Start Sync Commandes")
counter = synchronizer.synchronize_commandes()
logger.info(f"{counter} commandes maj")

# Save last success sync for next time
last_sync.timestamp = now
db.add(last_sync)


db.commit()
logger.info("Start Sync done")
