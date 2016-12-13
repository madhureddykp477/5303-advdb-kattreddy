from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from flask_restful import reqparse
from flask import jsonify
from flask_cors import CORS, cross_origin
import re
import datetime

#from pymongo import MongoClient
import pymongo
from bson import Binary, Code
from bson.json_util import dumps
from bson.objectid import ObjectId

import json
import urllib


import timeit

app = FlaskAPI(__name__)
CORS(app)

client = pymongo.MongoClient('localhost', 27017)


db = client['yelpdatavm']   
businessdb = db['yelp.business']
checkin = db['yelp.checkin']
review = db['yelp.review']
userdb = db['yelp.user']
tipsdb = db['yelp.tip']


parser = reqparse.RequestParser()

# ROUTES
"""=================================================================================="""
"""=================================================================================="""
"""=================================================================================="""


@cross_origin() # allow all origins all methods.
@app.route("/", methods=['GET'])
def index():
    """Print available functions."""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return func_list

    
"""=================================================================================="""
@app.route("/user/<args>", methods=['GET'])
def user(args):

    args = myParseArgs(args)
    
    if 'skip' in args.keys():
        args['skip'] = int(args['skip'])
    if 'limit' in args.keys():
        args['limit'] = int(args['limit'])

    data = []
    
    #.skip(1).limit(1)
    
    if 'skip' in args.keys() and 'limit' in args.keys():
        result = userdb.find({},{'_id':0}).skip(args['skip']).limit(args['limit'])
    elif 'skip' in args.keys():
        result = userdb.find({},{'_id':0}).skip(args['skip'])
    elif 'limit' in args.keys():
        result = userdb.find({},{'_id':0}).limit(args['limit'])
    else:
        result = userdb.find({},{'_id':0}).limit(10)  

    for row in result:
        data.append(row)


    return {"data":data}

"""====#1 = Restaurant with zip======================================================== Perfect"""
@app.route("/zip/<args>", methods=['GET'])
def zip(args):
	"""Find all restaurants with zip."""
	args = myParseArgs(args)
	
	first = args.values()[-1]
	zipslist = first.split(',')
	zip1 = zipslist[0]
	regx1 = '.*' + zip1 + '.*'
	if zipslist[1]:
		zip2 = zipslist[1]
		regx2 = '.*' + zip2 + '.*'
	if 'start' in args.keys():
		args['start'] = int(args['start'])
	if 'limit' in args.keys():
		args['limit'] = int(args['limit'])
	data = []
	
	if 'start' in args.keys() and 'limit' in args.keys():
		result = businessdb.find({'$or': [{'full_address' : {'$regex' : regx1}},{'full_address' : {'$regex' : regx2}}]},{"name":1, "_id":0, "full_address":1}).skip(args['start']).limit(args['limit'])
	elif 'start' in args.keys():
		result = businessdb.find({'$or': [{'full_address' : {'$regex' : regx1}},{'full_address' : {'$regex' : regx2}}]},{"name":1, "_id":0, "full_address":1}).skip(args['start'])
	elif 'limit' in args.keys():
		result = businessdb.find({'$or': [{'full_address' : {'$regex' : regx1}},{'full_address' : {'$regex' : regx2}}]},{"name":1, "_id":0, "full_address":1}).limit(args['limit'])
	else:
		result = businessdb.find({'$or': [{'full_address' : {'$regex' : regx1}},{'full_address' : {'$regex' : regx2}}]},{"name":1, "_id":0, "full_address":1}).limit(100)

	for row in result:
		data.append(row)

	return {"data":data}
	
