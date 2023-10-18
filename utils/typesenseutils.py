from typesense import Client
import pymongo
import time

mongo_connection_string = "mongodb://root:toor@192.168.1.40:27017/"

client = Client({
    'nodes': [{
        'host': 'localhost',
        'port': '8108',
        'protocol': 'http',
    }],
    'api_key': 'test',
    'connection_timeout_seconds': 2
})

product_schema = {
    'name': 'products',
    'fields': [
        {'name': 'id', 'type': 'string'},
        {'name': 'name', 'type': 'string'},
        {'name': 'countries', 'type': 'string[]', 'facet': True},
        {'name': 'carbohydrates', 'type': 'float', "optional": True},
    ]
}

def createCollection() -> None:
    print("Création de la collection dans TypeSense...")
    client.collections.create(product_schema)
    print("Collection créée dans TypeSense.")

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def reportProgress(iteration, total):
    printProgressBar(iteration, total, prefix="Import", length=50, suffix="Complete", printEnd="\r\n");


def createMongoClient():
    return pymongo.MongoClient(mongo_connection_string);

def safeCreate(mongoProduct: dict) -> None:
    name = mongoProduct.get('product_name')
    res = {}
    if (name != "" and name is not None):
        res['id'] = mongoProduct.get('code')
        res['name'] = name
        res['countries'] = str(mongoProduct.get('countries')).split(',')
        carb = mongoProduct['nutriments'].get('carbohydrates_100g')
        if carb is not None:
            res['carbohydrates'] = carb
        return res
    else:
        return None

def importToTypeSense():
    mongoClient = createMongoClient()
    db_products = mongoClient.off.products
    filter = {'code':{'$ne':'null'}}
    nb_products_to_import = db_products.count_documents(filter=filter)
    res = input("Voulez-vous importer " + str(nb_products_to_import) + " produits dans TypeSense ? (yN) ")

    max_batch_size = 20_000

    ts_prd_docs = client.collections['products'].documents

    if (res == "y"):
        projection = {'code': 1, 'product_name': 2, 'countries': 3, 'nutriments.carbohydrates_100g': 4}
        nb_products_imported = 0
        previous_code = None
        reportProgress(0, nb_products_to_import)
        while nb_products_imported < nb_products_to_import:
            batch_size = min(max_batch_size, nb_products_to_import - nb_products_imported)
            products = db_products.find(filter=filter, limit=batch_size, projection=projection, sort=[('_id', pymongo.ASCENDING)])
            if (previous_code is not None):
                products.hint("_id_")
                products.min([("_id", previous_code)])
            typesense_products = []
            for p in products:
                parsed_product = safeCreate(p)
                if parsed_product is not None:
                    typesense_products.append(parsed_product)

            previous_code = typesense_products[-1]['id']
            ts_prd_docs.import_(typesense_products)

            nb_products_imported += batch_size
            reportProgress(nb_products_imported, nb_products_to_import)
        print('Import terminé!')
        time.sleep(2)

def queryTypeSense():
    query = ''
    while True:
        query = input("Nom du produit à chercher (q pour quitter) : ")
        if (query == "q"):
            break
        search_params = {
            'q' : query,
            'query_by' : 'name',
            'sort_by' : 'carbohydrates:asc',
            'use_cache': False,
        }
        start_time = time.time()
        res = client.collections['products'].documents.search(search_params)
        print("Recherche terminée en %f secondes" % (time.time() - start_time))
        print(f"{res['found']}/{res['out_of']} produits correspondants")
        print("Affichage des 10 premiers :")
        for hit in res['hits']:
            prd = hit['document']
            print(f"\t{prd['name']} ({prd['carbohydrates']}/100g)")
        print()

if (__name__ == '__main__'):
    # ============= Pré-requis =============
    # - installer le package typesense
    # - lancer le docker compose
    # - lancer le docker MongoDB
    # - modifier mongo_connection_string

    # Permet de créer la collection TypeSense qui stockera les produits
    #createCollection()

    # Permet d'importer le contenu de la base de données MongoDB dans TypeSense
    #importToTypeSense()
    
    # Faire des requêtes à TypeSense une fois le tout importé
    queryTypeSense()