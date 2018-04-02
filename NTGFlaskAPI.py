import flask
from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask.ext.jsonpify import jsonify
import pandas as pd
import csv

import re


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


#takes in raw inpurt and returns the proper 2 dates
def retreiveDates(rawInput, impExp):

    form = impExp.replace("'", "").replace('"', "").upper() #unnecessary, but quality control
    inp = rawInput.replace("'", "").replace('"', "").upper() #unnecessary, but quality control
    
    #construct a default date to use if none can be extracted
    tod = pd.Timestamp.today() - datetime.timedelta(1)

    #create dictionary with defaults for all values as yesterday
    dateLimits = {}
    #dateLimits["ETA"] = tod
    #dateLimits["LFD"] = tod
    #dateLimits["CUT"] = tod
    #dateLimits["ERD"] = tod

    #regex pattern with groups for word1, date1; word 2, date2
    pat = re.compile(r"(?P<word1>ERD|ETA|LFD|CUT)\s?"   \
                     + "(?P<date1>\d{1,2}\/\d{1,2}\/{0,1}\/{0,4})" \
                     + "([^a-zA-Z0-9\n]{0,3}"    \
                     + "(?P<word2>ERD|ETA|LFD|CUT)?\s?" \
                     + "(?P<date2>\d{1,2}\/\d{1,2}\/{0,1}\/{0,4}))?")
    
    m = pat.search(inp)
    
    #if regex fails
    if m == None:
        dateLimits["ETA"] = tod
        dateLimits["LFD"] = tod
        dateLimits["CUT"] = tod
        dateLimits["ERD"] = tod
        return dateLimits

    #export has CUT and ERD
    #!need to add year
    elif form == "EXPORT":
        if 'date2' in m.groupdict().keys(): #means it has both CUT and ERD
            dateLimits[m.group("word1")] = pd.to_datetime(m.group("date1"), format='%m/%d').replace(year = tod.year)
            dateLimits[m.group("word2")] = pd.to_datetime(m.group("date2"), format='%m/%d').replace(year = tod.year)

        #if only 1 date was captured
        elif 'date1' in m.groupdict().keys(): #means it has both CUT and ERD
            dateLimits[m.group("word1")] = pd.to_datetime(m.group("date1"), format='%m/%d').replace(year = tod.year)

            if m.group("word1") == "CUT":
                dateLimits["ERD"] = dateLimits["CUT"] - datetime.timedelta(4)
            if m.group("word1") == "ERD":
                dateLimits["CUT"] = dateLimits["ERD"] + datetime.timedelta(4)

        retList[dateLimits["CUT"], dateLimits["CUT"]]
        
    #has LFD and ETA
    elif form == "IMPORT":
        if 'date2' in m.groupdict().keys(): #means it has both LFD and ETA
            dateLimits[m.group("word1")] = pd.to_datetime(m.group("date1"), format='%m/%d').replace(year = tod.year)
            dateLimits[m.group("word2")] = pd.to_datetime(m.group("date2"), format='%m/%d').replace(year = tod.year)

        #if only 1 date was captured
        elif 'date1' in m.groupdict().keys(): #means it has only one item
            dateLimits[m.group("word1")] = pd.to_datetime(m.group("date1"), format='%m/%d').replace(year = tod.year)

            if m.group("word1") == "ETA":
                dateLimits["LFD"] = dateLimits["ETA"] + datetime.timedelta(4)
            if m.group("word1") == "LFD":
                dateLimits["ETA"] = dateLimits["LFD"] - datetime.timedelta(4)

        retList[dateLimits["ETA"], dateLimits["LFD"]]
    
    #returns the two items in a dictionary
    #return dateLimits

    #returns two items in a list (chronological order)
    return retList



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

    #!edit end to return a json, currently returns dataframe
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
        query['ClientZip3'] = query['Con_Zip'].apply(addZip3)

        #computes distance of single trip and then based on the combined duo
        tempDF = zip(query.ShipZip3, query.ClientZip3)
        newCol = [distanceReferences[(x,y)] for x,y in tempDF]
        query['Distance'] = newCol
        
        
        #combined total of two trips run seperate. *2 because two legs of each
        query['IndivTotalDistance'] = (query['Distance'] + mainDistance) * 2

        #deadhead is the single empty leg of a pair
        tempDF = query.ClientZip3
        newCol = [distanceReferences[(clientZip3,x)] for x in tempDF]
        query['DeadHead'] = newCol

        #distance of the 3 legs if trip was merged
        tempDF = zip(query.DeadHead, query.Distance)
        newCol = [mainDistance + x + y for x,y in tempDF]
        query['CombinedTotalDistance'] = newCol

        #filters for distance
        query = query.query('CombinedTotalDistance < IndivTotalDistance')

        return query

