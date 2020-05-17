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
import time

app=Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:@localhost/mydatabase'
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'


db = SQLAlchemy(app)

class user(db.Model):
	__tablename__ = 'user'
	username = db.Column(db.String(50), primary_key=True)
	password = db.Column(db.String(50))

db.create_all()

@app.route('/api/v1/users',methods=["PUT"])
#{"username":"qwerty",
 #	"password":"3d725109c7e7c0bfb9d709836735b56d943d263f"}
def create_user():
	if request.method != 'PUT':
		return Response(json.dumps({"result": "Invalid method"}), 405)

	try:
		username = request.get_json()["username"]
		password = request.get_json()["password"]

	except:
		return Response(json.dumps({"result": "Input not in correct format"}), 400)

	if not re.match("^[a-fA-F0-9]{40}$", password):
		return Response(json.dumps({"result": "Password not in SHA1 hash hex format"}), 400)

	#encryptpassw = hashlib.sha1(password.encode('utf-8')).hexdigest()
	#print(encryptpassw)
	#new_user = user(username,encryptpassw)
	#print(json.dumps(new_user.serialize))
	#json_obj = json.dumps(new_user.serialize)
	headers = {'Content-Type' : 'application/json'}
	data = json.dumps({"table_name" : "user", "column_names" : ["username", "password"], "column_values" : [username,password], "delete_flag" : "0", "where" : "abcd"})
	#response = requests.post('http://127.0.0.1:5000/api/v1/db/write', data = json_obj, headers = headers)
	response = make_request('http://127.0.0.1:5000/api/v1/db/write', data, headers, "POST")
	#print(str(response))

	if str(response) == "<Response [400]>":
		return Response(json.dumps({"result": "Duplicate entry"}), 400)
	elif str(response) == "<Response [201]>":
		return Response(json.dumps({"result": "Insertion successful"}), 201)


def make_request(url, data, headers, http_method):
	global response
	try:
		if http_method == "POST":
			response = requests.post(url, data = data, headers = headers)
		return response
	except requests.exceptions.RequestException as e:
		#print(e)
		return None


@app.route('/api/v1/users/<username>', methods=["DELETE"])
#postman : 127.0.0.1:5000/api/v1/users/abcd
def delete_user(username):
	#username = request.args.get('username', None)
	where_clause = "username = " + "'" + username + "'"
	data = json.dumps({"table_name": "user", "column_names": ["username", "password"], "column_values": ["abc", "1234"], "where": where_clause, "delete_flag" : "1"})
	headers = {'Content-Type': 'application/json'}
	response = make_request('http://127.0.0.1:5000/api/v1/db/write', data, headers, "POST")
	#print(str(response))

	where_clause = "created_by = " + "'" + username + "'"
	data = json.dumps({"table_name": "rides", "column_names": ["created_by", "timestamp", "source", "destination"], "column_values": ["abcd", "1234", "1", "2"], "where": where_clause, "delete_flag": "1"})
	response1 = make_request('http://172.17.0.1:8080/api/v1/db/write', data, headers, "POST")
	where_clause = "username = " + "'" + username + "'"
	data = json.dumps({"table_name": "ride_users", "column_names": ["rideId", "username"], "column_values": ["2", "abcd"], "where": where_clause, "delete_flag": "1"})
	response2 = make_request('http://172.17.0.1:8080/api/v1/db/write', data, headers, "POST")
	#print(str(response1))
	#print(str(response2))

	if str(response) == "<Response [400]>":
		return Response(json.dumps({"result": "Username does not exist"}), 400)
	elif str(response) == "<Response [200]>":
		return Response(json.dumps({"result": "Deletion successful"}), 200)



@app.route('/api/v1/db/clear', methods=["POST"])
#postman : 127.0.0.1:5000/api/v1/rides/2
def clear_db():
	where_clause = "1=1"
	data = json.dumps({"table_name": "user", "column_names" : ["*"] , "column_values" : ["abcd", "1234", "1", "2"], "where": where_clause, "delete_flag" : "1"})
	headers = {'Content-Type': 'application/json'}
	response = make_request('http://127.0.0.1:5000/api/v1/db/write', data, headers, "POST")

	#print(str(response))
	if str(response) == "<Response [400]>":
		return Response(json.dumps({"result": "No users"}), 400)
	elif str(response) == "<Response [200]>":
		return Response(json.dumps({"result": "Deletion successful"}), 200)


@app.route('/api/v1/users',methods=["GET"])
def get_users():
	#new_cur = time.strftime("%Y-%m-%d %H:%M:%S", cur)
	where_clause = "1=1"
	data = json.dumps({"table_name": "user", "column_names": ["*"], "where": where_clause})
	headers = {'Content-Type': 'application/json'}
	response = make_request('http://127.0.0.1:5000/api/v1/db/read', data, headers, "POST")

	if response.json() == []:
		return Response(json.dumps({"result": "No users"}), 204)
	else:
		result = response.json()
		return jsonify(result)


@app.route('/api/v1/db/write',methods=["POST"])
def write_to_db():
	table_name = request.get_json()["table_name"]
	column_names = request.get_json()["column_names"]
	column_values = request.get_json()["column_values"]
	delete_flag = request.get_json()["delete_flag"]
	where_clause = request.get_json()["where"]

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
	app.run(host="0.0.0.0", debug = True)
	
