INSTALLATION
 - Install MongoDB 4.4.1 and have an instance running on localhost:27017
 - Install Python 3.9.0 and pip 20.2.3 (should work with somewhat older versions)
 - Extract the files of the archive to the directory of your choice
 - Setup and activate a virtual python environment in this directory
 - Install in this environment :
	- Flask 1.1.2
	- pymongo 3.11.0
	- pytest 6.1.1
 - Export the FLASK_APP environment variable : 'export FLASK_APP=app.py'
 - From the root of this directory :
	- Run the application with 'flask run'. Access results at 127.0.0.1:5000/~route~
	- Run the tests with 'pytest'

ROUTES IMPLEMENTED
 - A and C
	- GET '/songs' => Returns a list of songs
	Optional parameters : 
		- resultFrom : Used for pagination, integer telling to skip x first songs from the results.
		- resultQty : Used for pagination, integer limiting the result to x songs.
		- message : Search string that can be used to filter the results. The search
					takes into account the artist and title of the song and is case insensitive.
	Examples : 	'127.0.0.1:5000/songs'
				'127.0.0.1:5000/songs?message=yousicians&resultFrom=3&resultQty=4'

	note : A and C requests have been merged into a single route because they are fundamentally
		   requesting the same thing : a list of songs.

 - B
	- GET '/avgDifficulty' => Returns the average difficulty of the songs.
	Optional parameter :
		- level : integer filtering the songs with the matching level
	Examples : 	'127.0.0.1:5000/avgDifficulty'
				'127.0.0.1:5000/avgDifficulty?level=13'

 - D
	- POST '/songs/<songId>/addRating' => Returns _id of the created rating if successful.
	Required parameter :
		- 'songId' in the url : string representing the Object Id of a song in the db
		- 'rating' in the form data of the post request : integer from 1 to 5 inclusive
	Example : 	'127.0.0.1:5000/songs/5f8437c15b6bcb8a3ae43abb/addRating' form: {rating: 5}

 - E
	- GET '/songs/<songId>/ratingsStats' => Returns average, min and max of 
											the ratings of the given song id.
	Required parameter :
		- 'songId' in the url : string representing the Object Id of a song in the db
	Example : 	'127.0.0.1:5000/songs/5f8437c15b6bcb8a3ae43abb/ratingsStats'
