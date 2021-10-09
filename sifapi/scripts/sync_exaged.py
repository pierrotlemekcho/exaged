import logging
from datetime import datetime, timezone

from django.conf import settings
from planning import exact_api_client
from planning.models import LastSyncSuccess
from planning.synchroniser import Synchronizer

logger = logging.getLogger(__name__)


EXACT_SYNC_TYPE = "exact_online"


def run():
    exact_api_client.configure(config_file=settings.EXACT_ONLINE_CONFIG_FILE)
    api = exact_api_client.factory()
    now = datetime.now(timezone.utc)

    last_sync = LastSyncSuccess.objects.filter(sync_type=EXACT_SYNC_TYPE).first()
    if not last_sync:
        last_sync = LastSyncSuccess(sync_type=EXACT_SYNC_TYPE)

    last_sync_timestamp = last_sync.timestamp
    synchronizer = Synchronizer(
        api, settings.EXACT_ONLINE_DIVISION, last_sync_timestamp
    )
    logger.info(f"Start Sync modifed since {synchronizer.since_string}")
    logger.info("Start Sync Articles")
    counter = synchronizer.synchronize_articles()
    logger.info(f"{counter} articles maj")
    logger.info("Start Sync Gammes")
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

    last_sync.save()
    logger.info("Start Sync done")
