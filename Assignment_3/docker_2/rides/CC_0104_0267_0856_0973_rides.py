import hashlib
import requests
import re
import json
from collections import defaultdict
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from flask import Flask, render_template,jsonify,request,abort,Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from datetime import datetime
#from multiprocessing import Value

import time
#counter = Value('i', 0)
unique_count = 0
app=Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:@localhost/mydatabase'
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'


db = SQLAlchemy(app)



class ride(db.Model):
	__tablename__ = 'rides'
	rideId = db.Column(db.Integer, primary_key=True)
	created_by = db.Column(db.String(50))
	timestamp = db.Column(db.DateTime)
	source = db.Column(db.Integer)
	destination = db.Column(db.Integer)

class ride_users(db.Model):
	__tablename__ = 'ride_users'
	rideId = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), primary_key=True)

db.create_all()


#dictionary containing book names
# and quantities
#URL Routing:



def make_request(url, data, headers, http_method):
	global response
	try:
		if http_method == "POST":
			response = requests.post(url, data = data, headers = headers)
			return response
		elif http_method == "GET":
			response = requests.get(url, data = data, headers = headers)
			return response

	except requests.exceptions.RequestException as e:
		#print(e)
		return None

'''@app.route('/api/v1/count_inc',methods=["GET"])
def get_count():
	global unique_count
	unique_count += 1
	#with counter.get_lock():
        #counter.value += 1
	#unique_count = counter.value
	return jsonify(count=unique_count)'''

@app.route('/api/v1/_count',methods=["GET"])
def get_count():
	global unique_count
	#with counter.get_lock():
        #counter.value += 1
	#unique_count += 1
	#unique_count = counter.value
	res = []
	res.append(unique_count)
	return jsonify(res)


@app.route('/api/v1/_count',methods=["DELETE"])
def reset_count():
	global unique_count
	#with counter.get_lock():
        #counter.value += 1
	unique_count = 0
	#unique_count = counter.value
	return Response(json.dumps({}), 200)


@app.route('/api/v1/rides/count',methods=["GET"])
def count_rides():
	global unique_count
	unique_count += 1
	#new_cur = time.strftime("%Y-%m-%d %H:%M:%S", cur)
	where_clause = "1=1"
	data = json.dumps({"table_name": "rides", "column_names": ["*"], "where": where_clause})
	headers = {'Content-Type': 'application/json'}
	response = make_request('http://127.0.0.1:5000/api/v1/db/read', data, headers, "POST")

	result = response.json()
	r = len(result)
	res = []
	res.append(r)
	return jsonify(res)



@app.route('/api/v1/rides',methods=["POST"])
def create_ride():
	global unique_count
	unique_count += 1
	#{"created_by" : "abcde", "timestamp" : "12-02-2020:32-11-08", "source" : "1", "destination" : "2"}
	'''d = json.dumps({})
	header = {'Content-Type' : 'application/json'}
	resp = make_request('http://127.0.0.1:5000/api/v1/count_inc',d,header,"GET")'''
	try:
		created_by = request.get_json()["created_by"]
		timestamp = request.get_json()["timestamp"]
		source = request.get_json()["source"]
		destination = request.get_json()["destination"]
	except:
		return Response(json.dumps({"result": "Input not in correct format"}), 400)

	where_clause = "username = " + "'" + created_by + "'"
	dt0 = time.strptime(timestamp, "%d-%m-%Y:%S-%M-%H")
	dt = time.strftime("%Y-%m-%d %H:%M:%S", dt0)

	if int(source)>198 or int(source)<1 or int(destination)>198 or int(destination)<1:
		return Response(json.dumps({"result": "Invalid source or destination"}), 400)

	if source == destination:
		return Response(json.dumps({"result": "Source and destination cannot be same"}), 400)

	#data = json.dumps({"table_name" : "user", "column_names" : ["*"] , "where" : where_clause})
	data = json.dumps({})
	#["rideId", "created_by","timestamp","source","destination"]

	headers = {'Content-Type' : 'application/json'}

	response = make_request('http://CC-Rideshare-1938598602.us-east-1.elb.amazonaws.com/api/v1/users', data, headers, "GET")
	
	#print(response)
	if request.method != 'POST' \
						 '':
		return Response(json.dumps({"result": "Invalid method"}), 405)
	elif created_by not in response.text:
		return Response(json.dumps({"result" : "Username not registered"}), 400)
	else:
		headers = {'Content-Type' : 'application/json'}
		data = json.dumps({"table_name" : "rides", "column_names" : ["created_by","timestamp","source","destination"] , "column_values" : [created_by, dt, source, destination], "delete_flag" : "0", "where" : "abcd"})
		#data1 = json.dumps({"table_name": "ride_users", "column_names": ["rideId", "username"], "column_values": [created_by, timestamp, source, destination]})
		write_response = make_request('http://127.0.0.1:5000/api/v1/db/write', data, headers, "POST")
		return Response(json.dumps({"result" : "Ride created"}), 201)