"""====#2 = Restaurant in city======================================================== Perfect"""
@app.route("/city/<args>", methods=['GET'])
def city(args):
	"""Find all restaurants in city."""
	args = myParseArgs(args)
	if 'city' in args.keys():
		args['city'] = args['city']
	first = args['city']
	regx = '.*' + first + '.*'
	if 'skip' in args.keys():
		args['skip'] = int(args['skip'])
	if 'limit' in args.keys():
		args['limit'] = int(args['limit'])
	data = []

	if 'skip' in args.keys() and 'limit' in args.keys():
		result = businessdb.find({'full_address': {'$regex': regx}},{"name":1, "_id":0}).skip(args['skip']).limit(args['limit'])
	elif 'skip' in args.keys():
		result = businessdb.find({'full_address': {'$regex': regx}},{"name":1, "_id":0}).skip(args['skip'])
	elif 'limit' in args.keys():
		result = businessdb.find({'full_address': {'$regex': regx}},{"name":1, "_id":0}).limit(args['limit'])
	else:
		result = businessdb.find({'full_address': {'$regex': regx}},{"name":1, "_id":0}).limit(10)

	for row in result:
		data.append(row)

	return {"data":data}

"""====#3 = Restaurant within 5 miles================================================= Perfect"""
@app.route("/closest/<args>", methods=['GET'])
def closest(args):
	"""Find all closest restaurants with lon and lat."""
	args = myParseArgs(args)
	if 'lon' in args.keys():
		args['lon'] = float(args['lon'])
	if 'lat' in args.keys():
		args['lat'] = float(args['lat'])
	mile = 5/3963.2
	if 'start' in args.keys():
		args['start'] = int(args['start'])
	if 'limit' in args.keys():
		args['limit'] = int(args['limit'])
	data = []
	
	if 'start' in args.keys() and 'limit' in args.keys():
		result = businessdb.find({ 'loc' : { '$geoWithin' : { '$centerSphere': [ [ args['lon'], args['lat'] ], mile ] } } },{"name":1, "_id":0}).skip(args['start']).limit(args['limit'])
	elif 'start' in args.keys():
		result = businessdb.find({ 'loc' : { '$geoWithin' : { '$centerSphere': [ [ args['lon'], args['lat'] ], mile ] } } },{"name":1, "_id":0}).skip(args['start'])
	elif 'limit' in args.keys():
		result = businessdb.find({ 'loc' : { '$geoWithin' : { '$centerSphere': [ [ args['lon'], args['lat'] ], mile ] } } },{"name":1, "_id":0}).limit(args['limit'])
	else:
		result = businessdb.find({ 'loc' : { '$geoWithin' : { '$centerSphere': [ [ args['lon'], args['lat'] ], mile ] } } },{"name":1, "_id":0, "full_address":1}).limit(100)

	for row in result:
		data.append(row)
	
	return {"data":data}
	

"""====#4 = Reviews for restaurant========================================================Perfect"""
@app.route("/reviews/<args>", methods=['GET'])
def reviews(args):
	"""Find reviews for restaurant. Input: Business ID"""
	args = myParseArgs(args)
	if 'id' in args.keys():
		last = args['id']
	if 'skip' in args.keys():
		args['skip'] = int(args['skip'])
	if 'limit' in args.keys():
		args['limit'] = int(args['limit'])
	data = []
#data.append(args)
	if 'skip' in args.keys() and 'limit' in args.keys():
		result = review.find({"business_id" : last},{"text":1, "_id":None}).skip(args['skip']).limit(args['limit'])
	elif 'skip' in args.keys():
		result = review.find({"business_id" : last},{"text":1, "_id":None}).skip(args['skip'])
	elif 'limit' in args.keys():
		result = review.find({"business_id" : last},{"text":1, "_id":None}).limit(args['limit'])
	else:
		result = review.find({"business_id" : last},{"text":1, "_id":None}).limit(10)

	for row in result:
		data.append(row)

	return {"data":data}

