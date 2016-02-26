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
    global PRODUCT_RECOMMEND
    global NODEID_TO_TEXT
    PRODUCT_RECOMMEND = {}
    mongodb = MongoDB('123.57.250.189',27017,'dulishuo','Dulishuo123',True)
    mongodb.get_database('dulishuo')
    product_collection = mongodb.get_collection('product')
    producttag_collection = mongodb.get_collection('producttag')
    NODEID_TO_TEXT = {1:'提升GPA',3:'提升托福成绩',4:'提升雅思成绩',2:'提升GRE成绩',103:'提升GMAT成绩',11:'竞赛',6:'实习',12:'证书',102:'奖学金',14:'活动',104:'推荐信'}
    tag_list = ['提升GPA','提升托福成绩','提升雅思成绩','提升GRE成绩','提升GMAT成绩','竞赛','实习','证书','奖学金','活动','推荐信']
    tag_dict = get_tag_dict(tag_list,producttag_collection)
    for tag_name in tag_dict:
        list = []
        for record in product_collection.find({'tag':{'$regex':tag_dict[tag_name]}},{'id':1,'title':1,'title_pic':1,'tag':1}):
            product = {}
            product['product_id'] = record['id']
            product['title'] = record['title']
            product['picture'] = record['title_pic']
            list.append(product)
        PRODUCT_RECOMMEND[tag_name] = list

def get_product_by_node_id(node_id):
    print(PRODUCT_RECOMMEND[NODEID_TO_TEXT[node_id]])

init()
get_product_by_node_id(1)







