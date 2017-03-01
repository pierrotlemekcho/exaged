from exactonline.api import ExactApi
from exactonline.exceptions import ObjectDoesNotExist
from exactonline.resource import GET, POST, PUT, DELETE
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



print(' #################################')
#----------------  un deuxieme groupe ------------

contacts1 = api.relations.filter(select = 'ID,Name,Created,AddressLine1,AddressLine2,AddressLine3,Status,IsSales,IsSupplier' )
print(type(contacts1))
print(type(contacts1[0]))
print(contacts1)
for enr in contacts1 :
	print(enr['Name'],enr['Status'],enr['IsSales'],enr['IsSupplier'])

#----------------- un troisieme groupe -------------
contacts2 = api.restv1(GET('crm/Accounts?$top=2'))
print(type(contacts2)) 
print(contacts2)
#iontact3 = api.rest(GET('v1/%d/crm/Accounts' % selected_division))
#-------------------un quatrieme groupe
#contact3 = api.rest(GET('v1/%d/crm/Accounts' % selected_division))

#print(type(contacts3))

contacts3 = api.restv1(GET('manufacturing/ShopOrders?$top=2'))
print(type(contacts3)) 
print(contacts3)

#-------------------5eme groupe ESSAIS SUR expand qui marche
#devis = api.restv1(GET('crm/Quotations?$select=InvoiceAccountName,QuotationNumber,QuotationLines&$expand=QuotationLines'))
#print(type(devis))
#print(devis)

#print(len(devis))
#==================6 eme utile pour GED liste des devis 
devis = api.restv1(GET('crm/Quotations?$select=InvoiceAccountName,QuotationNumber,' +
	'Description,YourRef' +
	'&$orderby=QuotationNumber'))
for dev in devis :
	print(' N° de devis :{} ====> Client {} \
	==> your ref: {} ===> desc :{}'.format(dev['QuotationNumber'],dev['InvoiceAccountName'],\
	dev['YourRef'],dev['Description']))

print(len(devis))