@app.route('/api/v1/rides',methods=["PUT"])
def wrong_method():
	global unique_count
	unique_count += 1
	return Response(json.dumps({"result": "Invalid method"}), 405)





@app.route('/api/v1/rides/<rideId>', methods=["DELETE"])
#postman : 127.0.0.1:5000/api/v1/rides/2
def delete_ride(rideId):
	global unique_count
	unique_count += 1
	where_clause = "rideId = " + "'" + rideId + "'"
	data = json.dumps({"table_name": "rides", "column_names" : ["created_by","timestamp","source","destination"] , "column_values" : ["abcd", "1234", "1", "2"], "where": where_clause, "delete_flag" : "1"})
	headers = {'Content-Type': 'application/json'}
	response = make_request('http://127.0.0.1:5000/api/v1/db/write', data, headers, "POST")

	#print(str(response))
	if str(response) == "<Response [400]>":
		return Response(json.dumps({"result": "Ride does not exist"}), 400)
	elif str(response) == "<Response [200]>":
		return Response(json.dumps({"result": "Deletion successful"}), 200)


@app.route('/api/v1/db/clear', methods=["POST"])
#postman : 127.0.0.1:5000/api/v1/rides/2
def clear_db():
	#global unique_count
	#unique_count += 1
	'''where_clause = "1=1"
	data = json.dumps({"table_name": "rides", "column_names" : ["*"] , "column_values" : ["abcd", "1234", "1", "2"], "where": where_clause, "delete_flag" : "1"})
	headers = {'Content-Type': 'application/json'}
	response = make_request('http://127.0.0.1:5000/api/v1/db/write', data, headers, "POST")

	#print(str(response))
	if str(response) == "<Response [400]>":
		return Response(json.dumps({"result": "No rides"}), 400)
	elif str(response) == "<Response [200]>":

		data = json.dumps({"table_name": "ride_users", "column_names" : ["*"] , "column_values" : ["abcd", "1234", "1", "2"], "where": where_clause, "delete_flag" : "1"})
		response = make_request('http://127.0.0.1:5000/api/v1/db/write', data, headers, "POST")

		return Response(json.dumps({"result": "Deletion successful"}), 200)'''


	statement = text("DELETE" +  " FROM " + "rides" + " WHERE " + "1=1" + ";")
	result = db.engine.execute(statement.execution_options(autocommit=True))
	
	statement = text("DELETE" +  " FROM " + "ride_users" + " WHERE " + "1=1" + ";")
	result = db.engine.execute(statement.execution_options(autocommit=True))
	
	return Response(json.dumps({"result": "Deletion successful"}), 200)




