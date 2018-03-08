#Sean Hartrich
#Georgia Tech ISyE Senior Design Spring 2018
#Team 20

#Distance Matrix Generator

import pandas as pd
import numpy as np
import csv

from geopy.geocoders import Nominatim

import math
from vincenty import vincenty
import time

import zipcode
import uszipcode
import googlemaps

import gmplot

import re
import time


def zipToCordinates(fullZipcodeList):
    tracker = ""
    
    try:
        zips = [j[2] for j in fullZipcodeList] 
        left3 = [j[0] for j in fullZipcodeList]

    except:
        fullZipcodeList = [j[0].split('\t') for j in fullZipcodeList]
        zips = [j[2] for j in fullZipcodeList] 
        left3 = [j[0] for j in fullZipcodeList]

    search = uszipcode.ZipcodeSearchEngine()

    zipOutput = [['Zip3', 'Zipcode', 'Z', 'ZipcodeType', 'City', 'State', 'Population', 'Density', 'TotalWages', 'Wealthy', 'HouseOfUnits', 'LandArea', 'WaterArea', 'Latitude', 'Longitude', 'NEBoundLatitude', 'NEBoundLongitude', 'SWBoundLatitude', 'SWBoungLongitude']]
    
    for item in zips:
        try:
            zipcodeItem = search.by_zipcode(item)
            zipData = list(zipcodeItem)

            if zipData[0] == None:
                myzip = zipcode.isequal(str(item))
                temp = [item[:3], item] + [item, 'XX', myzip.city, myzip.state, myzip.population, 'XX', 'XX', 'XX', 'XX', 'XX', 'XX', myzip.lat, myzip.lon, 'XX', 'XX', 'XX', 'XX']

            else:                
                temp = [item[:3], item] + zipData

        except:
            tracker = tracker + "Error on zipcode: " + item +"\n"
            temp = [item[:3], item] + [item, 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']

        zipOutput.append(temp)
            #zipOutput.append(temp)

    print(tracker)

    return zipOutput

def printZipcodeData():
    data = csvToListOfRowLists("C:\\Users\\sean.hartrich\\Downloads\\zipCodesAll.csv")
    output = zipToCordinates(data)
    printListofTuples(output,"C:\\Users\\sean.hartrich\\Downloads\\zipcodeOutputData5.csv")


# Function to convert a csv file to a list of dictionaries.  Takes in one variable called "variables_file" 
def csvToDictionary(csvFile):
    with open(csvFile, 'r') as f:
        reader = csv.reader(f)
        allData = list(reader)
    dataItems = allData[1::]
    newDict = {}
        
    for item in dataItems:
        newDict[item[0]] = item[1::]

    return newDict

    
def csvToListOfRowLists(csvFile):
    with open(csvFile, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
        uniqueCities = data[1::]
    return uniqueCities

def readCSVwithHeaders(csvFile):
    with open(csvFile, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

def editCities(cityList, converterDict):
    newCityList = []
    for city in cityList:
        comma = city.find(', ')

        try:
            lft = city[:comma+2]
            abb = city[comma+2:]
            rght = converterDict[abb][0]
            newCityList.append(lft + rght)
        except:
            print("Failure to identify state of:", city)
            
    return newCityList

def generalizedZipcodes(cityList):
    duos = []
    geolocator = Nominatim()

    for city in cityList:
        try:
            location = geolocator.geocode(city, timeout = 5)
            revLocation = geolocator.reverse(str(location.latitude) + ', ' + str(location.longitude))
            #duos.append((city, location.address, location.latitude, location.longitude, revLocation.raw['address']['postcode']))
            duos.append((city, location.latitude, location.longitude, revLocation.raw['address']['postcode']))
            time.sleep(1)
        except:
            print("Unable to locate:", city)
            duos.append((city, 'X', 'X', 'X'))
            
    return duos
                        
def printListofTuples(listOfTuples, outputFile):
    with open(outputFile,'w', newline='') as out:
        csv_out=csv.writer(out)
        #csv_out.writerow(header)   #adds header to first row of csv file
        for row in listOfTuples:
            csv_out.writerow(row)
                            
        
#df = pd.read_csv("C:\\Users\\sean.hartrich\\Downloads\\Unique Cities.csv")

def scrapeCityData():
    rawCities = csvToListOfRowLists("C:\\Users\\sean.hartrich\\Downloads\\CitiesByOccurence.csv")
    uniqueCities = [j[0] for j in rawCities]
    converter = csvToDictionary("C:\\Users\\sean.hartrich\\Downloads\\abbToState.csv")

    fixedCities = editCities(uniqueCities, converter)

    withZips = generalizedZipcodes(fixedCities)

    header = ['City', 'Latitude', 'Longitude', 'Zipcode']
    outputList = header + withZips
    
    printListofTuples(outputList, "C:\\Users\\sean.hartrich\\Downloads\\citiesOutput3.csv")

def generateZipcodes():
    pass


def vincentyDistanceMatrixZipcodes(zipcodeList):    #reads in zipcode as [3digitzip, sampleZipcode, lat, long]
    byLead3 = ["", [j[0] for j in zipcodeList]]
    #print(forNames)
    #print(forZips)
    
    for cityA in zipcodeList:
        tempOfCity = [cityA[0]]

        try:
            latA = float(cityA[2])
            lonA = float(cityA[3])
        except:
            pass

        for cityB in zipcodeList:
            if cityA != cityB:
                try:
                    latB = float(cityB[2])
                    lonB = float(cityB[3])
                
                    A = (latA,lonA)
                    B = (latB,lonB)
                    
                    distance = vincenty(A,B,miles=True)
                except:
                    #print("Error on", cityA[0], "to", cityB[0])
                    distance = 'X'
            else:
                distance = 0
                
            tempOfCity.append(distance)

        byLead3.append(tempOfCity)

    printListofTuples(byLead3, 'C:\\Users\\sean.hartrich\\Downloads\\zip3DistanceMatrix.csv')  
                    
def vincentyDistanceMatrix(cityList):
    forNames = ["", [j[0] for j in cityList]]
    #print(forNames)
    #print(forZips)
    
    for cityA in cityList:
        tempOfCity = [cityA[0]]
        tempOfZip = [cityA[3]]
        try:
            latA = float(cityA[1])
            lonA = float(cityA[2])
        except:
            pass

        for cityB in cityList:
            if cityA != cityB:
                try:
                    latB = float(cityB[1])
                    lonB = float(cityB[2])
                
                    A = (latA,lonA)
                    B = (latB,lonB)
                    
                    distance = vincenty(A,B,miles=True)
                except:
                    #print("Error on", cityA[0], "to", cityB[0])
                    distance = 'X'
            else:
                distance = 0
                
            tempOfCity.append(distance)
            tempOfZip.append(distance)

        forZips.append(tempOfZip)
        forNames.append(tempOfCity)

    return forNames, forZips


def printBasicMatrix():
    data = csvToListOfRowLists("C:\\Users\\sean.hartrich\\Downloads\\citiesOutput3.csv")

    names, zips = vincentyDistanceMatrix(data)
    printListofTuples(names, "C:\\Users\\sean.hartrich\\Downloads\\basicCityDistanceMatrix.csv")
    printListofTuples(names, "C:\\Users\\sean.hartrich\\Downloads\\basicZipcodeDistanceMatrix.csv")

def loadMajorDistanceMatrix():
    csvFile = "C:\\Users\\sean.hartrich\\Downloads\\majorDistances.csv"
    with open(csvFile, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

def calcMajorDistanceMatrix():
    data = csvToListOfRowLists("C:\\Users\\sean.hartrich\\Downloads\\zipcodeOutputData4.csv")

def zipCodesToCoor():
    data = csvToListOfRowLists("C:\\Users\\sean.hartrich\\Downloads\\zipCodesAll.csv")
    dig3 = [j[2] for j in data]
    zips = [j[0] for j in data]


def verifyGoogle():
    import requests

    try:
        response = requests.get('http://www.google.com')
    except:
        print('Can\'t connect to Google\'s server')
        raw_input('Press any key to exit.')
    quit()

def testSpliceAlgorithm():
    coo = [1,2,3,4,5,6,7,8,9]
    numItems = len(coo)
    marker = []
    for idx in range(0, numItems - 1):
        temp1 = coo[(idx + 1):]
        temp2 = [coo[idx]]
        for t in temp1:
            marker.append((t, temp2[0]))

#print(marker)
#print(len(marker))

    for i in coo:
        for j in coo:
            if (i,j) in marker or (j,i) in marker:
                pass
            else:
                print((i,j))

def loadMajorZips():    #returns list of major zips as [3firstdigits, Zipcode, latitude, longitude]
    zips = csvToListOfRowLists("C:\\Users\\sean.hartrich\\Downloads\\zipcodeOutputData5.csv")

    validZips = []

    for item in zips:
        if item[4] == "X":
            pass
        else:
            validZips.append(item)

    zipsPure = [[j[0], j[1], j[13], j[14]] for j in validZips]
    return zipsPure


def launch():
    pass

def retreiveRoutes():
    progress = csvToListOfRowLists("C:\\Users\\sean.hartrich\\Downloads\\zip3GoogleMapsPathMiles.csv")

    progressCodes = {}

    for row in progress:
        city1 = str(row[0])
        city2 = str(row[1])

            #########################3
        if len(city1) == 2:
            city1 = '0' + city1
        if len(city2) == 2:
            city2 = '0' + city2
            #######################

        tempConcat = city1 + "_" + city2

        try:
            progressCodes[tempConcat] = float(row[2])
        except:
            progressCodes[tempConcat] = row[2]

    return progressCodes

def appendToCSV(lines, fileName):   #reads in lines as list of rows: [[row1], [row2], [row3]]
    with open(fileName, 'a', newline = '') as f:
        writer = csv.writer(f)
        for row in lines:
            writer.writerow(row)


def googleMapZipPaths(origins, destinations):
    #takes in list of (lat, long) tuples for both origins and destinations
    #purify zipcode list before running this

    gmaps = googlemaps.Client(key='AIzaSyD6zrIqz5SYqLE2NdZb0MQ4noltWPHE3rA')
    matrix = gmaps.distance_matrix(origins, destinations, mode="driving")

    return matrix


def spliceZipsIntoMatrix(zipcodeList):
    #takes in a list of all zipcodes that need to be mapped out
    #only use filtered list of zips you want route between

    #zips = [j[0] for j in zipcodeList]

    calculatedRoutes = retreiveRoutes()
    existingRoutes = calculatedRoutes.keys()

    newRoutes = 0
    ct294 = 0

    zips = [j[0] for j in zipcodeList]
    coordinates = [(j[2], j[3]) for j in zipcodeList]

    numItems = len(coordinates)

    for idx in range(0, numItems - 1):
        tempOZip = zips[(idx + 1):]
        tempOrigin = coordinates[(idx + 1):]


        destinationZip = str(zips[idx])
        tempDestination = [coordinates[idx]]    #takes a single target destination to prevent overlap

        originIdx = 0
        while originIdx < len(tempOZip):
            #testCase = str(zips[originIdx]) +  "_" + str(destinationZip)
            testCase = str(tempOZip[originIdx]) +  "_" + str(destinationZip)

            #if testCase in existingRoutes or zips[originIdx] == destinationZip:
            if testCase in existingRoutes or tempOZip[originIdx] == destinationZip:
                tempOZip.pop(originIdx)
                tempOrigin.pop(originIdx)

            else:
                originIdx = originIdx + 1


        if len(tempOrigin) > 0: #proceeds to next step IFF the origin vector has valid items
            #runGoogleMaps(tempOrigin, tempDestination)
            newRoutes = newRoutes + len(tempOrigin)
            print(tempOZip)
            print(destinationZip)
    
    print("Num new routes:", newRoutes)    


#pulls in all zip codes and tries to append as many routes as possible until alg crashes (reaches max limit of API request pulls)
def spliceMajorZips(zipcodeList, maxInterest = 100):

    zipcodeList = zipcodeList[:100]
    maxInterest = max(maxInterest, len(zipCodeList))



    calculatedRoutes = retreiveRoutes()
    existingRoutes = calculatedRoutes.keys()


    zips = [j[0] for j in zipcodeList]
    coordinates = [(j[2], j[3]) for j in zipcodeList]
    numItems = len(coordinates)

    newRoutes = 0


    for idx in range(0, maxInterest):
        tempOZip = zips
        tempOZip.pop(idx)

        tempOrigin = coordinates
        tempOrigin.pop(idx)


        destinationZip = str(zips[idx])
        tempDestination = [coordinates[idx]]    #takes a single target destination to prevent overlap

        validOrigins = []

        for originIdx in range(0, len(tempOZip)):
            testCase = str(tempOZip[originIdx]) +  "_" + destinationZip
            
            if testCase in existingRoutes or tempOZip[originIdx] == destinationZip:
                pass
            else:
                validOrigins.append(tempOrigin[originIdx])

        #print(len(validOrigins)
        if len(validOrigins) > 0:
            if newRoutes + len(validOrigins) <= 2450:

                rngMax = math.ceil(len(validOrigins)/25)
                for k in range(rngMax):
                    try:
                        properOriginSet = validOrigins[(25*k):(25*(k+1))]
                    except:
                        properOriginSet = validOrigins[(25*k):]
                    runGoogleMaps(properOriginSet, tempDestination)

                newRoutes = newRoutes + len(validOrigins)

                #print("Num new routes:", newRoutes)
                #print("Ended on index:", idx, "Zip3 =", tempDestination)

            else:
                adjustedVolume = 2500 - newRoutes
                adjustedValidOrigins = validOrigins[:adjustedVolume]

                rngMax = math.ceil(len(adjustedValidOrigins)/25)
                for k in range(rngMax):
                    try:
                        properOriginSet = adjustedValidOrigins[(25*k):(25*(k+1))]
                    except:
                        properOriginSet = adjustedValidOrigins[(25*k):]
                    runGoogleMaps(properOriginSet, tempDestination)


                newRoutes = newRoutes + len(adjustedValidOrigins)


                print("Num new routes:", newRoutes)
                print("Ended on index:", idx, "Zip3 =", destinationZip)
                quit()
        else:
            print(destinationZip, "is completed")
            pass

def buildZipDictionary():
    zipRows = loadMajorZips()
    zipDictionary = {}
    for row in zipRows:
        zip = row[0]
        if len(zip) == 2:
            zip = "0" + zip
        zipDictionary[zip] = (row[2], row[3])

    return zipDictionary

def constructDistanceMatrix():
    routes = csvToListOfRowLists("C:\\Users\\sean.hartrich\\Downloads\\zip3GoogleMapsPathMiles.csv")
    zipRows = loadMajorZips()
    zips = [j[0] for j in zipRows]

    zipRefDictionary = {}
    numItems = len(zips)

    #outputDictionaries = {}
    #uniqueItems = zips.unique()

    outputArray = [[""] + zips]

    for dictIndex, z in enumerate(zips):
        temp = [z] + ['X'] * numItems
        temp[dictIndex + 1] = 0
        outputArray.append(temp)
        zipRefDictionary[z] = dictIndex

    for row in routes:
        #print(row)
        fromLoc = row[0]
        toLoc = row[1]

        if len(fromLoc) == 2:
            fromLoc = '0' + fromLoc
        if len(toLoc) == 2:
            toLoc = '0' + toLoc

        if fromLoc != "X" and toLoc != "X":
            try:
                fromIdx = zipRefDictionary[fromLoc] + 1
                toIdx = zipRefDictionary[toLoc] + 1
                dist = row[2]

                outputArray[fromIdx][toIdx] = dist
            except:
                pass

    printListofTuples(outputArray, "C:\\Users\\sean.hartrich\\Downloads\\realDistanceMatrix.csv")



def addDistanceEstimators(mappedNum = 60):
    rawDist = readCSVwithHeaders("C:\\Users\\sean.hartrich\\Downloads\\zip3DistanceMatrix.csv")
    distances = [k[:mappedNum] for k in rawDist]    #returns first n items for if its mapped or not

    refDictionary = {}
    for dictIndex, z in enumerate(distances[1:]):
        tempZ = z[0] 
        lenZ = len(tempZ)

        if lenZ == 3:
            pass
        elif lenZ == 2:
            tempZ = "0" + tempZ
        elif lenZ == 1:
            tempZ = "00" + tempZ

        refDictionary[tempZ] = dictIndex + 1

    realDistDict = retreiveRoutes()
    

    zipRows = loadMajorZips()
    zips = [j[0] for j in zipRows]

    earlyMatrix = readCSVwithHeaders("C:\\Users\\sean.hartrich\\Downloads\\realDistanceMatrix.csv")
    c2Headers = earlyMatrix[0][1:]


    outputMatrix = [[""] + zips]
    errorCt = 0
    for rowIdx, row in enumerate(earlyMatrix[1:]):
        tempRow = []
        #valsOnly = row[1:]
        for idx, item in enumerate(row):
        #for idx, item in enumerate(valsOnly):
            #if item == "X":
            if idx > 0 and (item == "X" or rowIdx > mappedNum or idx > mappedNum):


                city1 = row[0]                  #pulls city from row header (first column)
                city2 = earlyMatrix[0][idx]     #pulls city from top of column (header)
                #city2 = c2Headers[idx]
                #city2 = earlyMatrix[0][idx] #pulls city from top of column (header)
                # print("Row#", rowIdx)
                # print("Col#", idx)

                # print("City1#", city1)
                # print("City2#", city2)

                vincentyDistance = float(rawDist[refDictionary[city1]][refDictionary[city2]])
                #print(city1, city2, vincentyDistance)
                #quit()

                adjustedCity1 = pullNearestMajorCity(city1, distances, refDictionary)
                adjustedCity2 = pullNearestMajorCity(city2, distances, refDictionary)



                ################
                try:
                    
                    #realDist = float(realDistDict[adjustedCity1 + "_" + adjustedCity2])

                    adjustedCity1Index = refDictionary[adjustedCity1]
                    adjustedCity2Index = refDictionary[adjustedCity2]

                    realDist = float(earlyMatrix[adjustedCity1Index][adjustedCity2Index])

                    adjustedVincenty = float(rawDist[adjustedCity1Index][adjustedCity2Index])

                    #print(adjustedCity1, adjustedCity2, adjustedVincenty)
                    #quit()

                    if adjustedVincenty > 0:
                        #print(vincentyDistance)
                        #print(adjustedVincenty)
                        ratio =  realDist / adjustedVincenty

                        distanceEstimate = ratio * vincentyDistance
                    else:
                        distanceEstimate = vincentyDistance
                except:
                    distanceEstimate = vincentyDistance
                    errorCt += 1


                ###############################3
                tempRow.append(distanceEstimate)
                
            else:
                tempRow.append(item)

        outputMatrix.append(tempRow)


                # pureRoute = True

                # if rowIdx > mappedNum:
                #     adjustedCity1 = pullNearestMajorCity(city1, distances)
                #     pureRoute = False
                # else:
                #     adjustedCity1 = city1

                # if idx > mappedNum:
                #     adjustedCity2 = pullNearestMajorCity(city2, distances)
                #     pureRoute = False
                # else:
                #     adjustedCity2 = city2

                # if pureRoute:
                #     distanceEstimate = realDistDict[adjustedCity1 + "_" + adjustedCity2]



    printListofTuples(outputMatrix, "C:\\Users\\sean.hartrich\\Downloads\\distanceMatrixEstimators2.csv")

    print(errorCt, "errors")


def pullNearestMajorCity(zip3, distances, refDict):

    distanceHeader = [k[0] for k in distances[1:]]
    tempRow = distances[refDict[zip3]][1:]
    distanceRow = [float(i) for i in tempRow]

    minDist = min(distanceRow)
    nearestMajorCity = distanceHeader[distanceRow.index(minDist)]

    if len(nearestMajorCity) == 2:
        nearestMajorCity = "0" + nearestMajorCity

    return nearestMajorCity



def testPull(zip3, mappedNum = 60):
    rawDist = readCSVwithHeaders("C:\\Users\\sean.hartrich\\Downloads\\zip3DistanceMatrix.csv")
    distances = [k[:mappedNum] for k in rawDist]    #returns first n items for if its mapped or not

    refDictionary = {}
    for dictIndex, z in enumerate(distances[1:]):
        tempZ = z[0] 
        lenZ = len(tempZ)

        if lenZ == 3:
            pass
        elif lenZ == 2:
            tempZ = "0" + tempToZip3
        elif lenZ == 1:
            tempZ = "00" + tempZ

        refDictionary[tempZ] = dictIndex + 1

    return pullNearestMajorCity(zip3, distances, refDictionary)

def testPull2(city1, city2, mappedNum = 60):
    rawDist = readCSVwithHeaders("C:\\Users\\sean.hartrich\\Downloads\\zip3DistanceMatrix.csv")
    distances = [k[:mappedNum] for k in rawDist]    #returns first n items for if its mapped or not

    refDictionary = {}
    for dictIndex, z in enumerate(distances[1:]):
        tempZ = z[0] 
        lenZ = len(tempZ)

        if lenZ == 3:
            pass
        elif lenZ == 2:
            tempZ = "0" + tempZ
        elif lenZ == 1:
            tempZ = "00" + tempZ

        refDictionary[tempZ] = dictIndex + 1

    print('City1:', city1)
    print('City2:', city2)
    vincenty = float(rawDist[refDictionary[city1]][refDictionary[city2]])
    print('Basic Vincenty:', vincenty)

    c1 = pullNearestMajorCity(city1, distances, refDictionary)
    c2 = pullNearestMajorCity(city2, distances, refDictionary)

    adjustedCity1Index = refDictionary[c1]
    adjustedCity2Index = refDictionary[c2]
    print('New City1:', c1)
    print('New City2:', c2)
    print(adjustedCity1Index)
    print(adjustedCity2Index)

    adjustedVincenty = float(rawDist[adjustedCity1Index][adjustedCity2Index])
    print("Representative Vincenty:", adjustedVincenty)

    earlyMatrix = readCSVwithHeaders("C:\\Users\\sean.hartrich\\Downloads\\realDistanceMatrix.csv")
    realDist = float(earlyMatrix[adjustedCity1Index][adjustedCity2Index])

    print("Representative Real Distance:", realDist)

    solution = realDist/adjustedVincenty * vincenty
    print("Adjusted Real Distance:", solution)




def addZeroDistRoutes():
    zipcodeList = loadMajorZips()
    zips = [j[0] for j in zipcodeList]

    zeroRoutes = []
    for z in zips:
        zeroRoutes.append([z,z,0])


    #print(zeroRoutes)
    appendToCSV(zeroRoutes, "C:\\Users\\sean.hartrich\\Downloads\\zip3GoogleMapsPathMiles.csv")

#Takes in origin coordinates and destination coordiantes lists and prints the results to 3 files
def runGoogleMaps(origins, destinations):
    #zips = [j[0] for j in fewZips]
    #coordinates = [(j[2], j[3]) for j in fewZips]

    #origins = coordinates
    #destinations = coordinates[0]

    gmaps = googlemaps.Client(key='AIzaSyD6zrIqz5SYqLE2NdZb0MQ4noltWPHE3rA')
    matrix = gmaps.distance_matrix(origins, destinations, mode="driving")


    #numOrigins = len(matrix['rows'])
    #numDestinations = len(sampleMatrix['rows'][0]['elements'])

    numOrigins = len(matrix['origin_addresses'])
    numDestinations = len(matrix['destination_addresses'])
    

    #rawMatrixList = [['FromAddress', 'ToAddress', 'DistanceOutput', 'Meters', 'Miles']]
    rawMatrixList = []
    #matrixOutputs = [['FromAddress', 'FromZip', 'FromZip3','ToAddress', 'ToZip', 'ToZip3', 'DistanceOutput', 'Meters', 'Miles']]
    #simpleOutput = [['FromZip3', 'ToZip3', 'Miles']]
    simpleOutput = []
    
    for a in range(0, numOrigins):
        
        tempToAdd = matrix['origin_addresses'][a]

        try:
            tempToZip = re.search('\d{5},', tempToAdd)[0][:-1]
            tempToZip3 = tempToZip[:3]
        except:
            tempToZip = 'X'
            tempToZip3 = 'X'
            
        
        for b in range(0, numDestinations):
        
            tempFromAdd = matrix['destination_addresses'][b]
            
            try:
                tempDistanceOutput = matrix['rows'][a]['elements'][b]['distance']['text']    

                tempMeters = matrix['rows'][a]['elements'][b]['distance']['value']
                
                tempMiles = round(tempMeters / 1609.34, 2)


            except:
                tempDistanceOutput = matrix['rows'][a]['elements'][b]
                tempMeters = 'X'
                tempMiles = 'X'


            tempA = [tempFromAdd, tempToAdd, tempDistanceOutput, tempMeters, tempMiles]
            tempB = [tempToAdd, tempFromAdd, tempDistanceOutput, tempMeters, tempMiles]



            rawMatrixList.append(tempA)
            rawMatrixList.append(tempB)

            #below lines try to pull out the zip codes of the addresses neatly
            try:
                tempFromZip = re.search('\d{5},', tempFromAdd)[0][:-1]
                tempFromZip3 = tempFromZip[:3]

            except:
                tempFromZip = 'X'
                tempFromZip3 = 'X'
            
            temp2A = [tempFromZip3, tempToZip3, tempMiles]
            temp2B = [tempToZip3, tempFromZip3, tempMiles]

            simpleOutput.append(temp2A)
            simpleOutput.append(temp2B)

    
    
    appendToCSV(simpleOutput, "C:\\Users\\sean.hartrich\\Downloads\\zip3GoogleMapsPathMiles.csv")
    appendToCSV(rawMatrixList, "C:\\Users\\sean.hartrich\\Downloads\\rawMatrixGoogleMaps.csv")
    

    #return matrix


def showMapProgress(saveFileName='ProgressMap.html'):
    progress = csvToListOfRowLists("C:\\Users\\sean.hartrich\\Downloads\\zip3GoogleMapsPathMiles.csv")
    zips = loadMajorZips()

    coorDict = {}

    pairs = []

    for row in zips:
        coorDict[row[0]] = (row[2], row[3])


    for row in progress:
        try:
            pairs.append([coorDict[row[0]], coorDict[row[1]]])
        except:
            pass


    gmap = gmplot.gmplot.GoogleMapPlotter.from_geocode("United States", zoom = 4.5)


    for item in pairs:
        #pathLat = [round(item[0][0],2), round(item[1][0],2)]
        #pathLon = [round(item[0][1], 2), round(item[1][1], 2)]        

        pathLat = [float(item[0][0]), float(item[1][0])]
        pathLon = [float(item[0][1]), float(item[1][1])]        



        gmap.plot(pathLat,pathLon,'cornflowerblue', edge_width=1)

    
    gmap.draw(saveFileName)


def addMoreRoutes():
    start = time.time()
    zips = loadMajorZips()
    spliceMajorZips(zips, 100)
    constructDistanceMatrix()


zips = loadMajorZips()
spliceMajorZips(zips)


#constructDistanceMatrix()
#distances = csvToListOfRowLists("C:\\Users\\sean.hartrich\\Downloads\\zip3DistanceMatrix.csv")
#print(distances[752])

#print(testPull('582'))


#addZeroDistRoutes()
#addDistanceEstimators(60)

#print(testPull('946'))
#print(testPull('108'))

#testPull2('415', '913')
#r = retreiveRoutes()
#print(r['415_913'])

#showMapProgress('ProgressMap6.html')
#100 first zips are mapped out