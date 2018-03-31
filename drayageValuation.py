# Import modules to be used
import csv
import datetime
import time
import pandas as pd
import numpy as np
import bisect
import math
#import gmplot
import random
import copy
from operator import itemgetter

''' VISUAL AID FOR ROUTING
def loadMajorZips():    #returns list of major zips as [3firstdigits, Zipcode, latitude, longitude]
	zips = readCSV("zipcodeOutputData5.csv")
	zips = zips[1:]

	validZips = []

	for item in zips:
		if item[4] == "X":
			pass
		else:
			validZips.append(item)

	zipsPure = [[j[0], j[1], j[13], j[14]] for j in validZips]
	return zipsPure

def get_random_color(pastel_factor = 0.5):
	return [(x+pastel_factor)/(1.0+pastel_factor) for x in [random.uniform(0,1.0) for i in [1,2,3]]]

def color_distance(c1,c2):
	return sum([abs(x[0]-x[1]) for x in zip(c1,c2)])

def generate_new_color(existing_colors,pastel_factor = 0.5):
	max_distance = None
	best_color = None
	for i in range(0,100):
		color = get_random_color(pastel_factor = pastel_factor)
		if not existing_colors:
			return color
		best_distance = min([color_distance(color,c) for c in existing_colors])
		if not max_distance or best_distance > max_distance:
			max_distance = best_distance
			best_color = color
	return best_color

def genColors(n):
	if __name__ == '__main__':
	  #To make your color choice reproducible, uncomment the following line:
	  random.seed(10)
	  colors = []
	  for i in range(0,n):
		  colors.append(generate_new_color(colors,pastel_factor = 0.9))    
	  return colors

def showRouteMap(drayageRoutes, saveFileName='DrayageMap.html'):
	#progress = csvToListOfRowLists("C:\\Users\\sean.hartrich\\Downloads\\zip3GoogleMapsPathMiles.csv")
	#LTLout = loadLTLRoutes()

	drayageZips = [d.zipSequence for d in drayageRoutes]
	#print (drayageZips)
	zips = loadMajorZips()


	sets = []
	citySet = []
	

	coorDict = {}
	for row in zips:
		coorDict[zipSwitcher(row[0])] = (row[2], row[3])

	for route in drayageZips:
		temp = []
		cities = []
		route2 = route[1:]
		try:
			for idx, zip in enumerate(route2):
				#temp.append((coorDict[route[idx]], coorDict[zip]))
				city1 = coorDict[route[idx]]
				temp.append((city1, coorDict[zip]))
				cities.append(city1)
			sets.append(temp)
			citySet.append(cities)
		except:
			print("Error on mapping zip:", route[idx], "to", zip)
		

	colorRatios = genColors(len(sets))
	colors = ['#%02x%02x%02x' % (round(255*x[0]), round(255*x[1]), round(255*x[2])) for x in colorRatios]

	try:
		gmap = gmplot.gmplot.GoogleMapPlotter.from_geocode("United States", zoom = 4.5)
	except:
		print("Error on mapping. Trying again...")
		gmap = gmplot.gmplot.GoogleMapPlotter.from_geocode("United States", zoom = 4.5)

	
	for idx, route in enumerate(sets):
		for item in route:
			

			pathLat = [float(item[0][0]), float(item[1][0])]
			pathLon = [float(item[0][1]), float(item[1][1])]        

			gmap.plot(pathLat, pathLon, colors[idx], edge_width=2)

	for idx, cities in enumerate(citySet):  
		for idx2, item in enumerate(cities):
			pathLat = [float(item[0])]
			pathLon = [float(item[1])]

			#print(pathLat, pathLon)
			gmap.scatter(pathLat, pathLon, color = colors[idx], size = 100*idx2)
			#gmap.scatter(pathLat, pathLon, color = colors[idx], size = 20*(idx2+1))
			
	
	gmap.draw('DrayageMap.html')
'''

