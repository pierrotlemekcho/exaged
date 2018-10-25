from exaged.synchroniser import Synchronizer
from exaged.model.tier import Tier
from exaged.model.devis import Devis
from exaged.model.commande import Commande
from exaged import (
    exact_api_client,
    database
)

import configparser
import logging
import logging.config

logging.config.fileConfig('exaged.ini')
logger = logging.getLogger('exaged')


config = configparser.ConfigParser()
config.read('exaged.ini')

exact_api_client.configure(config_file=config['exaged']['exact_api_config_file'])
database.configure(url=config['exaged']['database_url'])
logger.info('Configuration done')

api = exact_api_client.factory()
db = database.factory()

logger.info('Delete commandes')
db.query(Commande).delete()
logger.info('Delete devis')
db.query(Devis).delete()
logger.info('Delete tiers')
db.query(Tier).delete()

synchronizer = Synchronizer(db, api, 17923)

logger.info('Start Sync Tiers')
synchronizer.synchonize_tiers()
logger.info('Start Sync Devis')
synchronizer.synchronize_devis()
logger.info('Start Sync Commandes')
synchronizer.synchronize_commandes()

db.commit()
logger.info('Start Sync done')
