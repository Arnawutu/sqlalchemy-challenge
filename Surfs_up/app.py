# Import the dependencies.
from flask import Flask
import numpy as np 
import datetime as dt 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #link session from python to db
    session = Session(engine)
    """Return a List of all the precipitation and dates"""
    # Query all the precipitation and dates
    results = session.query(measurement.date,measurement.prcp).all()

    session.close()

    #Convert the list of tuples into a dictionary
    all_prcp=[]
    for date,prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    #link session from python to db
    session = Session(engine)

    """Return a list of all stations"""
    #query all stations
    results = session.query(station.id,station.station,station.name,station.latitude,station.longitude,station.elevation).all()
    session.close()
    all_station=[]
    for id,station,name,latitude,longitude,elevation in results:
        station_dict={}
        station_dict['Id']=id
        station_dict['station']=station
        station_dict['name']=name
        station_dict['latitude']=latitude
        station_dict['longitude']=longitude
        station_dict['elevation']=elevation
        all_station.append(station_dict)
    return jsonify(all_station)


@app.route("/api/v1.0/tobs")
def tempartureobs():
    #link session from python to db 
    session = Session(engine)

    """Return a list of all temparture observation"""
    #find date 1 year ago from last data point in the database
    results_date=session.query(measurement.date).order_by(measurement.date.desc()).first()
    datestart=list(np.ravel(results_date))[0]
    latest_date=dt.datetime.strptime(datestart,"%Y-%m-%d")
    date_from_lastyear=latest_date-dt.timedelta(days=366)
#query to retrieve the data and precipitation scores
    results=session.query(measurement.date, measurement.tobs).order_by(measurement.date.desc()).\
            filter(measurement.date>=date_from_lastyear).all()
    session.close()
    alltemps=[]
    for tobs,date in results:
        tobs_dict={}
        tobs_dict['date']=date
        tobs_dict['tobs']=tobs
        alltemps.append(tobs_dict)
    return jsonify(alltemps)


#return the min, avg, and max temperatures for date range
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):
    #link session from python to db
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results=session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()
    tempobs={}
    tempobs["Min_Temp"]=results[0][0]
    tempobs["avg_Temp"]=results[0][1]
    tempobs["max_Temp"]=results[0][2]
    return jsonify(tempobs)

@app.route("/api/v1.0/<start>")
def calc_temps_sd(start):
    #link session from python to db
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results=session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start).all()
    session.close()
    tempobs={}
    tempobs["Min_Temp"]=results[0][0]
    tempobs["avg_Temp"]=results[0][1]
    tempobs["max_Temp"]=results[0][2]
    return jsonify(tempobs)
if __name__ == '__main__':
    app.run(debug=True)