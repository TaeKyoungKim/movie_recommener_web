import json
import requests

genre = json.loads(requests.get("https://api.themoviedb.org/3/genre/movie/list?api_key=da396cb4a1c47c5b912fda20fd3a3336&language=en-US").text)

# print(genre['genres'])

for genre in genre['genres']:
            # print(genre['id'])
            genre_id = 'https://api.themoviedb.org/3/discover/movie/list?api_key=da396cb4a1c47c5b912fda20fd3a3336&with_genre={}&sort_by=popularity.desc'.format(genre["id"])
            print(genre_id)