"""====#5 = Business ID with stars================================================= Perfect"""
@app.route("/stars/<args>", methods=['GET'])
def stars(args):
	"""Find number of, number of stars with the business ID"""
	args = myParseArgs(args)
	if 'id' in args.keys():
		args['id'] = args['id']
	if 'num_stars' in args.keys():
		args['num_stars'] = int(args['num_stars'])
	
	if 'start' in args.keys():
		args['start'] = int(args['start'])
	if 'limit' in args.keys():
		args['limit'] = int(args['limit'])
	data = []
	data.append(args['id'])
	
	if 'start' in args.keys() and 'limit' in args.keys():
		result = review.find({ '$and' : [{'business_id' : args['id']}, {'stars' : args['num_stars']}]},{"review_id":1, "_id":0, "stars":1}).skip(args['start']).limit(args['limit'])
	elif 'start' in args.keys():
		result = review.find({ '$and' : [{'business_id' : args['id']}, {'stars' : args['num_stars']}]},{"review_id":1, "_id":0, "stars":1}).skip(args['start']).limit(10)
	elif 'limit' in args.keys():
		result = review.find({ '$and' : [{'business_id' : args['id']}, {'stars' : args['num_stars']}]},{"review_id":1, "_id":0, "stars":1}).limit(args['limit'])
	else:
		result = review.find({ '$and' : [{'business_id' : args['id']}, {'stars' : args['num_stars']}]},{"review_id":1, "_id":0, "stars":1}).limit(10)

	for row in result:
		data.append(row)
	
	return {"data":data}

"""====#6 = Yelping Since========================================================Perfect"""
@app.route("/yelping/<args>", methods=['GET'])
def yelping(args):
	"""User yelping since the input years."""

	args = myParseArgs(args)
	year_ip = int(args.values()[-1])
	ip_to_days = 365*year_ip
	today = datetime.datetime.today()
	dd = datetime.timedelta(days=ip_to_days)
	sincedate = today - dd
	y = sincedate.year
	m = sincedate.month
	min_year = str(y) + '-' + str(m)
		
	if 'skip' in args.keys():
		args['skip'] = int(args['skip'])
	if 'limit' in args.keys():
		args['limit'] = int(args['limit'])
#data.append(year)
	data = []
	if 'skip' in args.keys() and 'limit' in args.keys():
		result = userdb.find({ "yelping_since" : {'$lte':min_year}},{"_id":None,"name":1,"yelping_since":1}).skip(args['skip']).limit(args['limit'])
	elif 'skip' in args.keys():
		result = userdb.find({ "yelping_since" : {'$lte':min_year}},{"_id":None,"name":1,"yelping_since":1}).skip(args['skip'])
	elif 'limit' in args.keys():
		result = userdb.find({ "yelping_since" : {'$lte':min_year}},{"_id":None,"name":1,"yelping_since":1}).limit(args['limit'])
	else:
		result = userdb.find({ "yelping_since" : {'$lte':min_year}},{"_id":None,"name":1,"yelping_since":1}).limit(10)
	
	for row in result:
		data.append(row)

	return {"data":data}
	
"""====#7 = Business with most likes========================================================Perfect"""
@app.route("/most_likes/<args>", methods=['GET'])
def most_likes(args):
	"""Business with most likes"""
	args = myParseArgs(args)
	
	if 'start' in args.keys():
		args['start'] = int(args['start'])
	if 'limit' in args.keys():
		args['limit'] = int(args['limit'])
	data = []
#data.append(args)
	if 'start' in args.keys() and 'limit' in args.keys():
		result = tipsdb.find({},{"business_id" : 1, "_id" : 0, "likes":1}).sort([('likes' , -1)]).skip(args['start']).limit(args['limit'])
	elif 'start' in args.keys():
		result = tipsdb.find({},{"business_id" : 1, "_id" : 0, "likes":1}).sort([('likes' , -1)]).skip(args['start']).limit(200)
	elif 'limit' in args.keys():
		result = tipsdb.find({},{"business_id" : 1, "_id" : 0, "likes":1}).sort([('likes' , -1)]).limit(args['limit'])
	else:
		result = tipsdb.find({},{"business_id" : 1, "_id" : 0, "likes":1}).sort([('likes' , -1)]).limit(10)

	for row in result:
		data.append(row)

	return {"data":data}

