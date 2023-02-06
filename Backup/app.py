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
        f"List of all Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
        f"<br/>"
        f"<br/>"
        f"IMPORTANT NOTES:<br/>"
        f"<br/>"
        f"For the route: /api/v1.0/<start> , Please replace <start> with the desired date in (YYYY-MM-DD) ISO date format <br/>"
        f"Example:/api/v1.0/2016-01-01 <br/>"           
        f"For the route: /api/v1.0/<start>/<end> , Please replace <start> and <end> with the desired date in (YYYY-MM-DD) ISO date format <br/>"        
        f"Example:/api/v1.0/2016-01-01/2016-01-11 <br/>"                 
        f"Start date and end date should not be less than 2010-01-01 and later than 2017-08-23."
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all precipitation data for last year dates
    date_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_year_ago).order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_date_prcp
    all_date_prcp = []
    for date,prcp in results:
        all_date_prcp_dict = {}
        all_date_prcp_dict["Date"] = date
        all_date_prcp_dict["Precipitation"] = prcp
        all_date_prcp.append(all_date_prcp_dict)

    # return the list in json using jsonify
    return jsonify(all_date_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations data
    results = session.query(Station.station, Station.name).filter().all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station,name in results:
        all_stations_dict = {}
        all_stations_dict["Stations"] = station
        all_stations_dict["Name"] = name
        all_stations.append(all_stations_dict)

    # return the list in json using jsonify
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all tobs data for the most active station and last year dates

    # Calculate the date one year from the last date in data set.
    # recent_dates = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # print(recent_dates) --> result = ('2017-08-23',)

    date_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # active_station_id = session.query(Measurement.station).\
    #                 group_by(Measurement.station).\
    #                 order_by(func.count(Measurement.station).desc()).first()
    # active_station_id --> result : ('USC00519281')
    
    results =   session.query(Measurement.date, Measurement.tobs, Measurement.station).\
                filter(Measurement.date >= date_year_ago, Measurement.station == 'USC00519281').\
                order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    tobs_date_list = []
    for date, tobs,station in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_dict["Station"] = station
        tobs_date_list.append(tobs_dict)

    # return the list in json using jsonify
    return jsonify(tobs_date_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query start date
    results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.max(Measurement.tobs), \
                                func.avg(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        group_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of start_date_List
    start_date_list = []
    for date, min, max, avg in results:
        start_date_dict = {}
        start_date_dict["Date"] = date
        start_date_dict["TMin"] = min
        start_date_dict["TMax"] = max
        start_date_dict["Tavg"] = avg
        start_date_list.append(start_date_dict)

    # return the list in json using jsonify
    session.close()    

    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query Start Date / End Date
    results =   session.query( Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.max(Measurement.tobs), \
                                func.avg(Measurement.tobs)).\
                        filter(Measurement.date >= start, Measurement.date <= end).\
                        group_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of start_end_date_List
    start_end_date_List = []
    for date, min, max, avg in results:
        start_end_date_dict = {}
        start_end_date_dict["Date"] = date
        start_end_date_dict["TMin"] = min
        start_end_date_dict["TMax"] = max
        start_end_date_dict["Tavg"] = avg
        start_end_date_List.append(start_end_date_dict)

    session.close()    
     
    # return the list in json using jsonify
    return jsonify(start_end_date_List)

if __name__ == '__main__':
    app.run(debug=True)
