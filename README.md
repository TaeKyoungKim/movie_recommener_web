```
virtualenv movie_recommend_web 
cd movie_recommend_web 
Scripts\activate.bat

```

가상환경을 만든다.

데이터는 tmdb.csv를 활용하기 위해 model폴더에 저장하여 사용한다.

다음과 같은 추천알고리즘을 테스트 하기 위해 ml_test.py를 만들고

아래와 같은 코드를 추가한다.

```python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer , CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df2 = pd.read_csv('./model/tmdb.csv', encoding='utf-8')

count = TfidfVectorizer(stop_words="english")
count_matrix = count.fit_transform(df2['soup'])
cos_sim = cosine_similarity(count_matrix,count_matrix)

indices = pd.Series(df2.index , index=df2['title'])

idx = indices['Harry Potter and the Half-Blood Prince']
sim_scores = list(enumerate(cos_sim[idx]))
sim_scores = sorted(sim_scores , key=lambda x:x[1] , reverse=True)
sim_scores = sim_scores[1:11]
sim_indics = [i[0] for i in sim_scores]
tit = df2['title'].iloc[sim_indics]
dat = df2['release_date'].iloc[sim_indics]
return_df = pd.DataFrame(columns=['Title', 'Year'])
return_df['Title'] = tit
return_df['Year'] = dat

print(return_df)
```







```cmd
python ml_test.py

```

```cmd
(movie_remmend_web) C:\apps\movie_recommend_web>python ml_test.py
114           Harry Potter and the Goblet of Fire
113     Harry Potter and the Order of the Phoenix
197      Harry Potter and the Philosopher's Stone
276       Harry Potter and the Chamber of Secrets
191      Harry Potter and the Prisoner of Azkaban
37                     Oz: The Great and Powerful
2294                                Spirited Away
743                               Practical Magic
3364                                      Warlock
390                            Hotel Transylvania
Name: title, dtype: object
```

위와 같은 결과의 형태가 나온다.



위의 추천시스템을 모듈화 하기위해 

ml.py파일을 생성후 다음과 같은 코드를 추가한다.

```python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer , CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df2 = pd.read_csv('./model/tmdb.csv', encoding='utf-8')

class RECOMMEND():
    def __init__(self, vectorizer):
        self.vectorizer = vectorizer

    def get_recommendation(self, title):
        count = self.vectorizer(stop_words="english")
        count_matrix = count.fit_transform(df2['soup'])
        cos_sim = cosine_similarity(count_matrix,count_matrix)

        indices = pd.Series(df2.index , index=df2['title'])

        idx = indices[title]
        sim_scores = list(enumerate(cos_sim[idx]))
        sim_scores = sorted(sim_scores , key=lambda x:x[1] , reverse=True)
        sim_scores = sim_scores[1:11]
        sim_indics = [i[0] for i in sim_scores]
        tit = df2['title'].iloc[sim_indics]
        dat = df2['release_date'].iloc[sim_indics]
        return_df = pd.DataFrame(columns=['Title', 'Year'])
        return_df['Title'] = tit
        return_df['Year'] = dat

        print(return_df)
```

http://localhost:5000 서버를 구성하기 위해 flask 라이브러를 설치한다.

```
pip install flask
```



app.py 생성후 다음과 같은 코드를 추가

```python
from flask import Flask , request , render_template
from datetime import date
import json
from sklearn.feature_extraction.text import TfidfVectorizer , CountVectorizer

import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET' , 'POST'])
def index():
    return "SUCCESS"

if __name__ == "__main__":
    app.run(port=5000 ,debug=True)
```



TMDB api 를 활용하여 영화를 조회하고 결과값을 이용하여 페이지를 구성하기위한 단계로

https://www.themoviedb.org/ 에서 회원 가입후 로그인 한다.

![image-20210709110215446](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20210709110215446.png)

api key 발급 

http://localhost:5000 접속시 

이미지 와 여러가지 콘텐츠가 보여지위해 app.py를 다음과 같이 수정 



```python
@app.route('/', methods=['GET' , 'POST'])
def index():
    if request.method =="GET":
        year = date.today().year
        id_year = f'http://api.themoviedb.org/3/discover/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&primary_release_year={year}&sort_by=popularity.desc'
        top_year = movie_collection()
        top_year.results = []
        top_year.fetch(id_year)
        genres = json.loads(requests.get("https://api.themoviedb.org/3/genre/movie/list?api_key=da396cb4a1c47c5b912fda20fd3a3336&language=en-US").text)

        top_genre_collection = []
        for genre in genres['genres']:
            print(genre['id'])
            genre_id = 'https://api.themoviedb.org/3/discover/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&with_genres={}&sort_by=popularity.desc'.format(genre["id"])
            top_genre = movie_collection()
            top_genre.results = []
            top_genre.fetch(genre_id)
            top_genre_id = [top_genre.results, genre["name"]]
            top_genre_collection.append(top_genre_id)

    return render_template("home.html",top_year=top_year.results  , year=year ,top_genre=top_genre_collection )

```



fetch.py 파일을 생성후 이미지 url 변형 및 데이터 편집 class작성



