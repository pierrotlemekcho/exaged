from exactonline.api import ExactApi
from exactonline.exceptions import ObjectDoesNotExist
from exactonline.resource import GET, POST, PUT, DELETE
from exactonline.storage import IniStorage

""" Recuperer la liste des clients sur l'api EXACT
	crm/Accounts
	ID :  	Edm.Guid 
	Code :  Edm.String 
	Name : 	Edm.String
	IsSales : 	Edm.Boolean
	IsSupplier:  	Edm.Boolean
	
	mettre à jour la base POSTGRESQL sur le serveur prunelle """
								
	
# Create a function to get the api with your own storage backend.

def get_api():
    storage = IniStorage('config.ini')
    return ExactApi(storage=storage)
api = get_api()



contacts1 = api.relations.filter(select = 'ID,Code,Name,Status,IsSales,IsSupplier' )
print(contacts1)
for enr in contacts1 :
	print(enr['ID'],enr['Code'],enr['Name'],enr['Status'],enr['IsSales'],enr['IsSupplier'])

print(type(contacts1))
print(type(enr))


