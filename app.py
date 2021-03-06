import sys
import os
import time
import requests
import psycopg2
import calendar
from datetime import datetime
from joblib import Parallel, delayed
from flask import Flask, render_template, request, jsonify
from applicationinsights.flask.ext import AppInsights

city_id = requests.get("https://www.metaweather.com/api/location/search/?query={}".format('Moscow')).json()[0]['woeid']

num_days = calendar.monthrange(datetime.now().year, datetime.now().month)[1]

days = [('{:04}/{:02}/{:02}/'.format(datetime.now().year, datetime.now().month, day)) for day in range(1, num_days + 1)]

column_names = ["id", "weather_state_name", "wind_direction_compass", "created",
                    "applicable_date", "min_temp", "max_temp", "the_temp"]

db_params = {
    "host": os.getenv('DB_HOST'),
    "database": os.getenv('DB_NAME'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "port": "5432"
}

def get_weather_result(city_id, date):
    url = "https://www.metaweather.com/api/location/{}/{}".format(city_id, date)
    weather_result = requests.get(url)
    return weather_result.json()

def connect(db_params):
    conn = None
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**db_params)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    print("Connection successful")
    return conn

def insert_table():
    try:
        conn = connect(db_params)
        cursor = conn.cursor()
        cursor.execute(""" CREATE TABLE IF NOT EXISTS forecast (id bigint UNIQUE, weather_state_name varchar(45),\
            wind_direction_compass varchar(45), created varchar(45), applicable_date varchar(45), min_temp integer,\
            max_temp integer, the_temp integer); """)
        for date in days:
            result = get_weather_result(city_id, date)
            for item in result:
                sql = """ INSERT INTO forecast VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING; """
                table_data = [item[column] for column in column_names]
                cursor.execute(sql, table_data)
                conn.commit()
    except (Exception, psycopg2.Error) as error:
        print("Failed inserting record into mobile table {}".format(error))
    cursor.close()
    conn.close()


def clean_table():
    try:
        conn = connect(db_params)
        cursor = conn.cursor()
        cursor.execute(""" DELETE FROM public.forecast;  """)
        conn.commit()
    except (Exception, psycopg2.Error) as error:
        print("Failed cleaning data  {}".format(error))
    cursor.close()
    conn.close()


def postgresql_query(conn, select_query):
    cursor = conn.cursor()
    try:
        cursor.execute(select_query)
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return 1
    res = cursor.fetchall()
    cursor.close()
    return res

insert_table()

list_of_date = [item[0] for item in postgresql_query(conn=connect(db_params),
                                                         select_query="""SELECT DISTINCT(applicable_date)"
                                                                 " FROM forecast ORDER BY applicable_date;""")]

azure_appinsights_instrum_key=os.getenv('AZURE_APP_INS_KEY')

app = Flask(__name__)
app.config['APPINSIGHTS_INSTRUMENTATIONKEY'] = azure_appinsights_instrum_key
appinsights = AppInsights(app)

@app.route('/')
def index2():
    return render_template('index.html', list_of_date=list_of_date, azure_appinsights_instrum_key=azure_appinsights_instrum_key)

@app.route('/showalldata', methods=['POST','GET'])
def showalldata():
    conn = connect(db_params)
    sql_query = """ SELECT * FROM forecast ORDER BY created """
    date_weather = postgresql_query(conn, sql_query)
    conn.close()
    return render_template('showalldata.html', date_weather=date_weather)

@app.route('/showbydate', methods=['POST','GET'])
def showbydate():
    select = request.form.get('date_select')
    conn = connect(db_params)
    sql_query = """ SELECT * FROM forecast WHERE applicable_date = '{}' ORDER BY created; """.format(select)
    date_weather = postgresql_query(conn, sql_query)
    conn.close()
    return render_template('showbydate.html', select=select, list_of_date=list_of_date, date_weather=date_weather)

@app.route('/updatedb', methods=['POST','GET'])
def updatedb():
    insert_table()
    return render_template('updatedb.html', list_of_date=list_of_date)

@app.route('/cleandata', methods=['POST','GET'])
def cleandata():
    clean_table()
    return render_template('cleandata.html', list_of_date=list_of_date)

if __name__ == '__main__':
     app.run()