# Read In the Drayage Data .csv file as a LIST 
def readCSV(csvFile):
	with open(csvFile, 'r') as f:
		reader = csv.reader(f)
		data = list(reader)
	return data

# Output the distance (road, air, or both) between two ZipCodes
## To Do: Add Canadian ZipCodes and more accurate Distances
def distRef():
	# Create matrix with all the distances between the most used 3-digit zip codes 
	global distanceMatrix
	distanceMatrix = readCSV('matrixOfRealDistances.csv')

	headerRow = distanceMatrix[0][1:]

	distanceDict = {}

	# Find ZipCodes non-existent in the matrix and assign error.
	for a in range(1,1000):
		zipA = zipSwitcher(a)
		distanceDict[(zipA, 'ZipError')] = 999999
		distanceDict[('ZipError', zipA)] = 999999
		# Remove duplicates (Remove keys that have the same (toZip, fromZip): value
		for b in range(1,1000):
			distanceDict[(zipA, zipSwitcher(b))] = 999999
	distanceDict[('ZipError', 'ZipError')] = 999999
	# for z in headerRow:
	#     distanceDict[('ZipError', z)] = 999999
	#     distanceDict[(z, 'ZipError')] = 999999
	# Out distance b/w ZipCodes

	# Assign value to each (fromZip, toZip): distance value
	distanceRows = distanceMatrix[1:] 
	#for row in distanceMatrix:
	for row in distanceRows:
		#fromZip = row[0]
		fromZip = zipSwitcher(row[0])
		modifiedRow = row[1:]

		# Assign distance value between fromZip and toZip
		for colNum, item in enumerate(modifiedRow):
			toZip = zipSwitcher(headerRow[colNum])
			distanceDict[(fromZip, toZip)] = int(float(item))

	
	return distanceDict

# Assigns a 3-Digit Standard ZipCode 
def zipSwitcher(integer):

	switcher = {
		1: "00",
		2: "0",
		3: ""
		}

	s = str(integer)

	return switcher.get(len(s)) + s

