import flask
from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
#import jsonify
from flask.ext.jsonpify import jsonify
#from flask import jsonify
import pandas as pd


#db_connect = create_engine('sqlite:///chinook.db')
# db_connect = create_engine('sqlite:////home/shartrich/mysite/chinook.db')



app = Flask(__name__)
api = Api(app)

@app.route('/')
def hello_world():
    return 'Welcome to drayage API!'
    
engine = create_engine("mysql://sql9229495:2JAaltxk9J@sql9.freemysqlhosting.net/sql9229495", encoding='latin1', echo=True)

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
    def get(self, city, loadType):
        conn = engine.connect()
        query = conn.execute("select * from drayage_march where Cons_City =%s and `UPPER[Truck_Number]` =%s "  %(city, loadType))




        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)

api.add_resource(cities, '/cities') # Route_1
api.add_resource(loadTest, '/cities/<city>') # Route_3
api.add_resource(loadTest2, '/cities/<city>/<loadType>') # Route_3

#conn = engine.connect()
#df = pd.read_sql_table('drayage_march', conn)




if __name__ == '__main__':
    app.run()
