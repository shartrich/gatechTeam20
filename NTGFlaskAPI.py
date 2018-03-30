import flask
from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask.ext.jsonpify import jsonify
import pandas as pd
import csv


app = Flask(__name__)
api = Api(app)
engine = create_engine("mysql://sql9229495:2JAaltxk9J@sql9.freemysqlhosting.net/sql9229495", encoding='latin1', echo=True)




@app.route('/')
def hello_world():
    return 'Welcome to drayage API!'

def readCSV(csvFile):
    with open(csvFile, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

# Assigns a 3-Digit Standard ZipCode 
def zipSwitcher(integer):

    switcher = {
        1: "00",
        2: "0",
        3: ""
        }

    s = str(integer)

    return switcher.get(len(s)) + s

def addZip3(zipFull):
    zip = str(zipFull)

    try:
        t = int(zipFull[:5])
    except:
        #print(zipFull)
        return 'ZipError'

    lZip = len(zip)
    if lZip >= 5:
        return zip[:3]
    elif lZip == 4:
        return "0" + zip[:2]
    elif lZip == 3:
        return "00" + zip[:1]
    else:
        return 'ZipError'

def matchEquipment(equip):
    equip = equip.upper()
    e20 = ["'20FT CONTAINER'", "'20 STD'", "'20 HC'"]
    e40 = ["'40FT CONTAINER'", "'40 STD'", "'40 HC'"]

    if equip in e20 + e40:
        if equip in e20:
            temp = e20
            
        elif equip in e40:
            temp = e40
        else:
            print("Error on equipment:", equip)

    else:
        temp = [equip]


    #returns the set of matchable equipment
    return "("+str(temp)[1:-1] + ')'

class cities(Resource):
    def get(self):
        conn = engine.connect() # connect to database
        query = conn.execute("select Cons_City from drayage_march") # This line performs query and returns json result
        return {'Cons_Cities': [i[0] for i in query.cursor.fetchall()]} # Fetches first column that is Employee ID


class loadTest(Resource):
    def get(self, city,):
        conn = engine.connect()
        query = conn.execute("select * from drayage_march where Cons_City =%s "  %city)
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)

class loadTest2(Resource):
    def get(self, city, loadType):
        conn = engine.connect()


        #drayage_march will be whatever table holds pending orders (NTG)
        query = conn.execute("select * from drayage_march where Cons_City =%s and `UPPER[Truck_Number]` =%s "  %(city, loadType))
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}



        return jsonify(result)

class loadTest3(Resource):
    def get(self, steamShipLine, loadType, shipCity, clientCity, equipment):
        conn = engine.connect()
        query = conn.execute("select * from drayage_march where `UPPER[Driver]` =%s  and `UPPER[Truck_Number]` =%s and Ship_Zip =%s and Con_Zip =%s and Equipment =%s "  %(steamShipLine, loadType, shipCity, clientCity, equipment))
        #query = conn.execute("select * from drayage_march where `UPPER[Driver]` =%s  and `UPPER[Truck_Number]` =%s and Ship_Zip =%s and Con_Zip =%s and Equipment in %s "  %(steamShipLine, loadType, shipCity, clientCity, equipment))
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)


class findMatch(Resource):
    def get(self, steamShipLine, loadType, shipCity, clientCity, equipment):
        if loadType == 'EXPORT':
            retLoadType = 'IMPORT'
        elif loadType == 'IMPORT':
            retLoadType = 'EXPORT'
        else:
            return "Error on IMPORT/EXPORT label"

        retEquipment = matchEquipment(equipment)


        conn = engine.connect()
        query = conn.execute("select * from drayage_march where `UPPER[Driver]` =%s  and `UPPER[Truck_Number]` =%s and Ship_Zip =%s and Con_Zip =%s and Equipment in %s "  %(steamShipLine, retLoadType, shipCity, clientCity, retEquipment))
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)


