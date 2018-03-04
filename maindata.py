import requests
import json

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': 'f07414cab6e445e690c230b8b3539dda'
}
api = 'https://dev.tescolabs.com/grocery/products/?query=%s&offset=0&limit=20'

def getProducts(searchstring):
    response = requests.get(api % (searchstring), headers=headers)
    data = response.json()  

    #store the results in a file
    #jsonfile = open('static/data.json','w')
    #jsonfile.write(json.dumps(data['uk']['ghs']['products']['results'])) 
    #jsonfile.close()

    return data['uk']['ghs']['products']['results']