"""==#8. Review Count===============================================================Perfect"""
@app.route("/review_count/", methods=['GET'])
def review_count():
    """Average review ratings for all reviews."""
    data = []
		
    result = userdb.aggregate([{'$group':{"_id":"review_count",'averageReviewCount':{'$avg':"$review_count"}}}])
    
    for row in result:
        data.append(row)
    

    return {"data":data}

"""==#9. Elite - limit===============================================================Perfect"""
@app.route("/elite/<args>", methods=['GET'])
def elite(args):
	"""Get all the elite users."""
	args = myParseArgs(args)

	if 'start' in args.keys():
		args['start'] = int(args['start'])
	if 'limit' in args.keys():
		args['limit'] = int(args['limit'])

	data = []
	if 'start' in args.keys() and 'limit' in args.keys():
		result = userdb.find({"elite":{'$ne':[]}},{"_id":None,"user_id":1,"name":1,"elite":1}).skip(args['start']).limit(args['limit'])
	elif 'start' in args.keys():
		result = userdb.find({"elite":{'$ne':[]}},{"_id":None,"user_id":1,"name":1,"elite":1}).skip(args['start'])
	elif 'limit' in args.keys():
		result = userdb.find({"elite":{'$ne':[]}},{"_id":None,"user_id":1,"name":1,"elite":1}).limit(args['limit'])
	else:
		result = userdb.find({"elite":{'$ne':[]}},{"_id":None,"user_id":1,"name":1,"elite":1}).limit(10)
#reversed(result.keys())	
	for row in result:
		data.append(row)


	return {"data":data}

"""==#10. Elite - Reversed===============================================================Perfect"""
@app.route("/elite2/<args>", methods=['GET'])
def elite2(args):
	"""User list reversed"""
	args = myParseArgs(args)

	if 'start' in args.keys():
		args['start'] = int(args['start'])
	if 'limit' in args.keys():
		args['limit'] = int(args['limit'])

	data = []
	if 'start' in args.keys() and 'limit' in args.keys():
		result = userdb.find({"elite":{'$ne':[]}},{"_id":None,"user_id":1,"name":1,"elite":1}).skip(args['start']).limit(args['limit'])
	elif 'start' in args.keys():
		result = userdb.find({"elite":{'$ne':[]}},{"_id":None,"user_id":1,"name":1,"elite":1}).skip(args['start'])
	elif 'limit' in args.keys():
		result = userdb.find({"elite":{'$ne':[]}},{"_id":None,"user_id":1,"name":1,"elite":1}).limit(args['limit'])
	else:
		result = userdb.find({"elite":{'$ne':[]}},{"_id":None,"user_id":1,"name":1,"elite":1}).limit(1)
		
	for row in result:
		data.append(row)


	return {"data":data}

"""==#11. Average Elite===============================================================Perfect"""
@app.route("/avg_elite/", methods=['GET'])
def avg_elite():
    """Average years some is elite."""
    data = []
		
    result = userdb.aggregate([{'$project': {'elitelength':{'$size':"$elite"}}},{'$group':{"_id":None, 'avgYears':{'$avg':"$elitelength"}}}])
    
    for row in result:
        data.append(row)
    

    return {"data":data}
    
# HELPER METHODS
"""=================================================================================="""
"""=================================================================================="""
"""=================================================================================="""

def snap_time(time,snap_val):
    time = int(time)
    m = time % snap_val
    if m < (snap_val // 2):
        time -= m
    else:
        time += (snap_val - m)
        
    if (time + 40) % 100 == 0:
        time += 40
        
    return int(time)

"""=================================================================================="""
def myParseArgs(pairs=None):
    """Parses a url for key value pairs. Not very RESTful.
    Splits on ":"'s first, then "=" signs.
    
    Args:
        pairs: string of key value pairs
        
    Example:
    
        curl -X GET http://cs.mwsu.edu:5000/images/
        
    Returns:
        json object with all images
    """
    
    if not pairs:
        return {}
    
    argsList = pairs.split(":")
    argsDict = {}

    for arg in argsList:
        key,val = arg.split("=")
        argsDict[key]=str(val)
        
    return argsDict
    

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=5000)
