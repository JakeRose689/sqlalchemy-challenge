import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
import datetime as dt
import numpy as np

# Database
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement=Base.classes.measurement
Station=Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app=Flask(__name__)

# Flask Routes
@app.route('/')

def home():
    session = Session(engine)
    
    prev_date=dt.date(2017,8,23)-dt.timedelta(days=365)
    last_date=dt.date(2017,8,23)
    
    session.close()

    return (f"Welcome to your vacation planning weather advisor!<br/>"
          f"Available routes:<br/>"
          f"/api/v1.0/precipitation<br/>"
          f"/api/v1.0/stations<br/>"
          f"/api/v1.0/tobs<br/>"
          f"/api/v1.0/start/<br/>"
          f"/api/v1.0/start/end<br/>")
  
@app.route('/api/v1.0/precipitation')
def precipitation():
    
    #Creating a calculated field for one full previous year's worth of data.
    prev_date=dt.date(2017,8,23)-dt.timedelta(days=365)

    # Gathering date and precip values.
    precip=session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>prev_date).all()
    
    precipitation=[]

    for prcp, date in precip:
        precipitationDict={}
        precipitationDict['prcp']=prcp
        precipitationDict['date']=date
        precipitation.append(precipitationDict)

    session.close()
    
    all_dates = list(np.ravel(precipitation))

    return jsonify(all_dates)

@app.route('/api/v1.0/stations')
def stations():

    # Perform a query to all of the stations
    stations=session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(stations))

    return jsonify(stations=stations)

@app.route('/api/v1.0/tobs')
def tobs():

    #Same code as above, to set the date 1 year before the last measurement.
    prev_date=dt.date(2017,8,23)-dt.timedelta(days=365)
    
    # Querying for temperature and date
    temps=session.query(Measurement.tobs,Measurement.date).filter(Measurement.station=='USC00516128').filter(Measurement.date>prev_date).all()
    
    tobs_data=[]

    for tobs, date in temps:
        dict1={}
        dict1['tobs']=tobs
        dict1['date']=date
        tobs_data.append(dict1)
 
    session.close()

    tobs_result=list(np.ravel(tobs_data))

    return jsonify(tobs_result=tobs_result)

@app.route('/api/v1.0/<start_date>')
def start(start_date=None):

    sel=[func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]

    results=session.query(*sel).filter(Measurement.date>=start_date).all()
   
    temperatures=[]
    for TMIN, TMAX, TAVG in results:
        dict2={}
        dict2['Date_Start']=start_date
        dict2['TMIN']=TMIN
        dict2['TMAX']=TMAX
        dict2['TAVG']=TAVG
        temperatures.append(dict2)

    session.close()
        
    return jsonify(temperatures)

@app.route('/api/v1.0/<start_date>/<end_date>')
def start_end(start_date=None,end_date=None):

    sel=[func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]

    results=session.query(*sel).filter(Measurement.date>=start_date).filter(Measurement.date<=end_date).all()
   
    temp_range=[]
    for TMIN, TMAX, TAVG in results:
        dict3={}
        dict3['Date_Start']=start_date
        dict3['Date_End']=end_date
        dict3['TMIN']=TMIN
        dict3['TMAX']=TMAX
        dict3['TAVG']=TAVG
        temp_range.append(dict3)

    session.close()

    return jsonify(temp_range)

if __name__ == '__main__':
    app.run()