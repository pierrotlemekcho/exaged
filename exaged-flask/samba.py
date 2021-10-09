from smb.SMBConnection import SMBConnection
import logging

log = logging.getLogger(__name__)

config = {}

def configure(*args, **kwargs):
    log.debug('Configuring Samba')
    config.update(kwargs)

def factory():
    connection = SMBConnection(
        config["user"],
        config["password"],
        "abcd",
        config["server_name"],
        use_ntlm_v2=True)
    connection.connect(config["server_ip"], int(config["port"]))
    return connection

