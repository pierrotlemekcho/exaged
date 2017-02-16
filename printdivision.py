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
contacts = api.relations.filter(select = 'ID,Name,Created,AddressLine1,AddressLine2,AddressLine3,Status,IsSales,IsSupplier' )

print(type(contacts))
print(type(contacts[0]))
print(contacts)
for enr in contacts :
	print(enr['Name'],enr['Status'],enr['IsSales'],enr['IsSupplier'])
