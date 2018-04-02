from sqlalchemy import create_engine
engine = create_engine("mysql://sql9229495:2JAaltxk9J@sql9.freemysqlhosting.net/sql9229495", encoding='latin1', echo=True)

qryStr = "SHOW COLUMNS FROM sql9229495.drayage_march"

conn = engine.connect() # connect to database
query = conn.execute(qryStr)
a = query.fetchall()

print(a)