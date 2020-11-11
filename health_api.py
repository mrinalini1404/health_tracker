#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#!flask/bin/python
from flask import Flask, render_template,request, redirect, url_for, session,Response
import pymysql
import re
import json
import paho.mqtt.client as paho
import json
import time
from datetime import datetime
import requests 
import json

app = Flask(__name__)
app.secret_key = 'Mrinalini'
def get_db_result(sql):
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='root',
                                 db='healthtracker')
    #print(sql)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
            connection.close()

    except:
        return []

    return result
  
        
def get_db_result_as_dict(sql):
    return dict((x, y) for x, y in get_db_result(sql))

def execute_db(sql):
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='root',
                                 db='healthtracker')
    print(sql)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()
            connection.close()
    except:
        pass


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        sql = "select * from accounts where username = '"+username+"' and password = '"+password+"'";
        account = get_db_result(sql)
        # If account exists in accounts table in out database
        print(account)
        if (account):
            print(account)
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0][0]
            session['username'] = account[0][1]
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)  
     
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


@app.route('/details',methods=['GET', 'POST'])
def details():
   account=[] 
    # Remove session data, this will log the user out
   if request.method == 'POST' and 'id' in request.form: 
       pat_id = request.form['id']
       sql = "select * from details where id = '"+pat_id+"'";
       account = get_db_result(sql)
   # Redirect to login page
   return render_template("details.html", value=account) 

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        sql = "select * from accounts where username = '"+username+"'";
        account = get_db_result(sql)
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            sql = "insert into accounts values(NULL, '"+username+"' , '"+password+"','"+email+"')";
            execute_db(sql)
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


@app.route('/home',methods=['GET'])
def home():
    # Check if user is loggedin
    #Sensor_Data_Handler(myGlobalMessagePayload)
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
        
'''
def on_connect_sensors(client, userdata, flags, rc):
    #print("Connected with result codes {0}".format(str(rc))) 
    client.subscribe("Dialysis_Sensors")
'''
myGlobalMessagePayload={}

def on_message_sensors(client, userdata, msg):
    global myGlobalMessagePayload
    msg.payload = str(msg.payload.decode("utf-8","ignore"))
    myGlobalMessagePayload = json.loads(msg.payload)
    print(myGlobalMessagePayload)
    

'''
def on_connect_status(client2, userdata, flags, rc):
    #print("Connected with result codes {0}".format(str(rc))) 
    client.subscribe("Patient_Status")
'''
PatientDeets={}

def on_message_status(client2, userdata, msg):
    global PatientDeets
    msg.payload = str(msg.payload.decode("utf-8","ignore"))
    PatientDeets = json.loads(msg.payload)
    #print(PatientDeets)

def on_message(mosq, obj, msg):
    #print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    print(0)
    
        
def Sensor_Data_Handler(json_Dict):
    with app.test_request_context():
        Haemoglobin = str(json_Dict['Haemoglobin'])
        Body_Temp = str(json_Dict['Body_Temp'])
        BUN = str(json_Dict['BUN'])
        Liquid_Temp = str(json_Dict['Liquid_Temp'])
        Blood_Pressure = str(json_Dict['Blood_Pressure'])
        Pulse_Oximetry = str(json_Dict['Pulse_Oximetry'])
        Pulse = str(json_Dict['Pulse'])
        Pat_id = str(json_Dict['Patient_ID'])
        time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql="insert into details values ('"+Pat_id+"','"+Haemoglobin+"','"+Body_Temp+"','"+BUN+"','"+Liquid_Temp+"','"+Blood_Pressure+"','"+Pulse_Oximetry+"','"+Pulse+"','"+time+"')"
        execute_db(sql)
    
@app.route('/chart-data')
def chart_data():
    def generate_random_data():
        while True:
            #print(myGlobalMessagePayload) 
            json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'Art_Gas':myGlobalMessagePayload['Art_Gas'],'Haemoglobin':myGlobalMessagePayload['Haemoglobin'],'Body_Temp':myGlobalMessagePayload['Body_Temp'],'BUN':myGlobalMessagePayload['BUN'],'Liquid_Temp':myGlobalMessagePayload['Liquid_Temp'],'Blood_Pressure':myGlobalMessagePayload['Blood_Pressure'],'Pulse_Oximetry':myGlobalMessagePayload['Pulse_Oximetry'],'Pulse':myGlobalMessagePayload['Pulse'],'stat':PatientDeets['stat'],'value':PatientDeets['value']})
            yield f"data:{json_data}\n\n"
            time.sleep(3)
            #print(json_data)
            Sensor_Data_Handler(myGlobalMessagePayload)
    return Response(generate_random_data(), mimetype='text/event-stream')



@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        sql="select * from accounts where id= '"+str(session['id'])+"'"
        account = get_db_result(sql)
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


if __name__ == "__main__":
    
    mqttc = paho.Client()
    mqttc.message_callback_add('health/Dialysis_Sensors', on_message_sensors)
    mqttc.message_callback_add('health/Patient_Status', on_message_status)
    mqttc.on_message = on_message
    mqttc.connect("broker.mqttdashboard.com")
    mqttc.subscribe("health/#")
    mqttc.loop_start()

    app.run(debug=True)
