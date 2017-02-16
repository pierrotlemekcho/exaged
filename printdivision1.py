from exactonline.api import ExactApi
from exactonline.exceptions import ObjectDoesNotExist
from exactonline.storage import IniStorage

# Create a function to get the api with your own storage backend.
def get_api():
    storage = IniStorage('config.ini')
    return ExactApi(storage=storage)
api = get_api()

division_choices, current_division = api.get_divisions()

print(division_choices,'"***********"',current_division)

api.set_division(current_division)

contacts = api.relations.all()

print(type(contacts))
print(type(contacts[0]))
for enr in contacts :
	print(enr['Name'])
