from time import sleep
from exactonline.api import ExactApi
from exactonline.exceptions import ObjectDoesNotExist
from exactonline.storage import IniStorage
import webbrowser

class MyIniStorage(IniStorage):
    def get_response_url(self):
         "Configure your custom response URL."
         return self.get_base_url() + '/oauth/success/'


storage = MyIniStorage('config.ini')

api = ExactApi(storage=storage)

url = api.create_auth_request_url()

sleep(5)

webbrowser.open_new(url)

code = input('Enter value of the code query parameter: ')


api.request_token(code)

print("High five!! it worked")

























# vim: set ts=8 sw=4 sts=4 et ai tw=79:
