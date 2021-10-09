from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging

log = logging.getLogger(__name__)

config = {}

def configure(*args, **kwargs):
    log.debug('Configuring database')
    config.update(kwargs)

def factory():
    engine = create_engine(config['url'])
    return sessionmaker(bind=engine)()