@app.route('/api/v1/rides/<rideId>', methods=["POST"])
#postman : 127.0.0.1:5000/api/v1/rides/2
def join_ride(rideId):
	global unique_count
	unique_count += 1

	try:
		username = request.get_json()["username"]
	except:
		return Response(json.dumps({"result": "Input not in correct format"}), 400)

	where_clause = "rideId = " + "'" + rideId + "'"
	data = json.dumps({"table_name": "rides", "column_names": ["*"], "where": where_clause})
	headers = {'Content-Type': 'application/json'}
	response = make_request('http://127.0.0.1:5000/api/v1/db/read', data, headers, "POST")

	where_clause = "username = " + "'" + username + "'"
	#data = json.dumps({"table_name": "user", "column_names": ["*"], "where": where_clause})
	data = json.dumps({})
	response1 = make_request('http://CC-Rideshare-1938598602.us-east-1.elb.amazonaws.com/api/v1/users', data, headers, "GET")

	#print(str(response))
	if response.json() == []:
		return Response(json.dumps({"result": "Ride does not exist"}), 400)

	elif username not in response1.json():
		return Response(json.dumps({"result": "Username does not exist"}), 400)

	else:
		data = json.dumps({"table_name": "ride_users", "column_names" : ["rideId","username"] , "column_values" : [rideId, username], "where": where_clause, "delete_flag" : "0"})
		response = make_request('http://127.0.0.1:5000/api/v1/db/write', data, headers, "POST")
		#print(response)
		if str(response) == "<Response [400]>":
			return Response(json.dumps({"result": "Duplicate Entry"}), 400)
		return Response(json.dumps({"result": "Insertion successful"}), 200)



@app.route('/api/v1/rides',methods=["GET"])
#postman : 127.0.0.1:5000/api/v1/rides?source=1&destination=2
def get_rides():
	global unique_count
	unique_count += 1

	try:
		source = request.args.get('source', None)
		destination = request.args.get('destination', None)
	except:
		return Response(json.dumps({"result": "Input not in correct format"}), 400)

	cur = str(datetime.now())
	#new_cur = time.strftime("%Y-%m-%d %H:%M:%S", cur)
	where_clause = "source = " + "'" + source + "'" + " AND " + "destination = " + "'" + destination + "'" + " AND " + "timestamp >= " + "'" + cur +"'"
	data = json.dumps({"table_name": "rides", "column_names": ["rideId", "created_by", "timestamp"], "where": where_clause})
	headers = {'Content-Type': 'application/json'}
	response = make_request('http://127.0.0.1:5000/api/v1/db/read', data, headers, "POST")
	#print((response.json()))
	#column_names = ["rideId", "username", "timestamp"]
	#column_values = []
	src = int(source)
	des = int(destination)
	#print(int(source))
	if src>198 or src<1 or des>198 or des<1:
		return Response(json.dumps({"result": "Invalid source or destination"}), 400)
	elif response.json() == []:
		return Response(json.dumps({"result": "No upcoming rides for the given source and destination"}), 204)
	else:
		'''print(response.text)
		json_response = json.loads(response.text)
		column_values = json_response["fetched_rows"]
		column_values = column_values.strip("[(")
		column_values = column_values.strip(")]")
		column_values = column_values.replace("'", "")
		column_values = column_values.replace(" ", "")
		column_values = column_values.replace(")", "")
		column_values = column_values.split(',')
		print(column_values)
		# print(type(column_values))
		result = dict(zip(column_names, column_values))'''


		#Response(json.dumps({"result": "No upcoming rides for the given source and destination"}), 200)
		#dt = response.json()[0]["timestamp"]
		#print(dt)
		c = 0
		result = response.json()
		for i in result:
			dt = i["timestamp"]
			dt = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
			result[c]["timestamp"] = time.strftime("%d-%m-%Y:%S-%M-%H", dt)
			#print(time.strftime("%d-%m-%Y:%S-%M-%H", dt))
			c = c+1


		return jsonify(result)