class findMatchV2(Resource):
    def get(self, steamShipLine, loadType, shipCity, clientCity, equipment):
        if loadType == "'EXPORT'" or loadType == '"EXPORT"':
        retLoadType = "'IMPORT'"
    elif loadType == "'IMPORT'" or loadType == '"IMPORT"':
        retLoadType = "'EXPORT'"
    else:
        return "Error on IMPORT/EXPORT label"

        retEquipment = matchEquipment(equipment)

        #connect to DB and retreive basic results
        #!still needs addition of date fields in query to minimize data transfer
        conn = engine.connect()
        queryString = "select * from drayage_march where `UPPER[Driver]` =%s  and `UPPER[Truck_Number]` =%s and Ship_Zip =%s and Equipment in %s "  %(steamShipLine, retLoadType, shipCity, retEquipment)
        query = pd.read_sql_query(queryString, conn)
        

        #rename non-intuitive columns
        query.rename(index=str, columns={'`UPPER[Truck_Number]`': 'SteamShipLine', '`UPPER[Driver]`': 'ImpExp'})
        
        #add the 3digit zip equivalents and compute distances
        shipZip3 = addZip3(shipCity)
        clientZip3 = addZip3(clientCity)
        mainDistance = distanceReferences[(shipZip3, clientZip3)]

        #3 digit zips for table from sql
        query['ShipZip3'] = query['Ship_Zip'].apply(addZip3)
        query['ClientZip3'] = query['Client_Zip'].apply(addZip3)


        #computes distance of single trip and then based on the combined duo
        query['Distance'] = distanceReferences[(query['ShipZip3'], query['ClientZip3'])]
        #combined total of two trips run seperate. *2 because two legs of each
        query['IndivTotalDistance'] = (query['Distance'] + mainDistance) * 2

        #deadhead is the single empty leg of a pair
        query['DeadHead'] = distanceReferences[(shipZip3, query['ClientZip3'])]

        #distance of the 3 legs if trip was merged
        query['CombinedTotalDistance'] = query['DeadHead'] + query['Distance'] + mainDistance

        #filters for distance
        query = query.query('CombinedTotalDistance < IndivTotalDistance')

        return query

#consider a better method that doesnt need to invoke this O(n^2 is not ideal)
#!upload this file to PythonAnywhere
def distRef():
    # Create matrix with all the distances between the most used 3-digit zip codes 
    global distanceMatrix
    distanceMatrix = readCSV('matrixOfRealDistances.csv')

    headerRow = distanceMatrix[0][1:]

    distanceDict = {}

    # Find ZipCodes non-existent in the matrix and assign error
    #! check to see if multiple keys can all be constructed at once to reduce clunkiness
    for a in range(1,1000):
        zipA = zipSwitcher(a)
        distanceDict[(zipA, 'ZipError')] = 999999
        distanceDict[('ZipError', zipA)] = 999999
        # Remove duplicates (Remove keys that have the same (toZip, fromZip): value
        for b in range(1,1000):
            distanceDict[(zipA, zipSwitcher(b))] = 999999
    distanceDict[('ZipError', 'ZipError')] = 999999

    # Assign value to each (fromZip, toZip): distance value
    distanceRows = distanceMatrix[1:] 
    #for row in distanceMatrix:
    for row in distanceRows:

        fromZip = zipSwitcher(row[0])
        modifiedRow = row[1:]

        # Assign distance value between fromZip and toZip
        for colNum, item in enumerate(modifiedRow):
            toZip = zipSwitcher(headerRow[colNum])
            distanceDict[(fromZip, toZip)] = int(float(item))

    
    return distanceDict

global distanceReferences
distanceReferences = distRef()




api.add_resource(cities, '/cities') # Route_1
api.add_resource(loadTest, '/cities/<city>') # Route_3
api.add_resource(loadTest2, '/cities/<city>/<loadType>') # Route_3
api.add_resource(loadTest3, '/full/<steamShipLine>/<loadType>/<shipCity>/<clientCity>/<equipment>')

api.add_resource(findMatch, '/matches/<steamShipLine>/<loadType>/<shipCity>/<clientCity>/<equipment>')
api.add_resource(findMatchV2, '/matchesV2/<steamShipLine>/<loadType>/<shipCity>/<clientCity>/<equipment>') 





if __name__ == '__main__':
    app.run()

