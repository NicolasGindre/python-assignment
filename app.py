from flask import Flask
from flask import jsonify
from flask import request
app = Flask(__name__)

from pymongo import MongoClient, TEXT
client = MongoClient('localhost', 27017)

from bson.json_util import loads, dumps
from bson.objectid import ObjectId
import json

# !!! DB is deleted and initialised on every restart
client.drop_database("yousicianDB")
yousicianDB = client["yousicianDB"]
songsColl = yousicianDB["songs"]
ratingsColl = yousicianDB["ratings"]

songsColl.create_index(
	[
		("artist", TEXT),
		("title", TEXT)
	],
)
songsColl.create_index("level")
ratingsColl.create_index("song_id")

songs = []
for line in open('songs.json', 'r'):
	songs.append(json.loads(line))

songsColl.insert_many(songs)

@app.route('/songs')
def songs():
	message = request.args.get('message')
	resultFrom = castToIntOrNone(request.args.get('resultFrom'))
	resultQty = castToIntOrNone(request.args.get('resultQty'))

	if message:
		query = {"$text": {"$search": message}}
	else :
		query = {}
	if resultFrom is None: resultFrom = 0
	if resultQty is None: resultQty = 0 # 0 => infinite

	cursor = songsColl.find(query).skip(resultFrom).limit(resultQty)
	songs = [json.loads(dumps(song)) for song in cursor]

	return jsonify(songs)

@app.route('/avgDifficulty')
def avgDifficulty():
	pipeline = [
		{"$group": {"_id": 0, "avgDifficulty": {"$avg": "$difficulty"}}},
	]
	level = request.args.get('level')
	if level:
		level = castToIntOrNone(level)
		levelFilterPipeline = [ {"$match": {"level": level}} ]
		pipeline = levelFilterPipeline + pipeline

	cursor = songsColl.aggregate(pipeline)
	result = list(cursor)
	if result:
		avgDifficulty = result[0]["avgDifficulty"]
	else:
		avgDifficulty = None

	return jsonify(avgDifficulty)

@app.route('/songs/<songId>/addRating', methods = ['POST'])
def addRating(songId):
	rating = castToIntOrNone(request.form["rating"])
	if rating not in [1,2,3,4,5]:
		return {"error":"Rating has to be an integer between 1 and 5"}, 400
	
	if not ObjectId.is_valid(songId):
		return {"error":"songId is not a valid objectid"}, 400
	else:
		songId = ObjectId(songId)

	if not songsColl.count_documents({ '_id': songId }, limit = 1):
		return {"error":"songId is not referencing any song in the database"}, 400

	result = ratingsColl.insert_one({"song_id": songId, "rating": rating})
	return {"_id": dumps(result.inserted_id)}

@app.route('/songs/<songId>/ratingsStats')
def ratingsStats(songId):
	if not ObjectId.is_valid(songId):
		return {"error":"songId is not a valid objectid"}, 400
	else:
		songId = ObjectId(songId)

	pipeline = [
		{"$match": {"song_id": songId}},
		{"$group": {
			"_id": None,
			"average": {"$avg": "$rating"},
			"min": {"$min": "$rating"},
			"max": {"$max": "$rating"},
		}},
		{"$project": {"_id": 0}}
	]
	cursor = ratingsColl.aggregate(pipeline)
	result = list(cursor)
	if result:
		ratingsStats = result[0]
	else:
		ratingsStats = None

	return jsonify(ratingsStats)

def castToIntOrNone(string):
	if string is not None and string.isdigit():
		return int(string)
	else:
		return None