class tripObject:
	#def __init__(self, startZip, endZip, miles, pallets):
	def __init__(self, loadID, portZip, clientZip, shipDate, delivDate, impExp, steamShipLine, equipment, dateLimit, tertiaryDate, portCity = "?", clientCity = "?"):
		#self.zipSequence = [origin, destination]
		#self.dateSequence = [shipDate, delivDate]
		#self.palletSequence = [palletQuantity]

		self.impExp = impExp
		self.steamShipLine = steamShipLine

		self.loadID = loadID
		self.equipment = equipment
		self.dateLimit = dateLimit
		#
		# if self.dateLimit[:3] == "CUT":
		#     print(self.dateLimit)

		self.shipDate = shipDate
		self.delivDate = delivDate

		self.tertiaryDate = tertiaryDate
		
		#self.startDate = shipDate  #will need to be flexible in final model
		#self.endDate = delivDate   #will need to be flexible in final model

		if impExp == "EXPORT":
			self.origin = clientZip 
			self.destination = portZip
			self.originCity = clientCity
			self.destinationCity = portCity
			# Built ERD from CUT 
			if self.dateLimit[:3].upper() == "CUT":
				try:
					# Grab the date in string form and convert to date format
					for s in self.dateLimit[-5:].split():
						# print(s)
						if len(s) >= 2:
							# OCEAN CASE (4 days b/w ETA and LFD)
							self.CUT = pd.to_datetime(s, format='%m/%d')
							self.ERD = pd.to_datetime(s, format='%m/%d') - pd.Timedelta(4, unit='d')
							print (self.CUT)								
				except:
					pass
			# Build CUT from ERD
			elif self.dateLimit[:3].upper() == "ERD":
				# print (self.dateLimit)
				try:
					# Grab the date in string form and convert to date format
					for s in self.dateLimit[-5:].split():
						#print(s)
						if len(s) >= 2:
							# OCEAN CASE (4 days b/w ETA and LFD)
							self.CUT = pd.to_datetime(s, format='%m/%d') + pd.Timedelta(4, unit='d')
							self.ERD = pd.to_datetime(s, format='%m/%d') 
							# print (self.ETA)
							# print (self.LFD)								
				except:
					pass


		elif impExp == "IMPORT":
			self.origin = portZip
			self.destination = clientZip
			self.originCity = portCity
			self.destinationCity = clientCity
			# Built LFD from ETA 
			if self.dateLimit[:3].upper() == "ETA":
				try:
					# Grab the date in string form and convert to date format
					for s in self.dateLimit[-5:].split():
						# print(s)
						if len(s) >= 2:
							# OCEAN CASE (4 days b/w ETA and LFD)
							self.ETA = pd.to_datetime(s, format='%m/%d')
							self.LFD = pd.to_datetime(s, format='%m/%d') + pd.Timedelta(4, unit='d')
							# print (self.ETA)								
				except:
					pass
			# Build ETA from LFD
			elif self.dateLimit[:3].upper() == "LFD":
				# print (self.dateLimit)
				try:
					# Grab the date in string form and convert to date format
					for s in self.dateLimit[-5:].split():
						#print(s)
						if len(s) >= 2:
							# OCEAN CASE (4 days b/w ETA and LFD)
							self.ETA = pd.to_datetime(s, format='%m/%d') - pd.Timedelta(4, unit='d')
							self.LFD = pd.to_datetime(s, format='%m/%d') 
							# print (self.ETA)
							# print (self.LFD)								
				except:
					pass

		else:
			#print("Error")
			#print(self.loadID)
			self.origin = "ZipError"
			self.destination = "ZipError" 
			self.originCity = "portCity" 
			self.destinationCity = "clientCity"

		self.possibleRoutes = []
  
		try:
			self.distance = distanceReferences[(self.origin, self.destination)]
		except:
			pass

	def printTop10Routes(self):
		if len(self.possibleRoutes) > 0:
			self.sortPossibleRoutes()

			for i in range(0, 2):
				print("Route:", i + 1)
				self.possibleRoutes[i].printRoute()
				print()
	
	def returnTopRoute(self):
		if len(self.possibleRoutes) > 0:
			self.sortPossibleRoutes()
			#matchedItems.append(self.possibleRoutes[0])
			return self.possibleRoutes[0]

	def sortPossibleRoutes(self):
		tempList = self.possibleRoutes[:]

		data = [(route, route.deadHead) for route in tempList]
		temp = sorted(data,key=itemgetter(1))

		self.possibleRoutes = [route[0] for route in temp]
		

	def printTrip(self):
		#print('Route begins:', self.startDate, 'in', self.origin)
		#print('Route ends:', self.endDate, 'in', self.destination)

		print(" ", self.originCity, 'to', self.destinationCity)
		print("    Load:", self.loadID, \
			"\n    Type:", self.impExp, \
			"\n    Origin:", self.origin, "on ?", #self.shipDate.strftime('%m/%d/%Y'),\
			"\n    Destination:", self.destination, "on", self.delivDate.strftime('%m/%d/%Y'), \
			"\n    Steamship:", self.steamShipLine, \
			"\n    Equipment:", self.equipment, \
			"\n    Miles:", self.distance)

	def findRoute(self, testTrips):

		if self.impExp == "IMPORT":
			self.findExport(testTrips)
		elif self.impExp == "EXPORT":
			self.findImport(testTrips)
		
		try:
			if len(self.possibleRoutes) > 0:
				#for route in self.possibleRoutes:
					#bigRoutesList.append(route)
				topRoute = self.returnTopRoute()
				bigRoutesList.append(topRoute)
				matchedItems.append(topRoute.importTrip)
				matchedItems.append(topRoute.exportTrip)


		except:
			print("No matching routes")

	# For an import find a matching export
	def findExport(self, testTripSet):	
		possibleRoutes = []
		for testTrip in testTripSet:
			# Match steamShipLine
			if self.steamShipLine == testTrip.steamShipLine:
				 # Match Port cities
				if self.origin == testTrip.destination:
					# Match Import with Export only
					if testTrip.impExp == "EXPORT":
						#if self.delivDate <= testTrip.shipDate and testTrip.shipDate <= self.delivDate + pd.Timedelta(7, unit='d'):
						if self.delivDate in pd.date_range(testTrip.delivDate - pd.Timedelta(2, unit='d'),testTrip.delivDate + pd.Timedelta(2, unit='d')):
							# Match Equipment
							if self.equipment == testTrip.equipment:
								if not testTrip in matchedItems:
									# deadHead is distance from Import Drop-Off to Export Pick-Up
									deadHead = distanceReferences[(self.destination, testTrip.origin)]
									# Comparative is distance from Import pick-up to drop-off plus Export pick-up to drop-off
									comparative = distanceReferences[(testTrip.origin, testTrip.destination)] + distanceReferences[(self.origin, self.destination)]

									if deadHead <= comparative:
										newRoute = routeObject(importTrip = self, exportTrip = testTrip, deadHead = deadHead)
										self.possibleRoutes.append(newRoute)

	# For an export find a matching import									
	def findImport(self, testTripSet):
		possibleRoutes = []
		for testTrip in testTripSet:
			# Match steamShipLine
			if self.steamShipLine == testTrip.steamShipLine:
				# Match Port cities
				if self.destination == testTrip.origin:
					# Match Export with Import only
					if testTrip.impExp == "IMPORT":
					#if self.shipDate >= testTrip.delivDate and testTrip.delivDate + pd.Timedelta(7, unit='d') >= self.shipDate:
						if testTrip.delivDate in pd.date_range(self.delivDate - pd.Timedelta(2, unit='d'), self.delivDate + pd.Timedelta(2, unit='d')):
							# Match Equipment
							if self.equipment == testTrip.equipment:
								if not testTrip in matchedItems:
									# deadHead is distance from Import Drop-Off to Export Pick-Up
									deadHead = distanceReferences[(self.origin, testTrip.destination)]
									# Comparative is distance from Import pick-up to drop-off plus Export pick-up to drop-off
									comparative = distanceReferences[(testTrip.origin, testTrip.destination)] + distanceReferences[(self.origin, self.destination)]

									if deadHead <= comparative:
										newRoute = routeObject(importTrip = testTrip, exportTrip = self, deadHead = deadHead)
										self.possibleRoutes.append(newRoute)
		
