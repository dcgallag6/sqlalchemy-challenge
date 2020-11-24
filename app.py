# Dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table

Measurement = Base.classes.measurement
Station = Base.classes.station

# Set up start and end dates using time delta

session = Session(engine)

last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

query_date= dt.date(2017,8,23) - dt.timedelta(days=365)

session.close()

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
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return dictionary of precipitation data"""
    # Query all precipation data
    prcp_results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary using date as key and prcp as value; return JSON representation
    prcp_data = []
    for date, prcp in prcp_results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

#################################################

@app.route('/api/v1.0/stations')
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Return a JSON list of stations from the dataset.
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]

    station_results = session.query(*sel).all()

    session.close()

    # Return a JSON list of stations from the dataset.
    stations_data = []
    for station, name, lat, lon, el in station_results:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations_data)

#################################################

@app.route('/api/v1.0/tobs')
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query the dates and temperature observations of the most active station for the last year of data (8/23/2016).
    
    tobs_result = session.query(Measurement.tobs, Measurement.date).filter(Measurement.date >= query_date).all()

    session.close()

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    tobs_data = []
    for date, tobs in tobs_result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

#################################################

@app.route('/api/v1.0/<start>')
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Convert date to yyyy-mm-dd format
    start_date= dt.datetime.strptime(start, "%Y-%m-%d")

    # Given the start only: calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

    start_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    session.close()
    
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    tobs_start_data = []
    for min,avg,max in start_query:
        tobs_dict2 = {}
        tobs_dict2["Minimum Temp"] = min
        tobs_dict2["Average Temp"] = avg
        tobs_dict2["Maximum Temp"] = max
        tobs_start_data.append(tobs_dict2)

    return jsonify(tobs_start_data)

#################################################

@app.route('/api/v1.0/<start>/<stop>')
def start_end(start,stop):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Convert dates to yyyy-mm-dd format
    start_date= dt.datetime.strptime(start, "%Y-%m-%d")
    stop_date= dt.datetime.strptime(end, "%Y-%m-%d")

    # Given start and end dates: calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

    start_stop_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= stop_date)
    
    session.close()
    
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    tobs_start__stop_data = []
    for min,avg,max in start_stop_query:
        tobs_dict3 = {}
        tobs_dict3["Minimum Temp"] = min
        tobs_dict3["Average Temp"] = avg
        tobs_dict3["Maximum Temp"] = max
        tobs_start__stop_data.append(tobs_dict3)

    return jsonify(tobs_start_stop_data)

#################################################

if __name__ == '__main__':
    app.run(debug=True)