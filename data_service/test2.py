from db_util import MongoDB 

mongodb = MongoDB('123.57.250.189',27017,'dulishuo','Dulishuo123',True)
mongodb.get_database('dulishuo')
collection = mongodb.get_collection('product')
print(collection.find_one())
