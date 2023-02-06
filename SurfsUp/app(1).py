import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify

################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    print("List all available api routes.")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
        f"<br/>"
    )

# @app.route("/api/v1.0/precipitation")
# def precipitation():
#     # Create our session (link) from Python to the DB
#     session = Session(engine)

#     # Query for the dates and precipitation values
#     results =   session.query(Measurement.date, Measurement.prcp).\
#                 order_by(Measurement.date).all()

#     # Convert to list of dictionaries to jsonify
#     prcp_date_list = []

#     for date, prcp in results:
#         new_dict = {}
#         new_dict[date] = prcp
#         prcp_date_list.append(new_dict)

#     session.close()

#     return jsonify(prcp_date_list)

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_date_prcp = []
    for date,prcp in results:
        all_date_prcp_dict = {}
        all_date_prcp_dict["Date"] = date
        all_date_prcp_dict["Precipitation"] = prcp
        all_date_prcp.append(all_date_prcp_dict)

    return jsonify(all_date_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all passengers
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Query all stations
    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for station,name in results:
        all_stations_dict = {}
        all_stations_dict["Stations"] = station
        all_stations_dict["Name"] = name
        all_stations.append(all_stations_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # print(recent_date) --> result = ('2017-08-23',)

    # Calculate the date one year from the last date in data set.
    date_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # print("Query Date: ", date_year_ago)
    

    # Get the last date contained in the dataset and date from one year ago
    # last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # last_year_date = (dt.datetime.strptime(last_date[0],'%Y-%m-%d') \
    #                 - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    # Query all passengers
    results =   session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= date_year_ago).\
                order_by(Measurement.date).all()

    session.close()

    # Convert to list of dictionaries to jsonify
    tobs_date_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_date_list.append(tobs_dict)

    return jsonify(tobs_date_list)

@app.route("/api/v1.0/<start>")
def temp_range_start(start):
    """TMIN, TAVG, and TMAX per date starting from a starting date.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    

    # Create our session (link) from Python to the DB
    session = Session(engine)

    return_list = []

    results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    session.close()    

    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start,end):
    """TMIN, TAVG, and TMAX per date for a date range.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    # Create our session (link) from Python to the DB
    session = Session(engine)

    return_list = []

    results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(and_(Measurement.date >= start, Measurement.date <= end)).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    session.close()    

    return jsonify(return_list)

if __name__ == '__main__':
    app.run(debug=True)