class routeObject:
	#def __init__(self, zipSequence, dateSequence, palletVolumeSequence):
	#def __init__(self, origin, destination, shipDate, delivDate, palletQuantity):
	def __init__(self, importTrip, exportTrip, deadHead):
		self.importTrip = importTrip
		self.exportTrip = exportTrip
		self.deadHead = deadHead

		if self.importTrip.delivDate <= self.exportTrip.delivDate:
			self.startDate = self.importTrip.shipDate
			self.endDate = self.exportTrip.delivDate
			self.zipSequence = [self.importTrip.origin, self.importTrip.destination, self.exportTrip.origin, self.exportTrip.destination, self.importTrip.origin]

		elif self.importTrip.delivDate > self.exportTrip.delivDate:
			self.startDate = self.exportTrip.shipDate
			self.endDate = self.importTrip.shipDate
			self.zipSequence = [self.exportTrip.origin, self.exportTrip.destination, self.importTrip.origin, self.importTrip.destination, self.exportTrip.origin]


	def printRoute(self):
		print("ImportTrip:")
		self.importTrip.printTrip()

		print()

		print("ExportTrip:")
		self.exportTrip.printTrip()

		print("DeadHead Miles:", self.deadHead)
		print("\n")


def loadDataFrame(csvFile = "DrayageTestRun.csv"):
	# Use Panda package to load csv file as a dataFrame object
	dataFrame = pd.read_csv(csvFile, encoding = "ISO-8859-1") #adjust encoding as necessary
	
	dataFrame['ShipZip3'] = dataFrame['Ship Zip'].apply(addZip3)
	dataFrame['ConsZip3'] = dataFrame['Con Zip'].apply(addZip3)

	try:
		dataFrame['ShipDate'] = pd.to_datetime(dataFrame['Ship Date'], format='%m/%d/%Y')
		dataFrame['DelivDate'] = pd.to_datetime(dataFrame['Deliv Date'], format='%m/%d/%Y')

	except:
		dataFrame['ShipDate'] = pd.to_datetime(dataFrame['Ship Date'])
		dataFrame['DelivDate'] = pd.to_datetime(dataFrame['Deliv Date'])

	return dataFrame

