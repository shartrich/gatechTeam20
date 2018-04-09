
from sqlalchemy import create_engine
import pandas as pd

defaults = {}
defaults['server'] = "sql9.freemysqlhosting.net"
defaults['name'] = "sql9231477"
defaults['username'] = "sql9231477"
defaults['password'] = "fhGB7MNW5I"
defaults['table'] = "drayage_march"



result = {'data': [dict(zip(tuple (defaults.keys()) , i)) for i in defaults]}

print(result)




loadID =  1421466
dataTable =  defaults['table'] = "drayage_march"


#determine defaults for MySQL connection
server =  defaults['server']
name = defaults['name']
username =  defaults['username']
password =  defaults['password']





engineString = "mysql://" + username + ":" + password + "@" + server + "/" + name

print(engineString)
print("mysql://sql9229495:2JAaltxk9J@sql9.freemysqlhosting.net/sql9229495")



def matchMaker():
    #single input var is integer loadID, use SQL to return trip data items
    loadID =  1421466
    dataTable =  defaults['table']
    

    #determine defaults for MySQL connection
    server =  defaults['server']
    name = defaults['name']
    username =  defaults['username']
    password =  defaults['password']


    #construct ssh connection with 
    engineString = "mysql://" + username + ":" + password + "@" + server + "/" + name
    #engine = create_engine("mysql://sql9229495:2JAaltxk9J@sql9.freemysqlhosting.net/sql9229495", encoding='latin1', echo=True)

    engine = create_engine(engineString, encoding='latin1', echo=True)

    #query to look into target trip
    firstQuery = "SELECT * from %s where ID = %s"  %(dataTable, loadID)
    

    #return SQL query as pandas table
    conn = engine.connect()
    focusLoad = pd.read_sql_query(firstQuery, conn)
    conn.close()

    print(focusLoad)
    #declare all needed values of trip
    loadType = focusLoad['UPPER[Truck_Number]'].values[0]
    steamShipLine = focusLoad['UPPER[Driver]'].values[0]
    clientCity = focusLoad['Con_Zip'].values[0]
    shipCity = focusLoad['Ship_Zip'].values[0]
    equipment = focusLoad['Equipment'].values[0]
    rawInput = focusLoad['Trailer_Number'].values[0]


