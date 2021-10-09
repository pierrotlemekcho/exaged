from exactonline.api import ExactApi
from exactonline.storage import IniStorage

config = {}

def configure(*args, **kwargs):
    config.update(kwargs)

class MyIniStorage(IniStorage):
    def get_response_url(self):
        "Configure your custom response URL."
        return self.get_base_url()

    def get_iteration_limit(self):
        return 200


def factory():
    return ExactApi(MyIniStorage(config['config_file']))
