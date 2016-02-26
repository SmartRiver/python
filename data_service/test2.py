from db_util import MongoDB 
import json

def get_tag_dict(tag_list, collection):
    tag_dict = {}
    for tag_name in tag_list:
        result = collection.find_one({'name':tag_name},{'id':1})
        if isinstance(result,dict):
            tag_dict[tag_name] = '%d'%result['id']
    return tag_dict
    
def init():
    result = {}
    mongodb = MongoDB('123.57.250.189',27017,'dulishuo','Dulishuo123',True)
    mongodb.get_database('dulishuo')
    product_collection = mongodb.get_collection('product')
    producttag_collection = mongodb.get_collection('producttag')
    tag_list = ['提升GPA','提升托福成绩','提升雅思成绩','提升GRE成绩','提升GMAT成绩','竞赛','实习','证书','奖学金','活动','推荐信']
    tag_dict = get_tag_dict(tag_list,producttag_collection)
    for tag_name in tag_dict:
        list = []
        for result in product_collection.find({'tag':{'$regex':tag_dict[tag_name]}},{'id':1,'title':1,'title_pic':1,'tag':1}):
            product = {}
            product['product_id'] = result['id']
            product['title'] = result['title']
            product['picture'] = result['title_pic']
            list.append(product)
        result[tag_name] = list
    print(result)    
init()







