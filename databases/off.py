import pymongo
from entities.offproduct import OffProduct 

class OpenFoodFacts():
    def __init__(self):
        client = pymongo.MongoClient("localhost", 27017)
        self.db_product = client.off.products
        self.fields = [ 'product_name', 'nutriments', 'countries']
        
    def get_product(self, product_name):
        res = self.db_product.find_one(projection=self.fields, filter={"product_name": product_name, "countries": 'United Kingdom'})
        pdt = OffProduct(name=res['product_name'], carb = res['nutriments']['carbohydrates_100g'])
        return pdt 