```python
# Importing libs
import requests
import json

# Main dictionary
movie_dict = {}

# Main movie class
class movie:
    def __init__(self,id="",title="None",poster_url="None",score="None",date="None",overview="None",back_drop="None"):
        self.id = id
        self.title = title
        self.poster = "http://image.tmdb.org/t/p/w200" + str(poster_url)
        self.score = score
        self.date = date
        self.overview = overview
        self.back_drop = "http://image.tmdb.org/t/p/w200" + str(back_drop)


class movie_collection:
    def __init__(self,results=[]):
        self.results = results
    def fetch(self,url):
        results = json.loads(requests.get(url).text)["results"]
        
        print(results)
        for i in results:
            if i["id"] and i["title"] and i["poster_path"] and i["vote_average"] and i["release_date"] and i["overview"] and i["backdrop_path"]:
                self.results.append(movie(i["id"],i["title"],i["poster_path"],i["vote_average"],i["release_date"],i["overview"],i["backdrop_path"]))

    
# if __name__=="__main__":
#     mov = movie_collection().fetch("http://api.themoviedb.org/3/search/movie?api_key=15d2ea6d0dc1d476efbca3eba2b9bbfb&query=spiderman")
#     for i in mov.results:
#         print(i.id,i.title,i.poster,i.score,i.date,i.overview,i.back_drop)
#         print()
        

```





templates폴더 생성후 html 문서 작성

공통으로 적용되는 레이아웃을 만들기 위해 layout.html 생성하고 다음과 같이 추가

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta http-equiv="X-UA-Compatible" content="ie=edge" />
    <title>MovieDB</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{ url_for('static',filename='slide.css') }}" />
    <link rel="stylesheet" href="{{ url_for('static',filename='main.css') }}" />
    <link href="https://fonts.googleapis.com/css?family=Montserrat&display=swap" rel="stylesheet">
  </head>
  <body>
    {% block body %}{% endblock %}
  </body>
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
</html>
```





navigation bar 를 만들기 위해 nav.html파일 생성후 다음과 같이 코드를 추가

```html
<nav class="navbar navbar-dark">
  <a href="/" class="navbar-brand"><img id="logo" class="img-fluid" src="{{ url_for('static',filename='imgs/tmdb_logo.png') }}" alt=""></a>
  <form method="POST" action="/">
    <input id="search" type="search" placeholder="Search" name="query">
    <button class="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>
  </form>
</nav>
```





templates/home.html

```html
{% extends 'layout.html' %}
 {% block body %}
 {% include 'nav.html' %}
 <img src="{{ url_for('static',filename='imgs/tmdb_logo.png')}}"/>
 {% for i in top_year  %}
<img src="{{ i.poster }}" />
{% endfor %}
 
 {% endblock %}

```





![image-20210709143155738](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20210709143155738.png)



부분에 검색단어를 입력해서 tmdb REST api 를 이용해서 검색결과를 랜더링하는 기능을 추가한다.



@**app.route**('/', methods=['GET' , 'POST'])

def **index**(): ~~

POST로 리퀘스트가 올때 부분을 추가한다.

```python
app.route('/', methods=['GET' , 'POST'])

def index(): ~~
	...
    
elif request.method =='POST':

        # print(request.form['query'])
        key_word = request.form['query']
        id_url = f"http://api.themoviedb.org/3/search/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&query={key_word}"
        movie_dic = movie_collection()
        movie_dic.results = []
        movie_dic.fetch(id_url)
        print(movie_dic.results)
        return render_template("landing.html", movie=movie_dic.results , key_word =key_word )


```



landing.html

```html
{% extends "layout.html" %} 
{% block body %}
{% include 'nav.html' %}
  <div class="container-fluid">
    <h1 class="heading">{{movie|length}} Results for {{key_word}}</h1>
    <div class="slider">
      <div class="contain">
        <div class="row">
          <div class="row__inner">
            {% for i in movie %}
            <div class="tile">
              <a href="/details/{{i.id}}">
                  <img class="img-fluid" src="{{i.poster}}" alt="">
                  <div class="tile__details">
                    <div class="tile__title">
                      {{i.title}}
                    </div>
                  </div>
              </a>
            </div>
            {% endfor %}
          </div>
        </div>
      </div>
    </div>
  </div>
{% endblock %}
```





이미지를 클릭했을때 상세페이지가가 랜더링 되도록 

app.py를 다음과 같은 코드를 추가한다.

```python 
@app.route('/details/<id>', methods=['GET' , 'POST'])
def details(id):
    url = f"http://api.themoviedb.org/3/movie/{id}?api_key=da396cb4a1c47c5b912fda20fd3a3336"
    data = json.loads(requests.get(url).text)
    data_json = movie(data["id"],data["title"],data["poster_path"],data["vote_average"],data["release_date"],data["overview"])
    # print(data_json)
    return render_template("details.html" , movie=data_json)  
```





details.html 생성후 다음과 같이 코드를 추가

```html
{% extends "layout.html" %} 
{% block body %}
{% include 'nav.html' %}
    <div class="poster d-flex justify-content-center">
        <img class="img-fluid" src="{{movie.poster}}" alt="">
    </div>
<table>
    <tr style="color:white">
        <td style="color:white">Title</td>
        <td style="color:white">:</td>
        <td style="color:white">{{movie.title}}</td>
    </tr>
    <tr>
        <td style="color:white">Score</td>
        <td style="color:white">:</td>
        <td style="color:white">{{movie.score}}</td>
    </tr>
    <tr >
        <td style="color:white">Date</td>
        <td style="color:white">:</td>
        <td style="color:white">{{movie.date}}</td>
    </tr>
    <tr>
        <td style="color:white">Overview</td>
        <td style="color:white">:</td>
        <td style="color:white">{{movie.overview}}</td>
    </tr>
</table>
{% endblock %}
```







