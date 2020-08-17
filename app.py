###################################################################################################
# Climate App
#
#   Now that you have completed your initial analysis, design a Flask api 
#   based on the queries that you have just developed.
#
#      * Use FLASK to create your routes.
#
#   Routes
#
#       * `/api/v1.0/precipitation`
#           * Query for the dates and precipitation observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#           * Return the json representation of your dictionary.
#       * `/api/v1.0/stations`
#           * Return a json list of stations from the dataset.
#       * `/api/v1.0/tobs`
#           * Return a json list of Temperature Observations (tobs) for the previous year
#       * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
#           * Return a json list of the minimum temperature, the average temperature, and
#               the max temperature for a given start or start-end range.
#           * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates 
#               greater than and equal to the start date.
#           * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` 
#               for dates between the start and end date inclusive.
###################################################################################################

import numpy as np
import datetime
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request
import pandas as pd
#################################################
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
    """List all available api routes."""
    return (
        f"Available Routes:<br/><br/>"

        f"<a href='/api/v1.0/precipitation'>List of precipitation</a>"
        f"<br/>"
        f"<br/>"

        f"<a href='/api/v1.0/stations'>List of Station numbers and names</a>"
        f"<br/>"
        f"<br/>"

        f"<a href='/api/v1.0/tobs'>List of prior year(2017) temperatures from all stations</a>"        
        f"<br/>"
        f"<br/>"
        
        # f"Input start date, show the MIN/AVG/MAX temperature after your input date<br/>"
        #  f'<div class="container"> \
        #     <form name="task_form" method="post" action="/api/v1.0/">\
        #         Start Date: <input type="date" name="start_date" placeholder="start date" value="2017-01-01"/>\
        #         <input type="submit" name="task_submit" value="Submit"/>\
        #     </form>\
        # </div>'

        f"Input start date and end date , show the MIN/AVG/MAX temperature between your input start date and end date<br/>"
        f'<div class="container"> \
            <form name="task_form" method="post" action="/api/v1.0/">\
                Start Date: <input type="date" name="start_date" placeholder="start date" value="2015-01-01"/>\
                End Date: <input type="date" name="end_date" placeholder="end date" value="2017-01-01"/>\
                <input type="submit" name="task_submit" value="Submit"/>\
            </form>\
        </div>'






    )

#########################################################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)    
    # * Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    results = session.query(Measurement.date,Measurement.prcp).all()
    session.close()
    all_date_precipitation = []

    # Create a list of dicts with `date` and `precipitation` as the keys and values
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["precipitation"] = prcp
        all_date_precipitation.append(precipitation_dict)
    
    # * Return the JSON representation of your dictionary.
    return jsonify(all_date_precipitation)

#########################################################################################
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Station.station,Station.name).distinct().all()
    session.close()
    #create dataframe and return dictionary
    stations = pd.DataFrame(results)
    return jsonify(stations.to_dict())
#   * Return a JSON list of stations from the dataset.
#########################################################################################

@app.route("/api/v1.0/tobs")
def tobstest():
    # Create our session (link) from Python to the DB
    # Query the dates and temperature observations of the most active station for the last year of data.
    # obtain the most active station in 2017
    session = Session(engine)
    most_active_station= session.query(Measurement.station,func.count(Measurement.station)\
                    ).group_by(Measurement.station)\
                    .filter(Measurement.date>= datetime.datetime.strptime("2017-01-01", '%Y-%m-%d').date())\
                    .filter(Measurement.date<= datetime.datetime.strptime("2017-12-31", '%Y-%m-%d').date())\
                    .order_by(func.count(Measurement.station).desc()).all()
  # obtain the dates and temperature observations of the most active station in 2017
    results= session.query(Measurement.tobs, Measurement.date\
                    ).filter(Measurement.date>= datetime.datetime.strptime("2017-01-01", '%Y-%m-%d').date())\
                    .filter(Measurement.date<= datetime.datetime.strptime("2017-12-31", '%Y-%m-%d').date())\
                    .filter(Measurement.station==most_active_station[0][0]).all()

    session.close()

# Create a list of dicts with `date` and `temperature` as the keys and values
    all_date_tobs = []
    for tobs, date in results:
        temperature_dict = {}
        temperature_dict["date"] = date
        temperature_dict["temperature"] = tobs
        all_date_tobs.append(temperature_dict)


    station_dict = {}
    station_dict["Station"] = most_active_station[0][0]
    station_dict["tob"] = all_date_tobs
    #* Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify([station_dict])

#########################################################################################
@app.route("/api/v1.0/1/", methods=['GET', 'POST'])
def startdate():
    # Handle POST request
    # Get form data
    date = request.form['start_date']

        # Create our session (link) from Python to the DB
    try:
        # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

        startDate = datetime.datetime.strptime(date, '%Y-%m-%d')
        session = Session(engine)
        results= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)\
                    ).filter(Measurement.date >= startDate).all()
        session.close()
        if  isinstance(results[0][0], float):
        # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
            return "Hawaii climate record after date:{d} <br/>Min temperature: {a}<br/> Average temperature: {b}<br/> Max temperature: {c}"\
                .format(a= round(results[0][0],2), b = round( results[0][1],2), c = round( results[0][2],2), d = date)
        else:
            return f"No data after the {date}<br/>"
    
    except ValueError:
        #raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return f"Incorrect data format, should be YYYY-MM-DD<br/>"
    return jsonify({"error": f"Character with real_name {real_name} not found."}), 404
#########################################################################################

@app.route("/api/v1.0/", methods=['GET', 'POST'])
def startenddate():
    # Create our session (link) from Python to the DB

    startdate_post = request.form['start_date']
    enddate_post = request.form['end_date']

    try:
        #  When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

        startDate = datetime.datetime.strptime(startdate_post, '%Y-%m-%d')
        endate = datetime.datetime.strptime(enddate_post, '%Y-%m-%d')

        if startDate > endate:
            return f"Input error, the end date is earlier than start date<br/>"
        session = Session(engine)
        results= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)\
                    ).filter(Measurement.date >= startDate.date())\
                    .filter(Measurement.date <= endate.date()).all()
        session.close()
        if  isinstance(results[0][0], float):
        # * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

            return "Hawaii climate record from date:{d} to date: {e} <br/>Min temperature: {a}<br/> Average temperature: {b}<br/> Max temperature: {c}"\
                .format(a= round(results[0][0],2), b = round( results[0][1],2),\
                     c = round( results[0][2],2), d = startdate_post, e = enddate_post)
        else:
            return f"No data between {startdate_post} and {enddate_post} <br/>"
    
    except ValueError:
        #raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return f"Incorrect data format, should be YYYY-MM-DD<br/>"
    return jsonify({"error": f"Character with real_name {real_name} not found."}), 404



if __name__ == '__main__':
    app.run(debug=True)