@app.route('/api/v1/rides/<rideId>',methods=["GET"])
#postman : 127.0.0.1:5000/api/v1/rides
def get_details(rideId):
	global unique_count
	unique_count += 1
	#rideId = request.args.get('rideId', None)
	where_clause = "rideId = " + "'" + rideId + "'"
	data = json.dumps({"table_name": "rides", "column_names": ["rideId", "created_by", "timestamp", "source", "destination"], "where": where_clause})
	data1 = json.dumps({"table_name": "ride_users", "column_names": ["username"], "where": where_clause})
	headers = {'Content-Type': 'application/json'}
	response = make_request('http://127.0.0.1:5000/api/v1/db/read', data, headers, "POST")
	#print(response.text)
	response1 = make_request('http://127.0.0.1:5000/api/v1/db/read', data1, headers, "POST")
	#print(response1)
	#column_names = ["rideId", "Created_by", "Timestamp", "source", "destination"]
	#column_values = []
	#column_values1 = []
	fake = []
	col = []
	if response.json() == []:
		return Response(json.dumps({"result": "Ride ID does not exist"}), 204)
	else:
		#print(response.text)

		c = 0
		result = response.json()
		for i in result:
			dt = i["timestamp"]
			dt = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
			result[c]["timestamp"] = time.strftime("%d-%m-%Y:%S-%M-%H", dt)
			#print(time.strftime("%d-%m-%Y:%S-%M-%H", dt))
			c = c + 1

		for i in range(len(response1.json())):
			col.append(response1.json()[i]["username"])


		result[0]['users']=col

		return jsonify(result)



@app.route('/api/v1/db/write',methods=["POST"])
def write_to_db():


	try:
		table_name = request.get_json()["table_name"]
		column_names = request.get_json()["column_names"]
		column_values = request.get_json()["column_values"]
		delete_flag = request.get_json()["delete_flag"]
		where_clause = request.get_json()["where"]
	except:
		table_name = request.get_json()["table_name"]
		column_names = request.get_json()["column_names"]
		column_values = request.get_json()["column_values"]
		delete_flag = 0


	comma_sep_column_names = ",".join(column_names)
	comma_sep_column_values = ",".join("'{0}'".format(x) for x in column_values)
	#print(comma_sep_column_names)
	#print(comma_sep_column_values)

	if delete_flag == '1':
		statement = text("DELETE" +  " FROM " + table_name + " WHERE " + where_clause + ";")
		#print(statement)
		try:
			result = db.engine.execute(statement.execution_options(autocommit=True))
			#print(result.rowcount)
			#return str(result.rowcount)

			if result.rowcount == 0:
				return Response(json.dumps({"result": "Ride does not exist"}), 400)
			else:

				return Response(json.dumps({"result": "Deletion successful"}), 200)

		except IntegrityError:
			return "NOT OK"

	else:
		statement = text("INSERT INTO " + table_name + " (" + comma_sep_column_names + ") " + "VALUES (" + comma_sep_column_values + ");")
		#print(statement)

		#result = db.session.execute("INSERT INTO user (username,password) VALUES ('abc','123');").execution_options(autocommit = True)
		try:
			db.engine.execute(statement.execution_options(autocommit = True))
			#print(result.rowcount)
			return Response(json.dumps({"result": "Insertion successful"}), 201)
		except IntegrityError:
			return Response(json.dumps({"result": "Duplicate entry"}), 400)
	#print(result)

	#return "done"



@app.route('/api/v1/db/read',methods=["POST"])
def read_from_db():
	table_name = request.get_json()["table_name"]
	column_names = request.get_json()["column_names"]
	where_clause = request.get_json()["where"]
	#delete_flag = request.get_json()["delete_flag"]
	
	comma_sep_column_names = ",".join(column_names)


	statement = text("SELECT " + comma_sep_column_names + " FROM " + table_name + " WHERE " + where_clause + ";")
	#print(statement)
	result = db.engine.execute(statement.execution_options(autocommit = True))
	result = result.fetchall()
	res = []
	for i in result:
		res.append(dict(i))
	#print(res)
	return jsonify(res)


if __name__ == '__main__':
	
	app.debug=True
	app.run("0.0.0.0", debug = True)
	
