import app
import pytest

@pytest.fixture
def client():
	app.app.config['TESTING'] = True
	return app.app.test_client()

def test_getSongs(client):
	response = client.get('/songs')
	songs = response.get_json()
	assert len(songs) == 11
	assert songs[2]["artist"] == "Mr Fastfinger"

	response = client.get('/songs?message=wishing in the night')
	songs = response.get_json()
	assert len(songs) == 1
	assert songs[0]["title"] == "Wishing In The Night"

	response = client.get('/songs?resultFrom=1&resultQty=6')
	songs = response.get_json()
	assert len(songs) == 6
	assert songs[0]["title"] == "A New Kennel"

	response = client.get('/songs?resultFrom=WRONG&resultQty=WRONGAGAIN')
	songs = response.get_json()
	assert len(songs) == 11
	assert songs[1]["title"] == "A New Kennel"

	response = client.get('/songs?message=yousicians&resultFrom=3&resultQty=4')
	songs = response.get_json()
	assert len(songs) == 4
	assert songs[0]["artist"] == "The Yousicians"

def test_getAvgDifficulty(client):
	response = client.get('/avgDifficulty')
	avgDiff = response.get_json()
	assert avgDiff == 113.56 / 11

	response = client.get('/avgDifficulty?level=13')
	avgDiff = response.get_json()
	assert avgDiff == 70.48 / 5

	response = client.get('/avgDifficulty?level=1000')
	avgDiff = response.get_json()
	assert avgDiff == None

	response = client.get('/avgDifficulty?level=)js18@')
	avgDiff = response.get_json()
	assert avgDiff == None

	response = client.get('/avgDifficulty?level=-1')
	avgDiff = response.get_json()
	assert avgDiff == None

def test_addRating(client):
	response = client.get('/songs')
	songs = response.get_json()
	songId = songs[0]["_id"]["$oid"]

	url = '/songs/'+ songId +'/addRating'

	response = client.post( url, data = dict(rating=3) )
	rating = response.get_json()

	assert response.status_code == 200
	assert rating["_id"] is not None

def test_addRating_wrongRating(client):
	response = client.get('/songs')
	songs = response.get_json()
	songId = songs[0]["_id"]["$oid"]

	url = '/songs/'+ songId +'/addRating'

	response = client.post( url, data = dict(rating=0) )
	json_response = response.get_json()
	assert response.status_code == 400
	assert json_response["error"] == 'Rating has to be an integer between 1 and 5'

	response = client.post( url, data = dict(rating=6) )
	json_response = response.get_json()
	assert response.status_code == 400
	assert json_response["error"] == 'Rating has to be an integer between 1 and 5'

	response = client.post( url, data = dict(rating="WRONGRATING") )
	json_response = response.get_json()
	assert response.status_code == 400
	assert json_response["error"] == 'Rating has to be an integer between 1 and 5'

def test_addRating_wrongId(client):
	url = '/songs/WRONGSONGID/addRating'
	response = client.post( url, data = dict(rating=1) )
	json_response = response.get_json()
	assert response.status_code == 400
	assert json_response["error"] == "songId is not a valid objectid"

	url = '/songs/aaaaaaaaaaaaaaaaaaaaaaaa/addRating'
	response = client.post( url, data = dict(rating=1) )
	json_response = response.get_json()
	assert response.status_code == 400
	assert json_response["error"] == "songId is not referencing any song in the database"

def test_getRatingsStats(client):
	response = client.get('/songs')
	songs = response.get_json()
	songId = songs[1]["_id"]["$oid"]

	url = '/songs/'+ songId +'/addRating'
	client.post( url, data = dict(rating=2) )
	client.post( url, data = dict(rating=3) )
	client.post( url, data = dict(rating=4) )

	url = '/songs/'+ songId +'/ratingsStats'

	response = client.get(url)
	ratingsStats = response.get_json()

	assert response.status_code == 200
	assert ratingsStats == {"average":3, "min":2, "max":4}

def test_getRatingsStats_WrongId(client):
	url = '/songs/WRONGSONGID/ratingsStats'

	response = client.get(url)
	ratingsStats = response.get_json()

	assert response.status_code == 400
	assert ratingsStats["error"] == "songId is not a valid objectid"

def test_getRatingsStats_noStats(client):
	url = '/songs/aaaaaaaaaaaaaaaaaaaaaaaa/ratingsStats'

	response = client.get(url)
	ratingsStats = response.get_json()

	assert response.status_code == 200
	assert ratingsStats == None