# Assigns a 3-Digit Standard ZipCode
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

def fromDistance(baseZip3, zip3):
	return distanceReferences[(baseZip3, zip3)]

def dataFrameToTripList(df):
	trips = []
	items = len(df)

	for idx in range(0, items):
		row = df.ix[idx]
		#print(row)

		city1 = str(row['Ship City']) + ', ' + str(row['Ship State'])
		city2 = str(row['Cons City']) + ', ' + str(row['Cons State'])

		try:
			temp = tripObject(row['Id'], row['ShipZip3'], row['ConsZip3'], row['ShipDate'], row['DelivDate'], row['UPPER([Truck Number])'], row['UPPER([Driver])'], row['Equipment'], row['Trailer Number'], city1, city2)

		except:
			temp = tripObject(row['Id'], row['ShipZip3'], row['ConsZip3'], row['ShipDate'], row['DelivDate'], row['Truck Number Upper'], row['BL Line Agg'], row['Equipment Upper'], row['Trailer Number'], city1, city2)

		trips.append(temp)

	return trips


def masterRouteListSorter(routeList):
	tempList = routeList[:]

	data = [(route, route.deadHead) for route in tempList]
	temp = sorted(data,key=itemgetter(1))

	return[route[0] for route in temp]

def main():
	start = time.time()
	#df = loadDataFrame()
	df = loadDataFrame("marchDrayageRun.csv")
	#df = loadDataFrame("januaryDrayage.csv")
	tripList = dataFrameToTripList(df)

	
	print("Data loaded in", round(time.time() - start, 1), "seconds")
	print("Algorithm begins now...\n")
	#sampleTest = original[:]
	#sampleBlock = original[:]


	for idx, row in enumerate(tripList):
		#print("Testing Load:", sampleTest[idx].loadID)
		if not row in matchedItems:
			row.findRoute(tripList)

	dataOut = masterRouteListSorter(bigRoutesList)

	# for route in dataOut[:10]:
	# 	route.printRoute()

	print(len(dataOut), "possible best routes for", len(tripList), "shipments.")

	# for idx1, route1 in enumerate(bigRoutesList):
	# 	for idx2, route2 in enumerate(bigRoutesList):
	# 		if route1 == route2 and idx1 != idx2:
	# 			print("DUPLICATE ROUTE:")
	# 			print(idx1)
	# 		elif route1.importTrip == route2.importTrip and idx1 != idx2:
	# 			print("DUPLICATE IMPORT TRIP:")
	# 			route1.importTrip.printTrip()
	# 		elif route1.exportTrip == route2.exportTrip and idx1 != idx2:
	# 			print("DUPLICATE EXPORT TRIP:")
	# 			route1.exportTrip.printTrip()

	print("END OF ROUTE MATCHING")

global distanceReferences
distanceReferences = distRef()

global bigRoutesList 
bigRoutesList = []


global matchedItems
matchedItems = []
main()

#showRouteMap(bigRoutesList)
