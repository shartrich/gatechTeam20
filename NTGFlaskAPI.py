import flask
from flask import Flask, request
from sqlalchemy import create_engine
import pandas as pd
import csv
from flask.ext.jsonpify import jsonify
import re
import datetime
import numpy as np
from collections import OrderedDict



defaults = {}
defaults['server'] = "sql9.freemysqlhosting.net"
defaults['name'] = "sql9231477"
defaults['username'] = "sql9231477"
defaults['password'] = "fhGB7MNW5I"
defaults['table'] = "march_drayage"


#engineString = "mysql://" + username + password + "@" + server + name

#engine = create_engine("mysql://sql9229495:2JAaltxk9J@sql9.freemysqlhosting.net/sql9229495", encoding='latin1', echo=True)
#engine = create_engine(engineString)




app = Flask(__name__)




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
        #! might be returning extra errors
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
    equip = equip.upper().replace("'", "").replace('"','')


    e20 = ['20FT CONTAINER', '20 STD', '20 HC']
    e40 = ['40FT CONTAINER', '40 STD', '40 HC']

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
    #print("XXXXXXXXXX", rawInput, impExp)


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

    #print("XXXXXXXXXX2", inp, form)
    #regex pattern with groups for word1, date1; word 2, date2
    pat = re.compile(r"(?P<word1>ERD|ETA|LFD|CUT)\s?"   \
                     + "(?P<date1>\d{1,2}\/\d{1,2}\/{0,1}\/{0,4})" \
                     + "([^a-zA-Z0-9\n]{0,3}"    \
                     + "(?P<word2>ERD|ETA|LFD|CUT)?\s?" \
                     + "(?P<date2>\d{1,2}\/\d{1,2}\/{0,1}\/{0,4}))?")

    m = pat.search(inp)

    #print(m.groupdict().keys())
    #retList = []

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
        if m.group('date2') != None: #means it has both CUT and ERD
            dateLimits[m.group("word1")] = pd.to_datetime(m.group("date1"), format='%m/%d').replace(year = tod.year)
            dateLimits[m.group("word2")] = pd.to_datetime(m.group("date2"), format='%m/%d').replace(year = tod.year)

        #if only 1 date was captured
        elif m.group('date1') != None: #means it has both CUT and ERD
            dateLimits[m.group("word1")] = pd.to_datetime(m.group("date1"), format='%m/%d').replace(year = tod.year)

            if m.group("word1") == "CUT":
                dateLimits["ERD"] = dateLimits["CUT"] - datetime.timedelta(4)
            if m.group("word1") == "ERD":
                dateLimits["CUT"] = dateLimits["ERD"] + datetime.timedelta(4)

        retList = [dateLimits["ERD"], dateLimits["CUT"]]

    #has LFD and ETA
    elif form == "IMPORT":
        if m.group('date2') != None: #means it has both LFD and ETA
            dateLimits[m.group("word1")] = pd.to_datetime(m.group("date1"), format='%m/%d').replace(year = tod.year)
            dateLimits[m.group("word2")] = pd.to_datetime(m.group("date2"), format='%m/%d').replace(year = tod.year)

        #if only 1 date was captured
        elif m.group('date1') != None: #means it has only one item
            dateLimits[m.group("word1")] = pd.to_datetime(m.group("date1"), format='%m/%d').replace(year = tod.year)

            if m.group("word1") == "ETA":
                dateLimits["LFD"] = dateLimits["ETA"] + datetime.timedelta(4)
            if m.group("word1") == "LFD":
                dateLimits["ETA"] = dateLimits["LFD"] - datetime.timedelta(4)


        retList = [dateLimits["ETA"], dateLimits["LFD"]]

    #returns the two items in a dictionary
    #return dateLimits
    #print('RETLIST', retList)
    #returns two items in a list (chronological order)
    return retList


#consider a better method that doesnt need to invoke this O(n^2 is not ideal)
#!upload this file to PythonAnywhere
def distRef():
    # Create matrix with all the distances between the most used 3-digit zip codes
    global distanceMatrix
    #distanceMatrix = readCSV('matrixOfRealDistances.csv')

    ####!!!!!##!#!#!#!#! adjust in new api host
    distanceMatrix = readCSV('/home/shartrich/mysite/matrixOfRealDistances.csv')

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


