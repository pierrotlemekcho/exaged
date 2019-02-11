from exaged.synchroniser import Synchronizer
from exaged.model.tier import Tier
from exaged.model.tier_client import TierClient
from exaged.model.tier_supplier import TierSupplier
from exaged.model.devis import Devis
from exaged.model.commande import Commande
from exaged import (
    exact_api_client,
    database
)

import configparser
import logging
import logging.config

EXACT_DIVISION = 17923
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
db.query(TierClient).delete()
db.query(TierSupplier).delete()

synchronizer = Synchronizer(db, api, EXACT_DIVISION)

logger.info('Start Sync Tiers')
counter = synchronizer.synchonize_tiers()
logger.info(f'{counter} tiers ajoutés')
logger.info('Start Sync Devis')
counter = synchronizer.synchronize_devis()
logger.info(f'{counter} devis ajoutés')
logger.info('Start Sync Commandes')
counter = synchronizer.synchronize_commandes()
logger.info(f'{counter} commandes ajoutés')

db.commit()
logger.info('Start Sync done')