class findMatchV3(Resource):

    #!edit end to return a json, currently returns dataframe
    def get(self, steamShipLine, loadType, shipCity, clientCity, equipment, rawInput):
        loadType = loadType.upper()
        if loadType == "'EXPORT'" or loadType == '"EXPORT"':
            retLoadType = "'IMPORT'"
        elif loadType == "'IMPORT'" or loadType == '"IMPORT"':
            retLoadType = "'EXPORT'"
        else:
            return "Error on IMPORT/EXPORT label"


        #returns either [ETA, LFD] or [ERD, CUT]
        dateLimits = retreiveDates(rawInput, loadType)


        #grabs a list of valid matching equipment items
        retEquipment = matchEquipment(equipment)

        #connect to DB and retreive basic results
        #!still needs addition of date fields in query to minimize data transfer
        conn = engine.connect()
        queryString = "select * from drayage_march where `UPPER[Driver]` =%s  and `UPPER[Truck_Number]` =%s and Ship_Zip =%s and Equipment in %s "  %(steamShipLine, retLoadType, shipCity, retEquipment)
        
        query = pd.read_sql_query(queryString, conn)

        #rename non-intuitive columns
        query.rename(index=str, columns={'`UPPER[Truck_Number]`': 'SteamShipLine', '`UPPER[Driver]`': 'ImpExp', 'Trailer Number': 'rawInput'})
        
        #add the 3digit zip equivalents and compute distances
        shipZip3 = addZip3(shipCity)
        clientZip3 = addZip3(clientCity)
        mainDistance = distanceReferences[(shipZip3, clientZip3)]

        #3 digit zips for table from sql
        query['ShipZip3'] = query['Ship_Zip'].apply(addZip3)
        query['ClientZip3'] = query['Con_Zip'].apply(addZip3)

        #computes distance of single trip and then based on the combined duo
        tempDF = zip(query.ShipZip3, query.ClientZip3)
        newCol = [distanceReferences[(x,y)] for x,y in tempDF]
        query['Distance'] = newCol
        
        
        #combined total of two trips run seperate. *2 because two legs of each
        query['IndivTotalDistance'] = (query['Distance'] + mainDistance) * 2

        #deadhead is the single empty leg of a pair
        tempDF = query.ClientZip3
        newCol = [distanceReferences[(clientZip3,x)] for x in tempDF]
        query['DeadHead'] = newCol

        #distance of the 3 legs if trip was merged
        tempDF = zip(query.DeadHead, query.Distance)
        newCol = [mainDistance + x + y for x,y in tempDF]
        query['CombinedTotalDistance'] = newCol


        #filters for distance
        query = query.query('CombinedTotalDistance < IndivTotalDistance')

        #Turns the raw input into 2 viable dates
        tempDF = zip(query.rawInput, query.ImpExp)
        newCol = zip([retreiveDates(x,y) for x,y in tempDF])
        query['DateLim1'] = newCol[0]
        query['DateLim2'] = newCol[1]

        #filters for datesLimits
        if loadType == "'IMPORT'":
            #list of trips all exports

            #LFD to ERD
            query['LFDtoERD'] = abs(query.date[0] - dateLimits[1])

            #ETA to CUT
            query['ETAtoCUT'] = query.date[1] - dateLimits[0]


        elif loadType == "'EXPORT'":
            #LFD to ERD
            query['LFDtoERD'] = abs(query.date[1] - dateLimits[0])

            #ETA to CUT
            query['ETAtoCUT'] = -dateLimits[1] + query.date[0]

        #date filtering query:::
        query = query.query("LDFtoERD <= 2 and ETAtoCUT >= 0")


        #return dfToResponse(query)

        return query


#takes a filtered pandas dataframe and returns a JSON API response
def dfToResponse(df):
    
    

    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    return jsonify(result)


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
api.add_resource(findMatchV3, '/matchesV2/<steamShipLine>/<loadType>/<shipCity>/<clientCity>/<equipment>/<rawInput>') 





if __name__ == '__main__':
    app.run()