@app.route('/matchMaker')
def matchMaker():
    #single input var is integer loadID, use SQL to return trip data items
    loadID =  request.args.get('loadID', default = 0, type = int)
    dataTable =  request.args.get('table', default = defaults['table'], type = str)


    #determine defaults for MySQL connection
    server =  request.args.get('server', default = defaults['server'], type = str)
    name =  request.args.get('name', default = defaults['name'], type = str)
    username =  request.args.get('username', default = defaults['username'], type = str)
    password =  request.args.get('password', default = defaults['password'], type = str)


    #construct ssh connection with
    engineString = "mysql://" + username + ":" + password + "@" + server + "/" + name
    engineString =  request.args.get('database_engine', default = engineString, type = str)
    #engine = create_engine("mysql://sql9229495:2JAaltxk9J@sql9.freemysqlhosting.net/sql9229495", encoding='latin1', echo=True)

    engine = create_engine(engineString, encoding='latin1', echo=True)
    #query to look into target trip
    firstQuery = "SELECT * from %s where ID = %s"  %(dataTable, loadID)

    #return SQL query as pandas table
    conn = engine.connect()
    focusLoad = pd.read_sql_query(firstQuery, conn, index_col=['Id'])
    conn.close()

    #declare all needed values of trip
    loadType = focusLoad['UPPER[Truck_Number]'].values[0]
    steamShipLine = "'" + focusLoad['UPPER[Driver]'].values[0] + "'"
    clientCity = focusLoad['Con_Zip'].values[0]
    shipCity = focusLoad['Ship_Zip'].values[0]
    equipment = focusLoad['Equipment'].values[0]
    rawInput = focusLoad['Trailer_Number'].values[0]


    loadType = loadType.upper()
    if loadType == "'EXPORT'" or loadType == '"EXPORT"' or loadType == 'EXPORT':
        retLoadType = "'IMPORT'"
    elif loadType == "'IMPORT'" or loadType == '"IMPORT"' or loadType == 'IMPORT':
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
    engine = create_engine(engineString)


    queryString = "SELECT * from %s where `UPPER[Driver]` =%s  and `UPPER[Truck_Number]` =%s and Ship_Zip =%s and Equipment in %s " %(dataTable, steamShipLine, retLoadType, shipCity, retEquipment)


    query = pd.read_sql_query(queryString, conn, index_col=['Id'])
    #query = pd.read_sql_query(queryString, conn)
    conn.close()


    #rename non-intuitive columns
    query.rename(index=str, columns={'`UPPER[Truck_Number]`': 'ImpExp', '`UPPER[Driver]`': 'SteamShipLine', 'Trailer_Number': 'rawInput'})
    query.rename(columns={'UPPER[Truck_Number]': 'ImpExp', 'UPPER[Driver]': 'SteamShipLine', 'Trailer_Number': 'rawInput'}, inplace=True)


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
    #query.sort_values(by=['DeadHead'], ascending=True)

    #Turns the raw input into 2 viable dates
    tempDF = zip(query.rawInput, query.ImpExp)      #error is returning not loadType, but
    newCol = [retreiveDates(x,y) for x,y in tempDF]
    newCol1 = [x[0] for x in newCol]
    newCol2 = [x[1] for x in newCol]

    query['DateLim1'] = newCol1
    query['DateLim2'] = newCol2

    #make list of colummns to be exported
    #outputCols = ['Id', 'DeadHead', 'ImpExp', "SteamShipLine", 'Equipment', 'Ship_City_Full', 'Ship_Zip', 'Cons_City_Full', 'Con_Zip']

    #outputCols = ['DeadHead', 'ImpExp', "SteamShipLine", 'Equipment', 'Ship_City_Full', 'Ship_Zip', 'Cons_City_Full', 'Con_Zip']
    outputCols = ['DeadHead', 'ImpExp', "SteamShipLine", 'Equipment', 'Ship_City_Full', 'Cons_City_Full']

    #filters for datesLimits
    if loadType == "'IMPORT'" or loadType == '"IMPORT"' or loadType == 'IMPORT':
        #list of trips all exports

        #LFD to ERD
        query['LFDtoERD'] = ((query.DateLim1 - dateLimits[1]) / np.timedelta64(1, 'D')).astype(int)


        #ETA to CUT
        query['ETAtoCUT'] = ((query.DateLim2 - dateLimits[0])/ np.timedelta64(1, 'D')).astype(int)

        query['ERD'] = query.DateLim1.apply(lambda x: pd.to_datetime(str(x)).strftime('%m/%d/%Y'))
        query['CUT'] = query.DateLim2.apply(lambda x: pd.to_datetime(str(x)).strftime('%m/%d/%Y'))
        outputCols.extend(['ERD', 'CUT'])

        print(query['ERD'])


    elif loadType == "'EXPORT'" or loadType == '"EXPORT"' or loadType == 'EXPORT':
        #LFD to ERD
        query['LFDtoERD'] = ((query.DateLim2 - dateLimits[0]) / np.timedelta64(1, 'D')).astype(int)

        #ETA to CUT
        query['ETAtoCUT'] = ((query.DateLim1 - dateLimits[1]) / np.timedelta64(1, 'D')).astype(int)

        query['ETA'] = query.DateLim1.apply(lambda x: pd.to_datetime(str(x)).strftime('%m/%d/%Y'))
        query['LFD'] = query.DateLim2.apply(lambda x: pd.to_datetime(str(x)).strftime('%m/%d/%Y'))
        outputCols.extend(['ETA', 'LFD'])

    else:
        return "Error on IMPORT/EXPORT label"

    query = query.query("LFDtoERD <= 2 and ETAtoCUT >= 0")

    tempDF = zip(query.Cons_City, query.Cons_State, query.Con_Zip)
    newCol = [x + ', ' + y + " " + str(z) for x,y,z in tempDF]
    query['Cons_City_Full'] = newCol

    tempDF = zip(query.Ship_City, query.Ship_State, query.Ship_Zip)
    newCol = [x + ', ' + y + " " + str(z) for x,y,z in tempDF]
    query['Ship_City_Full'] = newCol

    outputDF = query[outputCols].copy()

    #kys = tuple(['LoadID'] + list(query.keys()))
    #app.config['JSON_SORT_KEYS'] = False
    #res = [OrderedDict(zip(kys, i)) for i in query.itertuples(index=True)]
    #result = {'Potential Matches for ' + str(loadID): res}


    outputDF = query[outputCols].copy()
    outputDF['DeadHead'] = outputDF['DeadHead'].astype('int')
    outputDF.sort_values(by='DeadHead', inplace=True)


    kys = tuple(['LoadID'] + list(outputDF.keys()))
    app.config['JSON_SORT_KEYS'] = False
    res = [OrderedDict(zip(kys, i)) for i in outputDF.itertuples(index=True)]
    result = {'Potential Matches for ' + str(loadID): res}


    return jsonify(result)



if __name__ == '__main__':
    app.run()
    #pass
