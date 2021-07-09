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



내가 찾는 유사한 영화를 찾아주는 기능을 만들기 위해 

유저가 영화제목을 입력하는 페이지 구성 하기 위해



http://localhost:5000/recommend 접속을 하면 영화제목 입력 페이지 랜더링

app.py에 다음과 같은 코드를 추가한다.



```python
from flask import Flask , request , render_template
from datetime import date
import json
from sklearn.feature_extraction.text import TfidfVectorizer , CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import requests
from fetch import movie, movie_collection

# from ml import RECOMMEND
df2 = pd.read_csv('./model/tmdb.csv', encoding='utf-8')
df2 = df2.reset_index()

count = TfidfVectorizer(stop_words="english")
count_matrix = count.fit_transform(df2['soup'])


all_titles = [df2['title'][i] for i in range(len(df2['title']))]
indices = pd.Series(df2.index , index=df2['title'])

def get_recommendation(title):
    cos_sim = cosine_similarity(count_matrix,count_matrix)
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

    return return_df

app = Flask(__name__)

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
            # print(genre['id'])
            genre_id = 'https://api.themoviedb.org/3/discover/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&with_genres={}&sort_by=popularity.desc'.format(genre["id"])
            top_genre = movie_collection()
            top_genre.results = []
            top_genre.fetch(genre_id)
            top_genre_id = [top_genre.results, genre["name"]]
            top_genre_collection.append(top_genre_id)

        return render_template("home.html",top_year=top_year.results  , year=year ,top_genre=top_genre_collection )
    
    elif request.method =='POST':

        # print(request.form['query'])
        key_word = request.form['query']
        id_url = f"http://api.themoviedb.org/3/search/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&query={key_word}"
        movie_dic = movie_collection()
        movie_dic.results = []
        movie_dic.fetch(id_url)
        print(movie_dic.results)
        return render_template("landing.html", movie=movie_dic.results , key_word =key_word )


@app.route('/details/<id>', methods=['GET' , 'POST'])
def details(id):
    url = f"http://api.themoviedb.org/3/movie/{id}?api_key=da396cb4a1c47c5b912fda20fd3a3336"
    data = json.loads(requests.get(url).text)
    data_json = movie(data["id"],data["title"],data["poster_path"],data["vote_average"],data["release_date"],data["overview"])
    # print(data_json)
    return render_template("details.html" , movie=data_json)

@app.route('/recommend', methods=['GET' , 'POST'])
def recommend():
    if request.method == 'GET':
        return render_template('recommend.html')
    elif request.method == 'POST':
        
        print(len(all_titles))
        m_name = request.form['movie_name']
        # print(m_name.title())
        m_name = m_name.title()
        if m_name not in all_titles:
            return render_template('nagative.html', name= m_name)
        else:
            
            result_final = get_recommendation(m_name)
            print(type(result_final))
            data = []
            for i in range(len(result_final)):
                data.append((result_final.iloc[i][0], result_final.iloc[i][1]))
            return render_template('positive.html' , movie_data=data, search_name=m_name)        

if __name__ == "__main__":
    app.run(port=5000 ,debug=True)
```



변경 



positive.html , nagative.html 생성후 다음과 같이 코딩 



positive.html

```html
{% extends "layout.html" %} 
{% block body %}
{% include 'nav.html' %}
  <div class="container-fluid">
    <h1 class="heading">{{movie|length}} Results for {{key_word}}</h1>
    <div class="slider">
            <div class="movie">
              <h2><u>Recommendations:</u></h2>
              <p>Showing results for: {{ search_name }}</p>
              <table class="movie_table" align="center">
                  <tr>
                      <th>Movie Title</th>
                      <th>Release Date</th>
                  </tr>
                  <tbody class="table_body">
                    {% for movie_name , movie_date in movie_data %}
                    <tr>
                      <td><form method="POST" action="/">
                        <input id="search" type="text" name="query" value="{{ movie_name }}">
                        <button class="btn btn-outline-success my-2 my-sm-0" type="submit">보기</button>
                      </form>
                        {{ movie_name }}
                      </td>
                      <td>{{ movie_date }}</td>
                  </tr>
            {% endfor %}
                  </tbody>
              </table>
              <br>
              <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
              <p style="margin-top:3em;">
              Liked it? Spend a moment from you precious time to provide us valuable feedback. <i class="fas fa-smile"></i> Thank you <i class="fas fa-heart"></i>
              </p>
              <p style="color: #919191;">Feedback: <a href="https://forms.gle/7NGyYAvSe7Fepm68A">Google Form Link</a></p>
              <p style="margin-bottom: 2em; border: 1px solid grey;">Read more on recommendation systems on <a href="https://developers.google.com/machine-learning/recommendation" target="_blank">Google Developers Machine Learning Blogs</a>.</p>
        </div>
          </div>
  </div>
{% endblock %}
```





nagative.html

```html
<!DOCTYPE html>
<html lang="en" >
<head>
  <meta charset="UTF-8">
  <title>Not Found</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'>
<style>

*
{
  font-family: 'PT Sans Caption', sans-serif, 'arial', 'Times New Roman';
}
/* Error Page */
    .error .clip .shadow
    {
        height: 180px;  /*Contrall*/
    }
    .error .clip:nth-of-type(2) .shadow
    {
        width: 130px;   /*Contrall play with javascript*/ 
    }
    .error .clip:nth-of-type(1) .shadow, .error .clip:nth-of-type(3) .shadow
    {
        width: 250px; /*Contrall*/
    }
    .error .digit
    {
        width: 150px;   /*Contrall*/
        height: 150px;  /*Contrall*/
        line-height: 150px; /*Contrall*/
        font-size: 120px;
        font-weight: bold;
    }
    .error h2   /*Contrall*/
    {
        font-size: 32px;
    }
    .error .msg /*Contrall*/
    {
        top: -190px;
        left: 30%;
        width: 80px;
        height: 80px;
        line-height: 80px;
        font-size: 32px;
    }
    .error span.triangle    /*Contrall*/
    {
        top: 70%;
        right: 0%;
        border-left: 20px solid #535353;
        border-top: 15px solid transparent;
        border-bottom: 15px solid transparent;
    }


    .error .container-error-404
    {
      margin-top: 2%;
        position: relative;
        height: 250px;
        padding-top: 40px;
    }
    .error .container-error-404 .clip
    {
        display: inline-block;
        transform: skew(-45deg);
    }
    .error .clip .shadow
    {
        
        overflow: hidden;
    }
    .error .clip:nth-of-type(2) .shadow
    {
        overflow: hidden;
        position: relative;
        box-shadow: inset 20px 0px 20px -15px rgba(150, 150, 150,0.8), 20px 0px 20px -15px rgba(150, 150, 150,0.8);
    }
    
    .error .clip:nth-of-type(3) .shadow:after, .error .clip:nth-of-type(1) .shadow:after
    {
        content: "";
        position: absolute;
        right: -8px;
        bottom: 0px;
        z-index: 9999;
        height: 100%;
        width: 10px;
        background: linear-gradient(90deg, transparent, rgba(173,173,173, 0.8), transparent);
        border-radius: 50%;
    }
    .error .clip:nth-of-type(3) .shadow:after
    {
        left: -8px;
    }
    .error .digit
    {
        position: relative;
        top: 8%;
        color: white;
        background: #07B3F9;
        border-radius: 50%;
        display: inline-block;
        transform: skew(45deg);
    }
    .error .clip:nth-of-type(2) .digit
    {
        left: -10%;
    }
    .error .clip:nth-of-type(1) .digit
    {
        right: -20%;
    }.error .clip:nth-of-type(3) .digit
    {
        left: -20%;
    }    
    .error h2
    {
        color: #A2A2A2;
        font-weight: bold;
        padding-bottom: 20px;
    }
    .error .msg
    {
        position: relative;
        z-index: 9999;
        display: block;
        background: #535353;
        color: #A2A2A2;
        border-radius: 50%;
        font-style: italic;
    }
    .error .triangle
    {
        position: absolute;
        z-index: 999;
        transform: rotate(45deg);
        content: "";
        width: 0; 
        height: 0; 
    }

/* Error Page */
@media(max-width: 767px)
{
    /* Error Page */
            .error .clip .shadow
            {
                height: 100px;  /*Contrall*/
            }
            .error .clip:nth-of-type(2) .shadow
            {
                width: 80px;   /*Contrall play with javascript*/ 
            }
            .error .clip:nth-of-type(1) .shadow, .error .clip:nth-of-type(3) .shadow
            {
                width: 100px; /*Contrall*/
            }
            .error .digit
            {
                width: 80px;   /*Contrall*/
                height: 80px;  /*Contrall*/
                line-height: 80px; /*Contrall*/
                font-size: 52px;
            }
            .error h2   /*Contrall*/
            {
                font-size: 24px;
            }
            .error .msg /*Contrall*/
            {
                top: -110px;
                left: 15%;
                width: 40px;
                height: 40px;
                line-height: 40px;
                font-size: 18px;
            }
            .error span.triangle    /*Contrall*/
            {
                top: 70%;
                right: -3%;
                border-left: 10px solid #535353;
                border-top: 8px solid transparent;
                border-bottom: 8px solid transparent;
            }
.error .container-error-404
  {
    height: 150px;
  }
        /* Error Page */
}

/*--------------------------------------------Framework --------------------------------*/

.overlay { position: relative; z-index: 20; } /*done*/
    .ground-color { background: white; }  /*done*/
    .item-bg-color { background: #EAEAEA } /*done*/
    
    /* Padding Section*/
        .padding-top { padding-top: 10px; } /*done*/
        .padding-bottom { padding-bottom: 10px; }   /*done*/
        .padding-vertical { padding-top: 10px; padding-bottom: 10px; }
        .padding-horizontal { padding-left: 10px; padding-right: 10px; }
        .padding-all { padding: 10px; }   /*done*/

        .no-padding-left { padding-left: 0px; }    /*done*/
        .no-padding-right { padding-right: 0px; }   /*done*/
        .no-vertical-padding { padding-top: 0px; padding-bottom: 0px; }
        .no-horizontal-padding { padding-left: 0px; padding-right: 0px; }
        .no-padding { padding: 0px; }   /*done*/
    /* Padding Section*/

    /* Margin section */
        .margin-top { margin-top: 10px; }   /*done*/
        .margin-bottom { margin-bottom: 10px; } /*done*/
        .margin-right { margin-right: 10px; } /*done*/
        .margin-left { margin-left: 10px; } /*done*/
        .margin-horizontal { margin-left: 10px; margin-right: 10px; } /*done*/
        .margin-vertical { margin-top: 10px; margin-bottom: 10px; } /*done*/
        .margin-all { margin: 10px; }   /*done*/
        .no-margin { margin: 0px; }   /*done*/

        .no-vertical-margin { margin-top: 0px; margin-bottom: 0px; }
        .no-horizontal-margin { margin-left: 0px; margin-right: 0px; }

        .inside-col-shrink { margin: 0px 20px; }    /*done - For the inside sections that has also Title section*/ 
    /* Margin section */

    hr
    { margin: 0px; padding: 0px; border-top: 1px dashed #999; }
 
    ol{
        text-align: center;
        margin: 1em;
        color: darkgray;
        font-weight: 100;
        line-height: 2.3em;
    }
    li{
        font-size: 20px;
        font-weight: 100;
    }
    
    #suggestions{
        font-size: 20px;
        text-align: center;
        padding: 2em;
        font-family: monospace;
    }
    .button {
      font-weight: 300;
      color: #fff;
      font-size: 1.2em;
      text-decoration: none;
      border: 1px solid #efefef;
      padding: 1em;
      background: #007aff;
      border-radius: 3px;
      float: left;
      margin: 6em 0 0 -155px;
      left: 50%;
      position: relative;
      transition: all .3s linear;
    }

    .button:hover {
      background-color: #fff;
      color: #007aff;
        box-shadow: 0px 0px 5px -2px grey;
    }

</style>
</head>
<body>
<script src="https://kit.fontawesome.com/a076d05399.js"></script>
<link href='https://fonts.googleapis.com/css?family=Anton|Passion+One|PT+Sans+Caption' rel='stylesheet' type='text/css'>
            <div class="error">
                <div class="container-floud">
                    <div class="col-xs-12 ground-color text-center">
                        <div class="container-error-404">
                            <div class="clip"><div class="shadow"><span class="digit thirdDigit"></span></div></div>
                            <div class="clip"><div class="shadow"><span class="digit secondDigit"></span></div></div>
                            <div class="clip"><div class="shadow"><span class="digit firstDigit"></span></div></div>
                            <div class="msg">OH!<span class="triangle"></span></div>
                        </div>
                        <h2 class="h1">Sorry! Page not found. Possible reason(s):</h2>
                        <ol>
                            <li>Misspelled input. (Check Suggestions below)</li>
                            <li>The movie name do not exists in the database.</li>
                        </ol>
                        <input type="hidden" value="{{ name }}" id="movie_name" oninput="checkSimilarity()" readonly/>
                        <hr>
                        <p>Did you mean?</p>
                        <span id="suggestions"></span>
                    </div>
                    <a class="button" onClick="goBack()"><i class="fas fa-home"></i> Go Back to Home Page &amp; Try Again.</a>
                </div>
            </div>
</body>
<script>
function goBack() {
  window.history.back();
}
</script>
<script>
    all_titles = ["Avatar","Pirates of the Caribbean: At World's End","Spectre","The Dark Knight Rises","John Carter","Spider-Man 3","Tangled","Avengers: Age of Ultron","Harry Potter and the Half-Blood Prince","Batman v Superman: Dawn of Justice","Superman Returns","Quantum of Solace","Pirates of the Caribbean: Dead Man's Chest","The Lone Ranger","Man of Steel","The Chronicles of Narnia: Prince Caspian","The Avengers","Pirates of the Caribbean: On Stranger Tides","Men in Black 3","The Hobbit: The Battle of the Five Armies","The Amazing Spider-Man","Robin Hood","The Hobbit: The Desolation of Smaug","The Golden Compass","King Kong","Titanic","Captain America: Civil War","Battleship","Jurassic World","Skyfall","Spider-Man 2","Iron Man 3","Alice in Wonderland","X-Men: The Last Stand","Monsters University","Transformers: Revenge of the Fallen","Transformers: Age of Extinction","Oz: The Great and Powerful","The Amazing Spider-Man 2","TRON: Legacy","Cars 2","Green Lantern","Toy Story 3","Terminator Salvation","Furious 7","World War Z","X-Men: Days of Future Past","Star Trek Into Darkness","Jack the Giant Slayer","The Great Gatsby","Prince of Persia: The Sands of Time","Pacific Rim","Transformers: Dark of the Moon","Indiana Jones and the Kingdom of the Crystal Skull","The Good Dinosaur","Brave","Star Trek Beyond","WALL·E","Rush Hour 3","2012","A Christmas Carol","Jupiter Ascending","The Legend of Tarzan","The Chronicles of Narnia: The Lion, the Witch and the Wardrobe","X-Men: Apocalypse","The Dark Knight","Up","Monsters vs Aliens","Iron Man","Hugo","Wild Wild West","The Mummy: Tomb of the Dragon Emperor","Suicide Squad","Evan Almighty","Edge of Tomorrow","Waterworld","G.I. Joe: The Rise of Cobra","Inside Out","The Jungle Book","Iron Man 2","Snow White and the Huntsman","Maleficent","Dawn of the Planet of the Apes","The Lovers","47 Ronin","Captain America: The Winter Soldier","Shrek Forever After","Tomorrowland","Big Hero 6","Wreck-It Ralph","The Polar Express","Independence Day: Resurgence","How to Train Your Dragon","Terminator 3: Rise of the Machines","Guardians of the Galaxy","Interstellar","Inception","Shin Godzilla","The Hobbit: An Unexpected Journey","The Fast and the Furious","The Curious Case of Benjamin Button","X-Men: First Class","The Hunger Games: Mockingjay - Part 2","The Sorcerer's Apprentice","Poseidon","Alice Through the Looking Glass","Shrek the Third","Warcraft","Terminator Genisys","The Chronicles of Narnia: The Voyage of the Dawn Treader","Pearl Harbor","Transformers","Alexander","Harry Potter and the Order of the Phoenix","Harry Potter and the Goblet of Fire","Hancock","I Am Legend","Charlie and the Chocolate Factory","Ratatouille","Batman Begins","Madagascar: Escape 2 Africa","Night at the Museum: Battle of the Smithsonian","X-Men Origins: Wolverine","The Matrix Revolutions","Frozen","The Matrix Reloaded","Thor: The Dark World","Mad Max: Fury Road","Angels & Demons","Thor","Bolt","G-Force","Wrath of the Titans","Dark Shadows","Mission: Impossible - Rogue Nation","The Wolfman","Bee Movie","Kung Fu Panda 2","The Last Airbender","Mission: Impossible III","White House Down","Mars Needs Moms","Flushed Away","Pan","Mr. Peabody & Sherman","Troy","Madagascar 3: Europe's Most Wanted","Die Another Day","Ghostbusters","Armageddon","Men in Black II","Beowulf","Kung Fu Panda 3","Mission: Impossible - Ghost Protocol","Rise of the Guardians","Fun with Dick and Jane","The Last Samurai","Exodus: Gods and Kings","Star Trek","Spider-Man","How to Train Your Dragon 2","Gods of Egypt","Stealth","Watchmen","Lethal Weapon 4","Hulk","G.I. Joe: Retaliation","Sahara","Final Fantasy: The Spirits Within","Captain America: The First Avenger","The World Is Not Enough","Master and Commander: The Far Side of the World","The Twilight Saga: Breaking Dawn - Part 2","Happy Feet Two","The Incredible Hulk","The BFG","The Revenant","Turbo","Rango","Penguins of Madagascar","The Bourne Ultimatum","Kung Fu Panda","Ant-Man","The Hunger Games: Catching Fire","Home","War of the Worlds","Bad Boys II","Puss in Boots","Salt","Noah","The Adventures of Tintin","Harry Potter and the Prisoner of Azkaban","Australia","After Earth","Dinosaur","Night at the Museum: Secret of the Tomb","Megamind","Harry Potter and the Philosopher's Stone","R.I.P.D.","Pirates of the Caribbean: The Curse of the Black Pearl","The Hunger Games: Mockingjay - Part 1","The Da Vinci Code","Rio 2","X2","Fast Five","Sherlock Holmes: A Game of Shadows","Clash of the Titans","Total Recall","The 13th Warrior","The Bourne Legacy","Batman & Robin","How the Grinch Stole Christmas","The Day After Tomorrow","Mission: Impossible II","The Perfect Storm","Fantastic 4: Rise of the Silver Surfer","Life of Pi","Ghost Rider","Jason Bourne","Charlie's Angels: Full Throttle","Prometheus","Stuart Little 2","Elysium","The Chronicles of Riddick","RoboCop","Speed Racer","How Do You Know","Knight and Day","Oblivion","Star Wars: Episode III - Revenge of the Sith","Star Wars: Episode II - Attack of the Clones","Monsters, Inc.","The Wolverine","Star Wars: Episode I - The Phantom Menace","The Croods","Asterix at the Olympic Games","Windtalkers","The Huntsman: Winter's War","Teenage Mutant Ninja Turtles","Gravity","Dante's Peak","Teenage Mutant Ninja Turtles: Out of the Shadows","Fantastic Four","Night at the Museum","San Andreas","Tomorrow Never Dies","The Patriot","Ocean's Twelve","Mr. & Mrs. Smith","Insurgent","The Aviator","Gulliver's Travels","The Green Hornet","300: Rise of an Empire","The Smurfs","Home on the Range","Allegiant","Real Steel","The Smurfs 2","Speed 2: Cruise Control","Ender's Game","Live Free or Die Hard","The Lord of the Rings: The Fellowship of the Ring","Around the World in 80 Days","Ali","The Cat in the Hat","I, Robot","Kingdom of Heaven","Stuart Little","The Princess and the Frog","The Martian","The Island","Town & Country","Gone in Sixty Seconds","Gladiator","Minority Report","Harry Potter and the Chamber of Secrets","Casino Royale","Planet of the Apes","Terminator 2: Judgment Day","Public Enemies","American Gangster","True Lies","The Taking of Pelham 1 2 3","Little Fockers","The Other Guys","Eraser","Django Unchained","The Hunchback of Notre Dame","The Emperor's New Groove","The Expendables 2","National Treasure","Eragon","Where the Wild Things Are","Epic","The Tourist","End of Days","Blood Diamond","The Wolf of Wall Street","Batman Forever","Starship Troopers","Cloud Atlas","Legend of the Guardians: The Owls of Ga'Hoole","Catwoman","Hercules","Treasure Planet","Land of the Lost","The Expendables 3","Point Break","Son of the Mask","In the Heart of the Sea","The Adventures of Pluto Nash","Green Zone","The Peanuts Movie","The Spanish Prisoner","The Mummy Returns","Gangs of New York","The Flowers of War","Surf's Up","The Stepford Wives","Black Hawk Down","The Campaign","The Fifth Element","Sex and the City 2","The Road to El Dorado","Ice Age: Continental Drift","Cinderella","The Lovely Bones","Finding Nemo","The Lord of the Rings: The Return of the King","The Lord of the Rings: The Two Towers","Seventh Son","Lara Croft: Tomb Raider","Transcendence","Jurassic Park III","Rise of the Planet of the Apes","The Spiderwick Chronicles","A Good Day to Die Hard","The Alamo","The Incredibles","Cutthroat Island","Percy Jackson & the Olympians: The Lightning Thief","Men in Black","Toy Story 2","Unstoppable","Rush Hour 2","What Lies Beneath","Cloudy with a Chance of Meatballs","Ice Age: Dawn of the Dinosaurs","The Secret Life of Walter Mitty","Charlie's Angels","The Departed","Mulan","Tropic Thunder","The Girl with the Dragon Tattoo","Die Hard: With a Vengeance","Sherlock Holmes","Ben-Hur","Atlantis: The Lost Empire","Alvin and the Chipmunks: The Road Chip","Valkyrie","You Don't Mess with the Zohan","Pixels","A.I. Artificial Intelligence","The Haunted Mansion","Contact","Hollow Man","The Interpreter","Percy Jackson: Sea of Monsters","Lara Croft Tomb Raider: The Cradle of Life","Now You See Me 2","The Saint","Spy Game","Mission to Mars","Rio","Bicentennial Man","Volcano","The Devil's Own","K-19: The Widowmaker","Conan the Barbarian","Cinderella Man","The Nutcracker: The Untold Story","Seabiscuit","Twister","Cast Away","Happy Feet","The Bourne Supremacy","Air Force One","Ocean's Eleven","The Three Musketeers","Hotel Transylvania","Enchanted","Safe House","102 Dalmatians","Tower Heist","The Holiday","Enemy of the State","It's Complicated","Ocean's Thirteen","Open Season","Divergent","Enemy at the Gates","The Rundown","Last Action Hero","Memoirs of a Geisha","The Fast and the Furious: Tokyo Drift","Arthur Christmas","Meet Joe Black","Collateral Damage","All That Jazz","Mirror Mirror","Scott Pilgrim vs. the World","The Core","Nutty Professor II: The Klumps","Scooby-Doo","Dredd","Click","Creepshow","Cats & Dogs 2 : The Revenge of Kitty Galore","Jumper","Hellboy II: The Golden Army","Zodiac","The 6th Day","Bruce Almighty","The Expendables","Mission: Impossible","The Hunger Games","The Hangover Part II","Batman Returns","Over the Hedge","Lilo & Stitch","Charlotte's Web","Deep Impact","RED 2","The Longest Yard","Alvin and the Chipmunks: Chipwrecked","Grown Ups 2","Get Smart","Something's Gotta Give","Shutter Island","Four Christmases","Robots","Face/Off","Bedtime Stories","Road to Perdition","Just Go with It","Con Air","Eagle Eye","Cold Mountain","The Book of Eli","Flubber","The Haunting","Space Jam","The Pink Panther","The Day the Earth Stood Still","Conspiracy Theory","Fury","Six Days Seven Nights","Yogi Bear","Spirit: Stallion of the Cimarron","Zookeeper","Lost in Space","The Manchurian Candidate","Déjà Vu","Hotel Transylvania 2","Fantasia 2000","The Time Machine","Mighty Joe Young","Swordfish","The Legend of Zorro","What Dreams May Come","Little Nicky","The Brothers Grimm","Mars Attacks!","Evolution","The Edge","Surrogates","Thirteen Days","Daylight","Walking With Dinosaurs","Battlefield Earth","Looney Tunes: Back in Action","Nine","Timeline","The Postman","Babe: Pig in the City","The Last Witch Hunter","Red Planet","Arthur and the Invisibles","Oceans","A Sound of Thunder","Pompeii","Top Cat Begins","A Beautiful Mind","The Lion King","Journey 2: The Mysterious Island","Cloudy with a Chance of Meatballs 2","Red Dragon","Hidalgo","Jack and Jill","2 Fast 2 Furious","The Little Prince","The Invasion","The Adventures of Rocky & Bullwinkle","The Secret Life of Pets","The League of Extraordinary Gentlemen","Despicable Me 2","Independence Day","The Lost World: Jurassic Park","Madagascar","Children of Men","X-Men","Wanted","The Rock","Ice Age: The Meltdown","50 First Dates","Hairspray","Exorcist: The Beginning","Inspector Gadget","Now You See Me","Grown Ups","The Terminal","Hotel for Dogs","Vertical Limit","Charlie Wilson's War","Shark Tale","Dreamgirls","Be Cool","Munich","Tears of the Sun","Killers","The Man from U.N.C.L.E.","Spanglish","Monster House","Bandits","First Knight","Anna and the King","Immortals","Hostage","Titan A.E.","Hollywood Homicide","Soldier","Carriers","Monkeybone","Flight of the Phoenix","Unbreakable","Minions","Sucker Punch","Snake Eyes","Sphere","The Angry Birds Movie","Fool's Gold","Funny People","The Kingdom","Talladega Nights: The Ballad of Ricky Bobby","Dr. Dolittle 2","Braveheart","Jarhead","The Simpsons Movie","The Majestic","Driven","Two Brothers","The Village","Doctor Dolittle","Signs","Shrek 2","Cars","Runaway Bride","xXx","The SpongeBob Movie: Sponge Out of Water","Ransom","Inglourious Basterds","Hook","Die Hard 2","S.W.A.T.","Vanilla Sky","Lady in the Water","AVP: Alien vs. Predator","Alvin and the Chipmunks: The Squeakquel","We Were Soldiers","Olympus Has Fallen","Star Trek: Insurrection","Battle: Los Angeles","Big Fish","Wolf","War Horse","The Monuments Men","The Abyss","Wall Street: Money Never Sleeps","Dracula Untold","The Siege","Stardust","Seven Years in Tibet","The Dilemma","Bad Company","Doom","I Spy","Underworld: Awakening","Rock of Ages","Hart's War","Killer Elite","Rollerball","Ballistic: Ecks vs. Sever","Hard Rain","Osmosis Jones","Legends of Oz: Dorothy's Return","Blackhat","Sky Captain and the World of Tomorrow","Basic Instinct 2","Escape Plan","The Legend of Hercules","The Sum of All Fears","The Twilight Saga: Eclipse","The Score","Despicable Me","Money Train","Ted 2","Agora","Mystery Men","Hall Pass","The Insider","The Finest Hours","Body of Lies","Dinner for Schmucks","Abraham Lincoln: Vampire Hunter","Entrapment","The X Files","The Last Legion","Saving Private Ryan","Need for Speed","What Women Want","Ice Age","Dreamcatcher","Lincoln","The Matrix","Apollo 13","The Santa Clause 2","Les Misérables","You've Got Mail","Step Brothers","The Mask of Zorro","Due Date","Unbroken","Space Cowboys","Cliffhanger","Broken Arrow","The Kid","World Trade Center","Mona Lisa Smile","The Dictator","Eyes Wide Shut","Annie","Focus","This Means War","Blade: Trinity","Red Dawn","Primary Colors","Resident Evil: Retribution","Death Race","The Long Kiss Goodnight","Proof of Life","Zathura: A Space Adventure","Fight Club","We Are Marshall","Hudson Hawk","Lucky Numbers","I, Frankenstein","Oliver Twist","Elektra","Sin City: A Dame to Kill For","Random Hearts","Everest","Perfume: The Story of a Murderer","Austin Powers in Goldmember","Astro Boy","Jurassic Park","Wyatt Earp","Clear and Present Danger","Dragon Blade","Little Man","U-571","The American President","The Love Guru","3000 Miles to Graceland","The Hateful Eight","Blades of Glory","Hop","300","Meet the Fockers","Marley & Me","The Green Mile","Wild Hogs","Chicken Little","Gone Girl","The Bourne Identity","GoldenEye","The General's Daughter","The Truman Show","The Prince of Egypt","Daddy Day Care","2 Guns","Cats & Dogs","The Italian Job","Two Weeks Notice","Antz","Couples Retreat","Days of Thunder","Cheaper by the Dozen 2","Maze Runner: The Scorch Trials","Eat Pray Love","The Family Man","RED","Any Given Sunday","The Horse Whisperer","Collateral","The Scorpion King","Ladder 49","Jack Reacher","Deep Blue Sea","This Is It","Contagion","Kangaroo Jack","Coraline","The Happening","Man on Fire","The Shaggy Dog","Starsky & Hutch","Jingle All the Way","Hellboy","A Civil Action","ParaNorman","The Jackal","Paycheck","Up Close & Personal","The Tale of Despereaux","The Tuxedo","Under Siege 2: Dark Territory","Jack Ryan: Shadow Recruit","Joy","London Has Fallen","Alien: Resurrection","Shooter","The Boxtrolls","Practical Magic","The Lego Movie","Miss Congeniality 2: Armed and Fabulous","Reign of Fire","Gangster Squad","Year One","Invictus","State of Play","Duplicity","My Favorite Martian","The Sentinel","Planet 51","Star Trek: Nemesis","Intolerable Cruelty","Trouble with the Curve","Edge of Darkness","The Relic","Analyze That","Righteous Kill","Mercury Rising","The Soloist","The Legend of Bagger Vance","Almost Famous","Garfield: A Tail of Two Kitties","xXx: State of the Union","Priest","Sinbad: Legend of the Seven Seas","Event Horizon","Dragonfly","The Black Dahlia","Flyboys","The Last Castle","Supernova","Winter's Tale","The Mortal Instruments: City of Bones","Meet Dave","Dark Water","Edtv","Inkheart","The Spirit","Mortdecai","In the Name of the King: A Dungeon Siege Tale","Beyond Borders","The Monkey King 2","The Great Raid","Deadpool","Holy Man","American Sniper","Goosebumps","Just Like Heaven","The Flintstones in Viva Rock Vegas","Rambo III","Leatherheads","The Ridiculous 6","Did You Hear About the Morgans?","The Internship","Resident Evil: Afterlife","Red Tails","The Devil's Advocate","That's My Boy","DragonHeart","After the Sunset","Ghost Rider: Spirit of Vengeance","Captain Corelli's Mandolin","The Pacifier","Walking Tall","Forrest Gump","Alvin and the Chipmunks","Meet the Parents","Pocahontas","Superman","The Nutty Professor","Hitch","George of the Jungle","American Wedding","Captain Phillips","Date Night","Casper","The Equalizer","Maid in Manhattan","Crimson Tide","The Pursuit of Happyness","Flightplan","Disclosure","City of Angels","Kill Bill: Vol. 1","Bowfinger","Kill Bill: Vol. 2","Tango & Cash","Death Becomes Her","Shanghai Noon","Executive Decision","Mr. Popper's Penguins","The Forbidden Kingdom","Free Birds","Alien³","Evita","Ronin","The Ghost and the Darkness","Paddington","The Watch","The Hunted","Instinct","Stuck on You","Semi-Pro","The Pirates! In an Adventure with Scientists!","Changeling","Chain Reaction","The Fan","The Phantom of the Opera","Elizabeth: The Golden Age","Æon Flux","Gods and Generals","Turbulence","Imagine That","Muppets Most Wanted","Thunderbirds","Burlesque","A Very Long Engagement","Lolita","D-Tox","Blade II","Seven Pounds","Bullet to the Head","The Godfather: Part III","Elizabethtown","You, Me and Dupree","Superman II","Gigli","All the King's Men","Shaft","Anastasia","Moulin Rouge!","Domestic Disturbance","Black Mass","Flags of Our Fathers","Law Abiding Citizen","Grindhouse","Beloved","Lucky You","Catch Me If You Can","Zero Dark Thirty","The Break-Up","Mamma Mia!","Valentine's Day","The Dukes of Hazzard","The Thin Red Line","The Change-Up","Man on the Moon","Casino","From Paris with Love","Bulletproof Monk","Me, Myself & Irene","Barnyard","Deck the Halls","The Twilight Saga: New Moon","Shrek","The Adjustment Bureau","Robin Hood: Prince of Thieves","Jerry Maguire","Ted","As Good as It Gets","Patch Adams","Anchorman 2: The Legend Continues","Mr. Deeds","Super 8","Erin Brockovich","How to Lose a Guy in 10 Days","22 Jump Street","Interview with the Vampire","Yes Man","Central Intelligence","Stepmom","Daddy's Home","Into the Woods","Inside Man","Payback","Congo","We Bought a Zoo","Knowing","Failure to Launch","The Ring Two","Crazy, Stupid, Love.","Garfield","Christmas with the Kranks","Moneyball","Outbreak","Non-Stop","Race to Witch Mountain","V for Vendetta","Shanghai Knights","Curious George","Herbie Fully Loaded","Don't Say a Word","Hansel & Gretel: Witch Hunters","Unfaithful","I Am Number Four","Syriana","13 Hours: The Secret Soldiers of Benghazi","The Book of Life","Firewall","Absolute Power","G.I. Jane","The Game","Silent Hill","The Replacements","American Reunion","The Negotiator","Into the Storm","Beverly Hills Cop III","Gremlins 2: The New Batch","The Judge","The Peacemaker","Resident Evil: Apocalypse","Bridget Jones: The Edge of Reason","Out of Time","On Deadly Ground","The Adventures of Sharkboy and Lavagirl","The Beach","Raising Helen","Ninja Assassin","For Love of the Game","Striptease","Marmaduke","Hereafter","Murder by Numbers","Assassins","Hannibal Rising","The Story of Us","The Host","Basic","Blood Work","The International","Escape from L.A.","The Iron Giant","The Life Aquatic with Steve Zissou","Free State of Jones","The Life of David Gale","Man of the House","Run All Night","Eastern Promises","Into the Blue","The Messenger: The Story of Joan of Arc","Your Highness","Dream House","Mad City","Baby's Day Out","The Scarlet Letter","Fair Game","Domino","Jade","Gamer","Beautiful Creatures","Death to Smoochy","Zoolander 2","The Big Bounce","What Planet Are You From?","Drive Angry","Street Fighter: The Legend of Chun-Li","The One","The Adventures of Ford Fairlane","The Boat That Rocked","Traffic","Indiana Jones and the Last Crusade","Anna Karenina","Chappie","The Bone Collector","Panic Room","The Tooth Fairy","Three Kings","Child 44","Rat Race","K-PAX","Kate & Leopold","Bedazzled","The Cotton Club","3:10 to Yuma","Taken 3","Out of Sight","The Cable Guy","Earth","Dick Tracy","The Thomas Crown Affair","Riding in Cars with Boys","First Blood","Solaris","Happily N'Ever After","Mary Reilly","My Best Friend's Wedding","America's Sweethearts","Insomnia","Star Trek: First Contact","Jonah Hex","Courage Under Fire","Liar Liar","The Infiltrator","Inchon","The Flintstones","Taken 2","Scary Movie 3","Miss Congeniality","Journey to the Center of the Earth","The Princess Diaries 2: Royal Engagement","The Pelican Brief","The Client","The Bucket List","Patriot Games","Monster-in-Law","Prisoners","Training Day","Galaxy Quest","Scary Movie 2","The Muppets","Blade","Coach Carter","Changing Lanes","Anaconda","Coyote Ugly","Love Actually","A Bug's Life","From Hell","The Specialist","Tin Cup","Yours, Mine and Ours","Kicking & Screaming","The Hitchhiker's Guide to the Galaxy","Fat Albert","Resident Evil: Extinction","Blended","Last Holiday","The River Wild","The Indian in the Cupboard","Savages","Cellular","Johnny English","The Ant Bully","Dune","Across the Universe","Revolutionary Road","16 Blocks","Babylon A.D.","The Glimmer Man","Multiplicity","Aliens in the Attic","The Pledge","The Producers","The Phantom","All the Pretty Horses","Nixon","The Ghost Writer","Deep Rising","Miracle at St. Anna","Curse of the Golden Flower","Bangkok Dangerous","Big Trouble","Love in the Time of Cholera","Shadow Conspiracy","Johnny English Reborn","Foodfight!","Argo","The Fugitive","The Bounty Hunter","Sleepers","Rambo: First Blood Part II","The Juror","Pinocchio","Heaven's Gate","Underworld: Evolution","Victor Frankenstein","Finding Forrester","28 Days","Unleashed","The Sweetest Thing","The Firm","Charlie St. Cloud","The Mechanic","21 Jump Street","Notting Hill","Chicken Run","Along Came Polly","Boomerang","The Heat","Cleopatra","Here Comes the Boom","High Crimes","The Mirror Has Two Faces","The Mothman Prophecies","Brüno","Licence to Kill","Red Riding Hood","15 Minutes","Super Mario Bros.","Lord of War","Hero","One for the Money","The Interview","The Warrior's Way","Micmacs","8 Mile","Why I Did (Not) Eat My Father","A Knight's Tale","The Medallion","The Sixth Sense","Man on a Ledge","The Big Year","The Karate Kid","American Hustle","The Proposal","Double Jeopardy","Back to the Future Part II","Lucy","Fifty Shades of Grey","Spy Kids 3-D: Game Over","A Time to Kill","Cheaper by the Dozen","Lone Survivor","A League of Their Own","The Conjuring 2","The Social Network","He's Just Not That Into You","Scary Movie 4","Scream 3","Back to the Future Part III","Get Hard","Dracula","Julie & Julia","42","The Talented Mr. Ripley","Dumb and Dumber To","Eight Below","The Intern","Ride Along 2","The Last of the Mohicans","Ray","Sin City","Vantage Point","I Love You, Man","Shallow Hal","JFK","Big Momma's House 2","The Mexican","17 Again","The Other Woman","The Final Destination","Bridge of Spies","Behind Enemy Lines","Get Him to the Greek","Shall We Dance?","Small Soldiers","Spawn","The Count of Monte Cristo","The Lincoln Lawyer","Unknown","The Prestige","Horrible Bosses 2","Escape from Planet Earth","Apocalypto","The Living Daylights","Predators","Legal Eagles","Secret Window","The Lake House","The Skeleton Key","The Odd Life of Timothy Green","Made of Honor","Jersey Boys","The Rainmaker","Gothika","Amistad","Medicine Man","Aliens vs Predator: Requiem","Ri¢hie Ri¢h","Autumn in New York","Music and Lyrics","Paul","The Guilt Trip","Scream 4","8MM","The Doors","Sex Tape","Hanging Up","Final Destination 5","Mickey Blue Eyes","Pay It Forward","Fever Pitch","Drillbit Taylor","A Million Ways to Die in the West","The Shadow","Extremely Loud & Incredibly Close","Morning Glory","Get Rich or Die Tryin'","The Art of War","Rent","Bless the Child","The Out-of-Towners","The Island of Dr. Moreau","The Musketeer","The Other Boleyn Girl","Sweet November","The Reaping","Mean Streets","Renaissance Man","Colombiana","Quest for Camelot","City By The Sea","At First Sight","Torque","City Hall","Showgirls","Marie Antoinette","Kiss of Death","Get Carter","The Impossible","Ishtar","Fantastic Mr. Fox","Life or Something Like It","Memoirs of an Invisible Man","Amélie","New York Minute","Alfie","Big Miracle","The Deep End of the Ocean","FearDotCom","Cirque du Freak: The Vampire's Assistant","Duplex","Soul Men","Raise the Titanic","Universal Soldier: The Return","Pandorum","Impostor","Extreme Ops","Just Visiting","Sunshine","A Thousand Words","Delgo","The Gunman","Stormbreaker","Disturbia","Hackers","The Hunting Party","The Hudsucker Proxy","The Warlords","Nomad: The Warrior","Snowpiercer","A Monster in Paris","The Last Shot","The Crow","Baahubali: The Beginning","The Time Traveler's Wife","Because I Said So","Frankenweenie","Serenity","Against the Ropes","Superman III","Grudge Match","Red Cliff","Sweet Home Alabama","The Ugly Truth","Sgt. Bilko","Spy Kids 2: The Island of Lost Dreams","Star Trek: Generations","The Grandmaster","Water for Elephants","Dragon Nest: Warriors' Dawn","The Hurricane","Enough","Heartbreakers","Paul Blart: Mall Cop 2","Angel Eyes","Joe Somebody","The Ninth Gate","Extreme Measures","Rock Star","Precious","White Squall","The Thing","Riddick","Switchback","Texas Rangers","City of Ember","The Master","Virgin Territory","The Express","The 5th Wave","Creed","The Town","What to Expect When You're Expecting","Burn After Reading","Nim's Island","Rush","Magnolia","Cop Out","How to Be Single","Dolphin Tale","Twilight","John Q","Blue Streak","We're the Millers","The Inhabited Island","Breakdown","Never Say Never Again","Hot Tub Time Machine","Dolphin Tale 2","Reindeer Games","A Man Apart","Aloha","Ghosts of Mississippi","Snow Falling on Cedars","The Rite","Gattaca","Isn't She Great","Space Chimps","Head of State","The Hangover","Ip Man 3","Austin Powers: The Spy Who Shagged Me","Batman","There Be Dragons","Lethal Weapon 3","The Blind Side","Spy Kids","Horrible Bosses","True Grit","The Devil Wears Prada","Star Trek: The Motion Picture","Identity Thief","Cape Fear","21","Trainwreck","Guess Who","The English Patient","L.A. Confidential","Sky High","In & Out","Species","A Nightmare on Elm Street","The Cell","The Man in the Iron Mask","Secretariat","TMNT","Radio","Friends with Benefits","Neighbors 2: Sorority Rising","Saving Mr. Banks","Malcolm X","This Is 40","Old Dogs","Underworld: Rise of the Lycans","License to Wed","The Benchwarmers","Must Love Dogs","Donnie Brasco","Resident Evil","Poltergeist","The Ladykillers","Max Payne","In Time","The Back-Up Plan","Something Borrowed","Black Knight","The Bad News Bears","Street Fighter","The Pianist","The Nativity Story","House of Wax","Closer","J. Edgar","Mirrors","Queen of the Damned","Predator 2","Untraceable","Blast from the Past","Flash Gordon","Jersey Girl","Alex Cross","Midnight in the Garden of Good and Evil","Heist","Nanny McPhee and the Big Bang","Hoffa","The X Files: I Want to Believe","Ella Enchanted","Concussion","Abduction","Valiant","Wonder Boys","Superhero Movie","Broken City","Cursed","Premium Rush","Hot Pursuit","The Four Feathers","Parker","Wimbledon","Furry Vengeance","Bait","Krull","Lions for Lambs","Flight of the Intruder","Walk Hard: The Dewey Cox Story","The Shipping News","American Outlaws","The Young Victoria","Whiteout","The Tree of Life","Knock Off","Sabotage","The Order","Punisher: War Zone","Zoom","The Walk","Warriors of Virtue","A Good Year","Radio Flyer","Bound by Honor","Smilla's Sense of Snow","Femme Fatale","Lion of the Desert","The Horseman on the Roof","Ride with the Devil","Biutiful","Bandidas","Black Water Transit","The Maze Runner","Unfinished Business","The Age of Innocence","The Fountain","Chill Factor","Stolen","Ponyo","The Longest Ride","The Astronaut's Wife","I Dreamed of Africa","Playing for Keeps","Mandela: Long Walk to Freedom","Reds","A Few Good Men","Exit Wounds","Big Momma's House","Thunder and the House of Magic","The Darkest Hour","Step Up Revolution","Snakes on a Plane","The Watcher","The Punisher","Goal!: The Dream Begins","Safe","Pushing Tin","Return of the Jedi","Doomsday","The Reader","Wanderlust","Elf","Phenomenon","Snow Dogs","Scrooged","Nacho Libre","Bridesmaids","This Is the End","Stigmata","Men of Honor","Takers","The Big Wedding","Big Mommas: Like Father, Like Son","Source Code","Alive","The Number 23","The Young and Prodigious T.S. Spivet","1941","Dreamer: Inspired By a True Story","A History of Violence","Transporter 2","The Quick and the Dead","Laws of Attraction","Bringing Out the Dead","Repo Men","Dragon Wars: D-War","Bogus","The Incredible Burt Wonderstone","Cats Don't Dance","Cradle Will Rock","The Good German","George and the Dragon","Apocalypse Now","Going the Distance","Mr. Holland's Opus","Criminal","Out of Africa","Flight","Moonraker","The Grand Budapest Hotel","Hearts in Atlantis","Arachnophobia","Frequency","Vacation","Get Shorty","Chicago","Big Daddy","American Pie 2","Toy Story","Speed","The Vow","Extraordinary Measures","Remember the Titans","The Hunt for Red October","The Butler","DodgeBall: A True Underdog Story","The Addams Family","Ace Ventura: When Nature Calls","The Princess Diaries","The First Wives Club","Se7en","District 9","The SpongeBob SquarePants Movie","Mystic River","Million Dollar Baby","Analyze This","The Notebook","27 Dresses","Hannah Montana: The Movie","Rugrats in Paris: The Movie","The Prince of Tides","Legends of the Fall","Up in the Air","About Schmidt","Warm Bodies","Looper","Down to Earth","Babe","Hope Springs","Forgetting Sarah Marshall","Four Brothers","Baby Mama","Hope Floats","Bride Wars","Without a Paddle","13 Going on 30","Midnight in Paris","The Nut Job","Blow","Message in a Bottle","Star Trek V: The Final Frontier","Like Mike","The Naked Gun 33⅓: The Final Insult","A View to a Kill","The Curse of the Were-Rabbit","P.S. I Love You","Racing Stripes","Atonement","Letters to Juliet","Black Rain","The Three Stooges","Corpse Bride","Glory Road","Sicario","Southpaw","Drag Me to Hell","The Age of Adaline","Secondhand Lions","Step Up 3D","Blue Crush","Stranger Than Fiction","30 Days of Night","The Cabin in the Woods","Meet the Spartans","Midnight Run","The Running Man","Little Shop of Horrors","Hanna","Mortal Kombat: Annihilation","Larry Crowne","Carrie","Take the Lead","Gridiron Gang","What's the Worst That Could Happen?","9","Side Effects","The Prince & Me","Winnie the Pooh","Dumb and Dumberer: When Harry Met Lloyd","Bulworth","Get on Up","One True Thing","Virtuosity","My Super Ex-Girlfriend","Deliver Us from Evil","Sanctum","Little Black Book","The Five-Year Engagement","Mr. 3000","The Next Three Days","Ultraviolet","Assault on Precinct 13","The Replacement Killers","Fled","Eight Legged Freaks","Love & Other Drugs","88 Minutes","North Country","The Whole Ten Yards","Splice","Howard the Duck","Pride and Glory","The Cave","Alex & Emma","Wicker Park","Fright Night","The New World","Wing Commander","In Dreams","Dragonball Evolution","The Last Stand","Godsend","Chasing Liberty","Hoodwinked Too! Hood VS. Evil","An Unfinished Life","The Imaginarium of Doctor Parnassus","Barney's Version","Runner Runner","Antitrust","Glory","Once Upon a Time in America","Dead Man Down","The Merchant of Venice","The Good Thief","Supercross","Miss Potter","The Promise","DOA: Dead or Alive","The Assassination of Jesse James by the Coward Robert Ford","1911","Little Nicholas","Wild Card","Machine Gun Preacher","Animals United","Goodbye Bafana","United Passions","Grace of Monaco","Savva. Heart of the Warrior","Ripley's Game","Sausage Party","Pitch Perfect 2","Walk the Line","Keeping the Faith","The Borrowers","Frost/Nixon","Confessions of a Dangerous Mind","Serving Sara","The Boss","Cry Freedom","Mumford","Seed of Chucky","The Jacket","Aladdin","Straight Outta Compton","Indiana Jones and the Temple of Doom","The Rugrats Movie","Along Came a Spider","Florence Foster Jenkins","Once Upon a Time in Mexico","Die Hard","Role Models","The Big Short","Taking Woodstock","Miracle","Dawn of the Dead","The Wedding Planner","Space Pirate Captain Harlock","The Royal Tenenbaums","Identity","Last Vegas","For Your Eyes Only","Serendipity","Timecop","Zoolander","Safe Haven","Hocus Pocus","No Reservations","Kick-Ass","30 Minutes or Less","Dracula 2000","Alexander and the Terrible, Horrible, No Good, Very Bad Day","Pride & Prejudice","Blade Runner","Rob Roy","3 Days to Kill","We Own the Night","Lost Souls","Winged Migration","Just My Luck","Mystery, Alaska","The Spy Next Door","A Simple Wish","Ghosts of Mars","Our Brand Is Crisis","Pride and Prejudice and Zombies","Kundun","How to Lose Friends & Alienate People","Kick-Ass 2","Alatriste","Brick Mansions","Octopussy","Knocked Up","My Sister's Keeper","Welcome Home Roscoe Jenkins","A Passage to India","Notes on a Scandal","Rendition","Star Trek VI: The Undiscovered Country","Divine Secrets of the Ya-Ya Sisterhood","Kiss the Girls","The Blues Brothers","The Sisterhood of the Traveling Pants 2","Joyful Noise","About a Boy","Lake Placid","Lucky Number Slevin","The Right Stuff","Anonymous","The NeverEnding Story","Dark City","The Duchess","Return to Oz","The Newton Boys","Case 39","Suspect Zero","Martian Child","Spy Kids: All the Time in the World","Money Monster","The 51st State","Flawless","Mindhunters","What Just Happened","The Statement","The Magic Flute","Paul Blart: Mall Cop","Freaky Friday","The 40 Year Old Virgin","Shakespeare in Love","A Walk Among the Tombstones","Kindergarten Cop","Pineapple Express","Ever After: A Cinderella Story","Open Range","Flatliners","A Bridge Too Far","Red Eye","Final Destination 2","O Brother, Where Art Thou?","Legion","Pain & Gain","In Good Company","Clockstoppers","Silverado","Brothers","Agent Cody Banks 2: Destination London","New Year's Eve","Original Sin","The Raven","Welcome to Mooseport","Highlander: The Final Dimension","Blood and Wine","Snow White: A Tale of Terror","The Curse of the Jade Scorpion","Accidental Love","Flipper","Self/less","The Constant Gardener","The Passion of the Christ","Mrs. Doubtfire","Rain Man","Gran Torino","W.","Taken","The Best of Me","The Bodyguard","Schindler's List","The Help","The Fifth Estate","Scooby-Doo 2: Monsters Unleashed","Forbidden Kingdom","Freddy vs. Jason","The Face of an Angel","Jimmy Neutron: Boy Genius","Cloverfield","Teenage Mutant Ninja Turtles II: The Secret of the Ooze","The Untouchables","No Country for Old Men","Ride Along","Bridget Jones's Diary","Chocolat","Legally Blonde 2: Red, White & Blonde","Parental Guidance","No Strings Attached","Tombstone","Romeo Must Die","The Omen","Final Destination 3","The Lucky One","Bridge to Terabithia","Finding Neverland","A Madea Christmas","The Grey","Hide and Seek","Anchorman: The Legend of Ron Burgundy","GoodFellas","Agent Cody Banks","Nanny McPhee","Scarface","Nothing to Lose","The Last Emperor","Contraband","Money Talks","There Will Be Blood","The Wild Thornberrys Movie","Rugrats Go Wild","Undercover Brother","The Sisterhood of the Traveling Pants","Kiss of the Dragon","The House Bunny","Beauty Shop","Million Dollar Arm","The Giver","What a Girl Wants","Jeepers Creepers 2","Good Luck Chuck","Cradle 2 the Grave","The Hours","She's the Man","Mr. Bean's Holiday","Anacondas: The Hunt for the Blood Orchid","Blood Ties","August Rush","Elizabeth","Bride of Chucky","Tora! Tora! Tora!","Spice World","The Sitter","Dance Flick","The Shawshank Redemption","Crocodile Dundee in Los Angeles","Kingpin","The Gambler","August: Osage County","Ice Princess","A Lot Like Love","Eddie the Eagle","He Got Game","Don Juan DeMarco","Dear John","The Losers","Don't Be Afraid of the Dark","War","Punch-Drunk Love","EuroTrip","Half Past Dead","Unaccompanied Minors","Bright Lights, Big City","The Adventures of Pinocchio","The Greatest Game Ever Played","The Box","The Ruins","The Next Best Thing","My Soul to Take","The Girl Next Door","Maximum Risk","Stealing Harvard","Legend","Hot Rod","Shark Night","Angela's Ashes","Draft Day","Lifeforce","The Conspirator","Lords of Dogtown","The 33","Big Trouble in Little China","Fly Me to the Moon","Warrior","Michael Collins","Gettysburg","Stop-Loss","Abandon","Brokedown Palace","The Possession","Mrs. Winterbourne","Straw Dogs","The Hoax","Stone Cold","The Road","Sheena","Underclassman","Say It Isn't So","The World's Fastest Indian","Tank Girl","King's Ransom","Blindness","BloodRayne","Carnage","Where the Truth Lies","Cirque du Soleil: Worlds Away","Without Limits","Me and Orson Welles","The Best Offer","The Bad Lieutenant: Port of Call - New Orleans","A Turtle's Tale: Sammy's Adventures","Little White Lies","Love Ranch","The True Story of Puss 'n Boots","Space Dogs","The Counselor","Ironclad","Waterloo","Kung Fu Jungle","Red Sky","Dangerous Liaisons","On the Road","Star Trek IV: The Voyage Home","Rocky Balboa","Scream 2","Jane Got a Gun","Think Like a Man Too","The Whole Nine Yards","Footloose","Old School","The Fisher King","I Still Know What You Did Last Summer","Return to Me","Zack and Miri Make a Porno","Nurse Betty","The Men Who Stare at Goats","Double Take","Girl, Interrupted","Win a Date with Tad Hamilton!","Muppets from Space","The Wiz","Ready to Rumble","Play It to the Bone","I Don't Know How She Does It","Piranha 3D","Beyond the Sea","Meet the Deedles","The Thief and the Cobbler","The Bridge of San Luis Rey","Faster","Howl's Moving Castle","Zombieland","The Waterboy","The Empire Strikes Back","Bad Boys","The Naked Gun 2½: The Smell of Fear","Final Destination","The Ides of March","Pitch Black","Someone Like You...","Her","Joy Ride","The Adventurer: The Curse of the Midas Box","Anywhere But Here","The Crew","Haywire","Jaws: The Revenge","Marvin's Room","The Longshots","The End of the Affair","Harley Davidson and the Marlboro Man","In the Valley of Elah","Coco Before Chanel","Forsaken","Cheri","Vanity Fair","Bodyguards and Assassins","1408","Spaceballs","The Water Diviner","Ghost","There's Something About Mary","The Santa Clause","The Rookie","The Game Plan","The Bridges of Madison County","The Animal","Gandhi","The Hundred-Foot Journey","The Net","I Am Sam","Son of God","Underworld","Derailed","The Informant!","Shadowlands","Deuce Bigalow: European Gigolo","Delivery Man","Our Kind of Traitor","Saving Silverman","Diary of a Wimpy Kid: Dog Days","Summer of Sam","Jay and Silent Bob Strike Back","The Glass House","Hail, Caesar!","Josie and the Pussycats","Homefront","The Little Vampire","I Heart Huckabees","RoboCop 3","Megiddo: The Omega Code 2","Darling Lili","Dudley Do-Right","The Transporter Refueled","The Libertine","Black Book","Joyeux Noël","Hit & Run","Mad Money","Before I Go to Sleep","Sorcerer","Stone","Moliere","Out of the Furnace","Michael Clayton","My Fellow Americans","Arlington Road","Underdogs","To Rome with Love","Firefox","South Park: Bigger, Longer & Uncut","Death at a Funeral","Teenage Mutant Ninja Turtles III","Hardball","Silver Linings Playbook","Freedom Writers","For Colored Girls","The Transporter","Never Back Down","The Rage: Carrie 2","Away We Go","Swing Vote","Moonlight Mile","Tinker Tailor Soldier Spy","Molly","The Beaver","The Best Little Whorehouse in Texas","eXistenZ","Raiders of the Lost Ark","Home Alone 2: Lost in New York","Close Encounters of the Third Kind","Pulse","Beverly Hills Cop II","Bringing Down the House","The Silence of the Lambs","Wayne's World","Jackass 3D","Jaws 2","Beverly Hills Chihuahua","The Conjuring","Are We There Yet?","Tammy","School of Rock","Mortal Kombat","White Chicks","The Descendants","Holes","The Last Song","12 Years a Slave","Drumline","Why Did I Get Married Too?","Edward Scissorhands","Me Before You","Madea's Witness Protection","The French Connection","Bad Moms","Date Movie","Return to Never Land","Selma","The Jungle Book 2","Boogeyman","Premonition","The Tigger Movie","Orphan","Max","Epic Movie","Spotlight","Lakeview Terrace","The Grudge 2","How Stella Got Her Groove Back","Bill & Ted's Bogus Journey","Man of the Year","The Black Hole","The American","Selena","Vampires Suck","Babel","This Is Where I Leave You","Doubt","Team America: World Police","Texas Chainsaw 3D","Copycat","Scary Movie 5","Paint Your Wagon","Milk","Risen","Ghost Ship","A Very Harold & Kumar Christmas","Wild Things","The Stepfather","The Debt","High Fidelity","One Missed Call","Eye for an Eye","The Bank Job","Eternal Sunshine of the Spotless Mind","You Again","Street Kings","The World's End","Nancy Drew","Daybreakers","She's Out of My League","Monte Carlo","Stay Alive","Quigley Down Under","Alpha and Omega","The Covenant","Stick It","Shorts","To Die For","Nerve","Appaloosa","Vampires","Psycho","My Best Friend's Girl","Endless Love","Georgia Rule","Under the Rainbow","Ladyhawke","Simon Birch","Reign Over Me","Into the Wild","School for Scoundrels","Silent Hill: Revelation 3D","From Dusk Till Dawn","Pooh's Heffalump Movie","Home for the Holidays","Kung Fu Hustle","The Country Bears","The Kite Runner","21 Grams","Paparazzi","A Guy Thing","Loser","Capitalism: A Love Story","The Greatest Story Ever Told","Secret in Their Eyes","Disaster Movie","Armored","The Man Who Knew Too Little","What's Your Number?","Lockout","Envy","Crank: High Voltage","Bullets Over Broadway","One Night with the King","The Quiet American","The Weather Man","Undisputed","Ghost Town","12 Rounds","Let Me In","3 Ninjas Kick Back","Be Kind Rewind","Mrs Henderson Presents","Triple 9","Deconstructing Harry","Three to Tango","Burnt","We're No Angels","Everyone Says I Love You","Death Sentence","Everybody's Fine","Superbabies: Baby Geniuses 2","The Man","Code Name: The Cleaner","Connie and Carla","Sweet Charity","Inherent Vice","Doogal","Battle of the Year","An American Carol","Machete Kills","Willard","Strange Wilderness","Topsy-Turvy","Little Boy","A Dangerous Method","A Scanner Darkly","Chasing Mavericks","Alone in the Dark","Bandslam","Birth","A Most Violent Year","Passchendaele","Flash of Genius","I'm Not There.","The Cold Light of Day","The Brothers Bloom","Synecdoche, New York","Princess Mononoke","Bon voyage","Can't Stop the Music","The Proposition","My All American","Marci X","Equilibrium","The Children of Huang Shi","The Yards","The Oogieloves in the Big Balloon Adventure","By the Sea","Steamboy","The Game of Their Lives","All Good Things","Rapa Nui","CJ7","The Visitors II: The Corridors of Time","Dylan Dog: Dead of Night","People I Know","The Tempest","Regression","Three Kingdoms: Resurrection of the Dragon","Butterfly on a Wheel","Zambezia","Ramanujan","Dwegons","Hands of Stone","Survivor","The Frozen Ground","The Painted Veil","The Baader Meinhof Complex","Dances with Wolves","Bad Teacher","Sea of Love","A Cinderella Story","Scream","Thir13en Ghosts","The Shining","Back to the Future","House on Haunted Hill","I Can Do Bad All By Myself","Fight Valley","The Switch","Just Married","The Devil's Double","Thomas and the Magic Railroad","The Crazies","Spirited Away","Firestorm","The Bounty","The Book Thief","Sex Drive","Leap Year","The Fall of the Roman Empire","Take Me Home Tonight","Won't Back Down","The Nutcracker","Kansas City","Indignation","The Amityville Horror","Adaptation.","Land of the Dead","Out of Inferno","Fear and Loathing in Las Vegas","The Invention of Lying","Neighbors","The Mask","Big","Borat: Cultural Learnings of America for Make Benefit Glorious Nation of Kazakhstan","Legally Blonde","Star Trek III: The Search for Spock","The Exorcism of Emily Rose","Deuce Bigalow: Male Gigolo","Left Behind","The Family Stone","Barbershop 2:  Back in Business","Bad Santa","Austin Powers: International Man of Mystery","My Big Fat Greek Wedding 2","Diary of a Wimpy Kid: Rodrick Rules","Predator","Amadeus","Prom Night","Mean Girls","Under the Tuscan Sun","Gosford Park","Peggy Sue Got Married","Birdman","Blue Jasmine","United 93","Honey","Spy Hard","The Fog","Soul Surfer","Catch-22","Observe and Report","Conan the Destroyer","Raging Bull","Love Happens","Young Sherlock Holmes","Fame","127 Hours","Small Time Crooks","Center Stage","Love the Coopers","Catch That Kid","Life as a House","Steve Jobs","I Love You, Beth Cooper","Youth in Revolt","The Legend of the Lone Ranger","The Tailor of Panama","Blow Out","Getaway","The Ice Storm","And So It Goes","Troop Beverly Hills","Being Julia","Nine 1/2 Weeks","Dragonslayer","The Last Station","Ed Wood","Labor Day","Mongol: The Rise of Genghis Khan","RockNRolla","Megaforce","Hamlet","Mao's Last Dancer","Midnight Special","Anything Else","The Railway Man","The White Ribbon","Restoration","The Wraith","Salton Sea","Metallica: Through the Never","The Informers","Carlos","I Come with the Rain","One Man's Hero","Day of the Dead","I Am Wrath","Renaissance","Red Sonja","Red Lights","Superbad","Madea Goes to Jail","Wolves","Step Up 2: The Streets","Hoodwinked!","Hotel Rwanda","Hitman","Black Nativity","The Prince","City of Ghosts","The Others","Aliens","My Fair Lady","I Know What You Did Last Summer","Let's Be Cops","Sideways","Beerfest","Halloween","Good Boy!","The Best Man Holiday","Smokin' Aces","Saw: The Final Chapter","40 Days and 40 Nights","A Night at the Roxbury","Beastly","The Hills Have Eyes","Dickie Roberts: Former Child Star","McFarland, USA","Lottery Ticket","ATL","Pitch Perfect","Summer Catch","A Simple Plan","They","Larry the Cable Guy: Health Inspector","The Adventures of Elmo in Grouchland","Brooklyn's Finest","55 Days at Peking","Evil Dead","My Life in Ruins","American Dreamz","Superman IV: The Quest for Peace","How She Move","Running Scared","Bobby Jones: Stroke of Genius","Shanghai Surprise","The Illusionist","Roar","Veronica Guerin","Escobar: Paradise Lost","Southland Tales","Dragon Hunters","Damnation Alley","The Apparition","My Girl","Fur: An Imaginary Portrait of Diane Arbus","Wall Street","Sense and Sensibility","Becoming Jane","Sydney White","House of Sand and Fog","Dead Poets Society","Dumb and Dumber","When Harry Met Sally...","The Verdict","Road Trip","Varsity Blues","The Artist","The Unborn","Moonrise Kingdom","The Texas Chainsaw Massacre: The Beginning","The Young Messiah","The Master of Disguise","Pan's Labyrinth","See Spot Run","Baby Boy","The Roommate","Joe Dirt","Double Impact","Hot Fuzz","The Women","Vicky Cristina Barcelona","Arn: The Knight Templar","Boys and Girls","White Oleander","Jennifer's Body","Drowning Mona","Radio Days","Remember Me","How to Deal","My Stepmother is an Alien","Philadelphia","The Thirteenth Floor","The Cookout","Meteor","Duets","Hollywood Ending","Detroit Rock City","Highlander","Things We Lost in the Fire","Steel","The Immigrant","The White Countess","Trance","Soul Plane","Welcome to the Sticks","Good","Enter the Void","Vamps","Hachi: A Dog's Tale","Zulu","The Homesman","Juwanna Mann","Ararat","Madison","Slow Burn","Wasabi","Slither","Beverly Hills Cop","Home Alone","Three Men and a Baby","Tootsie","Top Gun","Crouching Tiger, Hidden Dragon","American Beauty","The King's Speech","Twins","The Yellow Handkerchief","The Color Purple","Tidal Wave","The Imitation Game","Private Benjamin","Coal Miner's Daughter","Diary of a Wimpy Kid","Mama","National Lampoon's Vacation","Bad Grandpa","The Queen","Beetlejuice","Why Did I Get Married?","Little Women","The Woman in Black","When a Stranger Calls","Big Fat Liar","The Deer Hunter","Wag the Dog","The Lizzie McGuire Movie","Snitch","Krampus","The Faculty","What's Love Got to Do with It","Cop Land","Not Another Teen Movie","End of Watch","The Skulls","The Theory of Everything","Malibu's Most Wanted","Where the Heart Is","Lawrence of Arabia","Halloween II","Wild","The Last House on the Left","The Wedding Date","Halloween: Resurrection","The Princess Bride","The Great Debaters","Drive","Confessions of a Teenage Drama Queen","The Object of My Affection","28 Weeks Later","When the Game Stands Tall","Because of Winn-Dixie","Love & Basketball","Grosse Pointe Blank","All About Steve","Book of Shadows: Blair Witch 2","The Craft","Match Point","Ramona and Beezus","The Remains of the Day","Boogie Nights","Nowhere to Run","Flicka","The Hills Have Eyes 2","Urban Legends: Final Cut","Tuck Everlasting","The Marine","Keanu","Country Strong","Disturbing Behavior","The Place Beyond the Pines","The November Man","Eye of the Beholder","The Hurt Locker","Firestarter","Killing Them Softly","A Most Wanted Man","Freddy Got Fingered","VeggieTales: The Pirates Who Don't Do Anything","U2 3D","Highlander: Endgame","Idlewild","One Day","Whip It","Knockaround Guys","Confidence","The Muse","De-Lovely","New York Stories","Barney's Great Adventure","The Man with the Iron Fists","Home Fries","Here On Earth","Brazil","Raise Your Voice","The Big Lebowski","Black Snake Moan","Dark Blue","A Mighty Heart","Whatever It Takes","Boat Trip","The Importance of Being Earnest","The Love Letter","Hoot","In Bruges","Peeples","The Rocker","Post Grad","Promised Land","Whatever Works","The In Crowd","The Three Burials of Melquiades Estrada","Jakob the Liar","Kiss Kiss Bang Bang","Idle Hands","Mulholland Drive","Blood and Chocolate","You Will Meet a Tall Dark Stranger","Never Let Me Go","The Company","Transsiberian","The Clan of the Cave Bear","Crazy in Alabama","Funny Games","Listening","Felicia's Journey","Metropolis","District B13","Things to Do in Denver When You're Dead","The Assassin","Buffalo Soldiers","The Return","Ong Bak 2","Centurion","Silent Trigger","The Midnight Meat Train","Winnie Mandela","The Son of No One","All The Queen's Men","The Good Night","Bathory: Countess of Blood","Khumba","Automata","Dungeons & Dragons: Wrath of the Dragon God","Chiamatemi Francesco - Il Papa della gente","Shinjuku Incident","Pandaemonium","Groundhog Day","Magic Mike XXL","Romeo + Juliet","Sarah's Key","Freedom","Unforgiven","Manderlay","Slumdog Millionaire","Fatal Attraction","Pretty Woman","Crocodile Dundee II","Broken Horses","Born on the Fourth of July","Cool Runnings","My Bloody Valentine","Stomp the Yard","The Spy Who Loved Me","Urban Legend","Good Deeds","White Fang","Superstar","The Iron Lady","Jonah: A VeggieTales Movie","Poetic Justice","All About the Benjamins","Vampire in Brooklyn","Exorcist II: The Heretic","An American Haunting","My Boss's Daughter","A Perfect Getaway","Our Family Wedding","Dead Man on Campus","Tea with Mussolini","Thinner","New York, New York","Crooklyn","I Think I Love My Wife","Jason X","Bobby","Head Over Heels","Fun Size","The Diving Bell and the Butterfly","Little Children","Gossip","A Walk on the Moon","Catch a Fire","Soul Survivors","Jefferson in Paris","Easy Virtue","Caravans","Mr. Turner","Wild Grass","Amen.","Reign of Assassins","The Lucky Ones","Margaret","Stan Helsing","Flipped","Brokeback Mountain","Clueless","Far from Heaven","Hot Tub Time Machine 2","Quills","Seven Psychopaths","The Caveman's Valentine","Downfall","The Sea Inside","Under the Skin","Good Morning, Vietnam","The Last Godfather","Justin Bieber: Never Say Never","Black Swan","The Godfather: Part II","Save the Last Dance","A Nightmare on Elm Street 4: The Dream Master","Miracles from Heaven","Dude, Where's My Car?","Young Guns","St. Vincent","About Last Night","10 Things I Hate About You","The New Guy","National Lampoon's Loaded Weapon 1","The Shallows","The Butterfly Effect","Snow Day","This Christmas","Baby Geniuses","The Big Hit","Harriet the Spy","Child's Play 2","No Good Deed","The Mist","Ex Machina","Being John Malkovich","Two Can Play That Game","Earth to Echo","Crazy/Beautiful","Letters from Iwo Jima","The Astronaut Farmer","Woo","Room","Dirty Work","Serial Mom","Dick","Light It Up","54","Bubble Boy","Birthday Girl","21 & Over","Paris, je t'aime","Resurrecting the Champ","Admission","The Widow of Saint-Pierre","Chloe","Faithful","Find Me Guilty","The Perks of Being a Wallflower","Excessive Force","Infamous","The Claim","The Vatican Tapes","Attack the Block","In the Land of Blood and Honey","The Call","Operation Chromite","The Crocodile Hunter: Collision Course","I Love You Phillip Morris","Quest for Fire","Antwone Fisher","The Emperor's Club","True Romance","Womb","Glengarry Glen Ross","The Killer Inside Me","Cat People","Sorority Row","The Prisoner of Zenda","Lars and the Real Girl","The Boy in the Striped Pyjamas","Dancer in the Dark","Oscar and Lucinda","The Funeral","Solitary Man","Machete","Casino Jack","The Land Before Time","Tae Guk Gi: The Brotherhood of War","The Perfect Game","The Exorcist","Jaws","American Pie","Ernest & Celestine","The Golden Child","Think Like a Man","Barbershop","Star Trek II: The Wrath of Khan","Ace Ventura: Pet Detective","WarGames","Witness","Act of Valor","Step Up","Beavis and Butt-Head Do America","Jackie Brown","Harold & Kumar Escape from Guantanamo Bay","Chronicle","Yentl","Time Bandits","Crossroads","Project X","Patton","One Hour Photo","Quarantine","The Eye","Johnson Family Vacation","How High","The Muppet Christmas Carol","Frida","Katy Perry: Part of Me","The Fault in Our Stars","Rounders","Top Five","Prophecy","Stir of Echoes","Philomena","The Upside of Anger","The Boys from Brazil","Aquamarine","Paper Towns","My Baby's Daddy","Nebraska","Tales from the Crypt: Demon Knight","Max Keeble's Big Move","Young Adult","Crank","Def Jam's How to Be a Player","Living Out Loud","Just Wright","Rachel Getting Married","The Postman Always Rings Twice","Girl with a Pearl Earring","Das Boot","Sorority Boys","About Time","House of Flying Daggers","Arbitrage","Project Almanac","Cadillac Records","Screwed","Fortress","For Your Consideration","Celebrity","Running with Scissors","From Justin to Kelly","Girl 6","In the Cut","Two Lovers","Last Orders","The Host","The Pursuit of D.B. Cooper","Ravenous","Charlie Bartlett","The Great Beauty","The Dangerous Lives of Altar Boys","Stoker","2046","Married Life","Duma","Ondine","Brother","Welcome to Collinwood","Critical Care","The Life Before Her Eyes","Darling Companion","Trade","Fateless","Breakfast of Champions","A Woman, a Gun and a Noodle Shop","Cypher","City of Life and Death","Legend of a Rabbit","Space Battleship Yamato","5 Days of War","Triangle","10 Days in a Madhouse","Heaven is for Real","Snatch","Dancin' It's On","Pet Sematary","Madadayo","The Cry of the Owl","A Tale of Three Cities","Gremlins","Star Wars","Dirty Grandpa","Doctor Zhivago","Trash","High School Musical 3: Senior Year","The Fighter","Jackass Number Two","My Cousin Vinny","If I Stay","Drive Hard","Major League","St. Trinian's","Phone Booth","A Walk to Remember","Dead Man Walking","Cruel Intentions","Saw VI","History of the World: Part I","The Secret Life of Bees","Corky Romano","Raising Cain","F.I.S.T.","Invaders from Mars","Brooklyn","Barry Lyndon","Out Cold","The Ladies Man","Quartet","Tomcats","Frailty","Woman in Gold","Kinsey","Army of Darkness","Slackers","What's Eating Gilbert Grape","The Visual Bible: The Gospel of John","Vera Drake","The Guru","The Perez Family","Inside Llewyn Davis","O","Return to the Blue Lagoon","The Molly Maguires","Romance & Cigarettes","Copying Beethoven","Brighton Rock","Saw V","Machine Gun McCain","LOL","Jindabyne","Kabhi Alvida Naa Kehna","An Ideal Husband","The Last Days on Mars","Darkness","2001: A Space Odyssey","E.T. the Extra-Terrestrial","In the Land of Women","The Blue Butterfly","There Goes My Baby","Housefull","September Dawn","For Greater Glory - The True Story of Cristiada","The Bélier Family","Good Will Hunting","Misconduct","Saw III","Stripes","Bring It On","The Purge: Election Year","She's All That","Saw IV","White Noise","Madea's Family Reunion","The Color of Money","The Longest Day","The Mighty Ducks","The Grudge","Happy Gilmore","Jeepers Creepers","Bill & Ted's Excellent Adventure","Oliver!","The Best Exotic Marigold Hotel","Recess: School's Out","Mad Max Beyond Thunderdome","Commando","The Boy","Devil","Friday After Next","Insidious: Chapter 3","The Last Dragon","The Lawnmower Man","Nick and Norah's Infinite Playlist","Dogma","The Banger Sisters","Twilight Zone: The Movie","Road House","A Low Down Dirty Shame","Swimfan","Employee of the Month","Can't Hardly Wait","The Outsiders","Pete's Dragon","The Dead Zone","Sinister 2","Sparkle","Valentine","The Fourth Kind","A Prairie Home Companion","Sugar Hill","Invasion U.S.A.","Roll Bounce","Rushmore","Skyline","The Second Best Exotic Marigold Hotel","Kit Kittredge: An American Girl","The Perfect Man","Mo' Better Blues","Kung Pow: Enter the Fist","Tremors","Wrong Turn","The Long Riders","The Corruptor","Mud","Reno 911!: Miami","One Direction: This Is Us","The Goods: Live Hard, Sell Hard","Hey Arnold! The Movie","My Week with Marilyn","The Matador","Love Jones","The Gift","End of the Spear","Get Over It","Office Space","Drop Dead Gorgeous","Big Eyes","Very Bad Things","Sleepover","Body Double","MacGruber","Dirty Pretty Things","Movie 43","Over Her Dead Body","Seeking a Friend for the End of the World","Cedar Rapids","American History X","The Collection","Teacher's Pet","The Red Violin","The Straight Story","Deuces Wild","Bad Words","Run, Fatboy, Run","Heartbeeps","Black or White","On the Line","Rescue Dawn","Danny Collins","Jeff, Who Lives at Home","I Am Love","Atlas Shrugged Part II","Romeo Is Bleeding","The Limey","Crash","The House of Mirth","Malone","Peaceful Warrior","Bucky Larson: Born to Be a Star","Bamboozled","The Forest","Sphinx","While We're Young","A Better Life","Spider","Gun Shy","Nicholas Nickleby","The Iceman","Krrish","Cecil B. Demented","Killer Joe","The Joneses","Owning Mahowny","The Brothers Solomon","My Blueberry Nights","Illuminata","Swept Away","War, Inc.","Shaolin Soccer","The Brown Bunny","The Swindle","Rosewater","The Chambermaid on the Titanic","Coriolanus","Imaginary Heroes","High Heels and Low Lifes","World's Greatest Dad","Severance","Edmond","Welcome to the Rileys","Police Academy: Mission to Moscow","Blood Done Sign My Name","Cinco de Mayo: La Batalla","Elsa & Fred","An Alan Smithee Film: Burn, Hollywood, Burn","The Open Road","The Good Guy","Motherhood","Free Style","Strangerland","Janky Promoters","Blonde Ambition","The Oxford Murders","The Reef","Eulogy","White Noise 2: The Light","Beat the World","Fifty Dead Men Walking","Jungle Shuffle","Adam Resurrected","Of Horses and Men","It's a Wonderful Afterlife","The Devil's Tomb","Partition","Good Intentions","The Good, The Bad, The Weird","Nurse 3-D","Gunless","Adventureland","The Lost City","Next Friday","American Heist","You Only Live Twice","Plastic","Amour","Poltergeist III","Re-Kill","It's a Mad, Mad, Mad, Mad World","Volver","Heavy Metal","Gentlemen Broncos","Richard III","Into the Grizzly Maze","Kites","Melancholia","Red Dog","Jab Tak Hai Jaan","Alien","The Texas Chain Saw Massacre","The Runaways","Fiddler on the Roof","Thunderball","Detention","Loose Cannons","Set It Off","The Best Man","Child's Play","Sicko","The Purge: Anarchy","Down to You","Harold & Kumar Go to White Castle","The Contender","Boiler Room","Trading Places","Black Christmas","Breakin' All the Rules","Henry V","The Savages","Chasing Papi","The Way of the Gun","Igby Goes Down","PCU","The Ultimate Gift","The Ice Pirates","Gracie","Trust the Man","Hamlet 2","Velvet Goldmine","The Wailing","Glee: The Concert Movie","The Legend of Suriyothai","Two Evil Eyes","Barbecue","All or Nothing","Princess Kaiulani","Opal Dream","Flame & Citron","Undiscovered","Red Riding: In the Year of Our Lord 1974","The Girl on the Train","Veronika Decides to Die","Crocodile Dundee","Ultramarines: A Warhammer 40,000 Movie","The I Inside","Beneath Hill 60","Polisse","Awake","Star Wars: Clone Wars: Volume 1","Skin Trade","The Lost Boys","Crazy Heart","The Rose","Baggage Claim","Barbarella","Shipwrecked","Election","The Namesake","The DUFF","Glitter","The Haunting in Connecticut 2: Ghosts of Georgia","Silmido","Bright Star","My Name Is Khan","All Is Lost","Limbo","Namastey London","The Wind That Shakes the Barley","Yeh Jawaani Hai Deewani","Quo Vadis","Repo! The Genetic Opera","Valley of the Wolves: Iraq","Pulp Fiction","The Muppet Movie","Nightcrawler","Club Dread","The Sound of Music","Splash","Little Miss Sunshine","Stand by Me","28 Days Later","You Got Served","Escape from Alcatraz","Brown Sugar","A Thin Line Between Love and Hate","50/50","Shutter","That Awkward Moment","Modern Problems","Kicks","Much Ado About Nothing","On Her Majesty's Secret Service","New Nightmare","Drive Me Crazy","Akeelah and the Bee","Half Baked","New in Town","American Psycho","The Good Girl","Bon Cop Bad Cop","The Boondock Saints II: All Saints Day","The City of Your Final Destination","Enough Said","Easy A","The Inkwell","Shadow of the Vampire","Prom","The Pallbearer","Held Up","Woman on Top","Howards End","Anomalisa","Another Year","8 Women","Showdown in Little Tokyo","Clay Pigeons","It's Kind of a Funny Story","Made in Dagenham","When Did You Last See Your Father?","Prefontaine","The Wicked Lady","The Secret of Kells","Begin Again","Down in the Valley","Brooklyn Rules","Restless","The Singing Detective","The Land Girls","Fido","The Wendell Baker Story","Wild Target","Pathology","Wuthering Heights","10th & Wolf","Dear Wendy","Aloft","Akira","The Death and Life of Bobby Z","The Rocket: The Legend of Rocket Richard","Swelter","My Lucky Star","Imagine Me & You","Mr. Church","Swimming Pool","Green Street Hooligans: Underground","The Blood of Heroes","Code of Honor","Driving Miss Daisy","Soul Food","Rumble in the Bronx","Far from Men","Thank You for Smoking","Hostel: Part II","An Education","Shopgirl","The Hotel New Hampshire","Narc","Men with Brooms","Witless Protection","The Work and the Glory","Extract","Masked and Anonymous","Betty Fisher and Other Stories","Code 46","Outside Bet","Albert Nobbs","Black November","Ta Ra Rum Pum","Persepolis","The Hole","The Wave","The Neon Demon","Harry Brown","The Omega Code","Juno","Pound of Flesh","Diamonds Are Forever","The Godfather","Flashdance","(500) Days of Summer","The Piano","Magic Mike","Darkness Falls","Live and Let Die","My Dog Skip","Definitely, Maybe","Jumping the Broom","Good Night, and Good Luck.","Capote","Desperado","Logan's Run","The Man with the Golden Gun","Action Jackson","The Descent","Michael Jordan to the Max","Devil's Due","Flirting with Disaster","The Devil's Rejects","Dope","In Too Deep","House of 1000 Corpses","Alien Zone","A Serious Man","Get Low","Warlock","Beyond the Lights","A Single Man","The Last Temptation of Christ","Outside Providence","Bride & Prejudice","Rabbit-Proof Fence","Who's Your Caddy?","Split Second","The Other Side of Heaven","Veer-Zaara","Redbelt","Cyrus","A Dog Of Flanders","Auto Focus","Factory Girl","We Need to Talk About Kevin","The Christmas Candle","The Mighty Macs","Losin' It","Mother and Child","March or Die","The Visitors","Somewhere","I Hope They Serve Beer in Hell","Chairman of the Board","Hesher","Dom Hemingway","Gerry","The Heart of Me","Freeheld","The Extra Man","Hard to Be a God","Ca$h","Wah-Wah","The Boondock Saints","Z Storm","Twixt","The Snow Queen","Alpha and Omega: The Legend of the Saw Tooth Cave","Pale Rider","Stargate: The Ark of Truth","Dazed and Confused","High School Musical 2","Two Lovers and a Bear","Criminal Activities","Aimee & Jaguar","The Chumscrubber","Shade","House at the End of the Street","Incendies","Remember Me, My Love","Perrier's Bounty","Elite Squad","Annabelle","Bran Nue Dae","Boyz n the Hood","La Bamba","The Four Seasons","Dressed to Kill","The Adventures of Huck Finn","Go","Friends with Money","The Andromeda Strain","Bats","Nowhere in Africa","Shame","Layer Cake","The Work and the Glory II: American Zion","The East","A Home at the End of the World","Aberdeen","The Messenger","Tracker","Control","The Terminator","Good bye, Lenin!","The Damned United","The Return of the Living Dead","Mallrats","Grease","Platoon","Fahrenheit 9/11","Butch Cassidy and the Sundance Kid","Mary Poppins","Ordinary People","West Side Story","Caddyshack","The Brothers","The Wood","The Usual Suspects","A Nightmare on Elm Street 5: The Dream Child","National Lampoon's Van Wilder","The Wrestler","Duel in the Sun","Best in Show","Escape from New York","School Daze","Daddy Day Camp","Mr. Nice Guy","A Mighty Wind","Mystic Pizza","Sliding Doors","Tales from the Hood","The Last King of Scotland","Halloween 5: The Revenge of Michael Myers","Bernie","Dolphins and Whales: Tribes of the Ocean","Pollock","200 Cigarettes","The Words","Casa De Mi Padre","City Island","The Guard","College","The Virgin Suicides","Little Voice","Miss March","Wish I Was Here","Simply Irresistible","Hedwig and the Angry Inch","Only the Strong","Goddess of Love","Shattered Glass","Novocaine","The Business of Strangers","The Wild Bunch","The Wackness","The First Great Train Robbery","Morvern Callar","Beastmaster 2: Through the Portal of Time","The 5th Quarter","The Flower of Evil","The Greatest","Snow Flower and the Secret Fan","Come Early Morning","Lucky Break","Julia","Surfer, Dude","Lake of Fire","11:14","Men of War","Don McKay","Deadfall","A Shine of Rainbows","The Hit List","Emma","Videodrome","The Spanish Apartment","Song One","Winter in Wartime","Freaky Deaky","The Train","Trade Of Innocents","The Protector","Stiff Upper Lips","Bend It Like Beckham","Sunshine State","Crossover","Khiladi 786","[REC]²","Standing Ovation","The Sting","Chariots of Fire","Diary of a Mad Black Woman","Shine","Don Jon","High Plains Drifter","Ghost World","Iris","Galaxina","The Chorus","Mambo Italiano","Wonderland","Do the Right Thing","Harvard Man","Le Havre","Irreversible","R100","Rang De Basanti","Animals","Salvation Boulevard","The Ten","A Room for Romeo Brass","Headhunters","Grabbers","Saint Ralph","Miss Julie","Somewhere in Time","Dum Maaro Dum","Insidious: Chapter 2","Saw II","10 Cloverfield Lane","Jackass: The Movie","Lights Out","Paranormal Activity 3","Ouija","A Nightmare on Elm Street 3: Dream Warriors","Instructions Not Included","Paranormal Activity 4","The Robe","The Return of the Pink Panther","Freddy's Dead: The Final Nightmare","Monster","20,000 Leagues Under the Sea","Paranormal Activity: The Marked Ones","The Elephant Man","Dallas Buyers Club","The Lazarus Effect","Memento","Oculus","Clerks II","Billy Elliot","The Way Way Back","House Party 2","The Man from Snowy River","Doug's 1st Movie","The Apostle","Mommie Dearest","Our Idiot Brother","Race","The Players Club","As Above, So Below","Addicted","Eve's Bayou","Still Alice","The Egyptian","Nighthawks","Friday the 13th Part VIII: Jason Takes Manhattan","My Big Fat Greek Wedding","Spring Breakers","Halloween: The Curse of Michael Myers","Y Tu Mamá También","Shaun of the Dead","The Haunting of Molly Hartley","Lone Star","Halloween 4: The Return of Michael Myers","April Fool's Day","Diner","Lone Wolf McQuade","Apollo 18","Sunshine Cleaning","No Escape","The Beastmaster","Solomon and Sheba","Fifty Shades of Black","Not Easily Broken","A Farewell to Arms","The Perfect Match","Digimon: The Movie","Saved!","The Barbarian Invasions","Robin and Marian","The Forsaken","Force 10 from Navarone","UHF","Grandma's Boy","Slums of Beverly Hills","Once Upon a Time in the West","Made","Moon","Keeping Up with the Steins","Sea Rex 3D: Journey to a Prehistoric World","The Sweet Hereafter","Of Gods and Men","Bottle Shock","Jekyll and Hyde ... Together Again","Heavenly Creatures","90 Minutes in Heaven","Everything Must Go","Zero Effect","The Machinist","Light Sleeper","Kill the Messenger","Rabbit Hole","Party Monster","Green Room","The Oh in Ohio","Atlas Shrugged Part III: Who is John Galt?","Bottle Rocket","Albino Alligator","Gandhi, My Father","Standard Operating Procedure","Out of the Blue","Tucker and Dale vs Evil","Lovely, Still","Tycoon","Desert Blue","Decoys","The Visit","Redacted","Fascination","Area 51","Sleep Tight","The Cottage","Dead Like Me: Life After Death","Farce of the Penguins","Flying By","Rudderless","Henry & Me","Christmas Eve","We Have Your Husband","Dying of the Light","Born Of War","Capricorn One","Should've Been Romeo","Running Forever","Yoga Hosers","Navy Seals vs. Zombies","I Served the King of England","Soul Kitchen","Sling Blade","The Awakening","Hostel","A Cock and Bull Story","Take Shelter","Lady in White","Driving Lessons","Let's Kill Ward's Wife","The Texas Chainsaw Massacre 2","Pat Garrett & Billy the Kid","Only God Forgives","Camping Sauvage","Without Men","Dear Frankie","All Hat","The Names of Love","Treading Water","Savage Grace","Out of the Blue","Police Academy","The Blue Lagoon","Four Weddings and a Funeral","Fast Times at Ridgemont High","Moby Dick","25th Hour","Bound","Requiem for a Dream","State Fair","Tango","Salvador","Moms' Night Out","Donnie Darko","Saving Private Perez","Character","Spun","Life During Wartime","Sympathy for Lady Vengeance","Mozart's Sister","Mean Machine","Exiled","Blackthorn","Lilya 4-ever","After.Life","Fugly","One Flew Over the Cuckoo's Nest","R.L. Stine's Monsterville: The Cabinet of Souls","Silent Movie","Airlift","Anne of Green Gables","Falcon Rising","The Sweeney","Sexy Beast","Easy Money","Whale Rider","Paa","Cargo","High School Musical","Love and Death on Long Island","Night Watch","The Crying Game","Porky's","Survival of the Dead","Night of the Living Dead","Lost in Translation","Annie Hall","The Greatest Show on Earth","Monster's Ball","Maggie","Leaving Las Vegas","Hansel and Gretel Get Baked","The Front Page","The Boy Next Door","Trapeze","The Kids Are All Right","They Live","The Great Escape","What the #$*! Do We (K)now!?","The Last Exorcism Part II","Boyhood","Scoop","The Wash","3 Strikes","The Cooler","The Misfits","The Night Listener","The Jerky Boys","The Orphanage","A Haunted House 2","The Rules of Attraction","Topaz","Let's Go to Prison","Four Rooms","Secretary","The Real Cancun","Talk Radio","Waiting for Guffman","Love Stinks","You Kill Me","Thumbsucker","Red State","Mirrormask","Samsara","The Barbarians","The Art of Getting By","Zipper","Poolhall Junkies","The Loss of Sexual Innocence","Holy Motors","Joe","Shooting Fish","Prison","Psycho Beach Party","The Big Tease","Guten Tag, Ramón","Trust","An Everlasting Piece","Among Giants","Adore","The Velocity of Gary","Mondays in the Sun","Stake Land","The Last Time I Committed Suicide","Futuro Beach","Another Happy Day","A Lonely Place to Die","Nothing","The Geographer Drank His Globe Away","1776","Inescapable","Hell's Angels","Purple Violets","The Veil","The Loved Ones","The Helpers","How to Fall in Love","The Perfect Wave","A Man for All Seasons","Network","Gone with the Wind","Desert Dancer","Major Dundee","Annie Get Your Gun","Four Lions","The House of Sand","Defendor","The Pirate","The Good Heart","The History Boys","Midnight Cowboy","The Full Monty","Airplane!","Chain of Command","Friday","Menace II Society","Creepshow 2","The Ballad of Cable Hogue","In Cold Blood","The Nun's Story","Harper","Frenzy","The Witch","I Got the Hook Up","She's the One","Gods and Monsters","The Secret in Their Eyes","Train","Evil Dead II","Pootie Tang","Sharknado","The Other Conquest","Troll Hunter","Ira & Abby","Winter Passing","D.E.B.S.","The Masked Saint","The Betrayed","Taxman","The Secret","2:13","Batman: The Dark Knight Returns, Part 2","Time to Choose","In the Name of the King III","Wicked Blood","Stranded","Lords of London","High Anxiety","March of the Penguins","Margin Call","August","Choke","Whiplash","City of God","Human Traffic","To Write Love on Her Arms","The Dead Girl","The Hunt","A Christmas Story","Bella","Class of 1984","The Opposite Sex","Dreaming of Joseph Lees","The Class","Rosemary's Baby","The Man Who Shot Liberty Valance","Adam","Maria Full of Grace","Beginners","Feast","Animal House","Goldfinger","Antiviral","It's a Wonderful Life","Trainspotting","The Original Kings of Comedy","Paranormal Activity 2","Waking Ned","Bowling for Columbine","Coming Home","A Nightmare on Elm Street Part 2: Freddy's Revenge","A Room with a View","The Purge","Sinister","Martin Lawrence Live: Runteldat","Cat on a Hot Tin Roof","Beneath the Planet of the Apes","Air Bud","Pokémon: Spell of the Unknown","Friday the 13th Part VI: Jason Lives","The Bridge on the River Kwai","Spaced Invaders","Family Plot","The Apartment","Jason Goes to Hell: The Final Friday","Torn Curtain","Dave Chappelle's Block Party","Slow West","Krush Groove","Next Day Air","Elmer Gantry","Judgment at Nuremberg","Trippin'","Red River","Phat Girlz","Before Midnight","Teen Wolf Too","Phantasm II","Woman Thou Art Loosed","Real Women Have Curves","Water","East Is East","Whipped","Kama Sutra - A Tale of Love","Please Give","Willy Wonka & the Chocolate Factory","Warlock: The Armageddon","8 Heads in a Duffel Bag","Days of Heaven","Thirteen Conversations About One Thing","Jawbreaker","Basquiat","Frances Ha","Tsotsi","Happiness","DysFunktional Family","Tusk","Oldboy","Letters to God","Hobo with a Shotgun","Compadres","Freeway","Love's Abiding Joy","Fish Tank","Damsels in Distress","Creature","Bachelorette","Brave New Girl","Tim and Eric's Billion Dollar Movie","Summer Storm","Fort McCoy","Chain Letter","Just Looking","The Divide","The Eclipse","Demonic","My Big Fat Independent Movie","The Deported","Tanner Hall","Open Road","They Came Together","30 Nights of Paranormal Activity With the Devil Inside the Girl With the Dragon Tattoo","Never Back Down 2: The Beatdown","Point Blank","Four Single Fathers","Enter the Dangerous Mind","Something Wicked","AWOL-72","Iguana","Chicago Overcoat","Barry Munday","Central Station","Pocketful of Miracles","Close Range","Boynton Beach Club","Amnesiac","Freakonomics","High Tension","Griff the Invisible","Unnatural","Hustle & Flow","Some Like It Hot","Friday the 13th Part VII: The New Blood","The Wizard of Oz","Young Frankenstein","Diary of the Dead","Lage Raho Munna Bhai","Ulee's Gold","The Black Stallion","Sardaarji","Journey to Saturn","Donovan's Reef","The Dress","A Guy Named Joe","Blazing Saddles","Friday the 13th: The Final Chapter","Ida","Maurice","Beer League","Riding Giants","Timecrimes","Silver Medalist","Timber Falls","Singin' in the Rain","Fat, Sick & Nearly Dead","A Haunted House","2016: Obama's America","That Thing You Do!","Halloween III: Season of the Witch","Escape from the Planet of the Apes","Hud","Kevin Hart: Let Me Explain","My Own Private Idaho","Garden State","Before Sunrise","Evil Words","Jesus' Son","Saving Face","Brick Lane","Robot & Frank","My Life Without Me","The Spectacular Now","Religulous","Fuel","Valley of the Heart's Delight","Eye of the Dolphin","8: The Mormon Proposition","The Other End of the Line","Anatomy","Sleep Dealer","Super","Christmas Mail","Stung","Antibirth","Get on the Bus","Thr3e","Idiocracy","The Rise of the Krays","This Is England","U.F.O.","Bathing Beauty","Go for It!","Dancer, Texas Pop. 81","Show Boat","Redemption Road","The Calling","The Brave Little Toaster","Fantasia","8 Days","Friday the 13th Part III","Friday the 13th: A New Beginning","The Last Sin Eater","Do You Believe?","Impact Point","The Valley of Decision","Eden","Chicken Tikka Masala","There's Always Woodstock","Jack Brooks: Monster Slayer","The Best Years of Our Lives","Bully","Elling","Mi America","[REC]","Lies in Plain Sight","Sharkskin","Containment","The Timber","From Russia with Love","The Toxic Avenger Part II","Sleeper","It Follows","Everything You Always Wanted to Know About Sex *But Were Afraid to Ask","To Kill a Mockingbird","Mad Max 2: The Road Warrior","The Legend of Drunken Master","Boys Don't Cry","Silent House","The Lives of Others","Courageous","The Hustler","Boom Town","The Triplets of Belleville","Smoke Signals","American Splendor","Before Sunset","Amores perros","Thirteen","Gentleman's Agreement","Winter's Bone","Touching the Void","Alexander's Ragtime Band","Me and You and Everyone We Know","Inside Job","We Are Your Friends","Ghost Dog: The Way of the Samurai","Harsh Times","Captive","Full Frontal","Witchboard","Shortbus","Waltz with Bashir","The Book of Mormon Movie, Volume 1: The Journey","No End in Sight","The Diary of a Teenage Girl","In the Shadow of the Moon","Meek's Cutoff","Inside Deep Throat","Dinner Rush","Clockwatchers","The Virginity Hit","Subway","House of D","Teeth","Six-String Samurai","Hum To Mohabbat Karega","It's All Gone Pete Tong","Saint John of Las Vegas","24 7: Twenty Four Seven","Stonewall","Roadside Romeo","This Thing of Ours","The Lost Medallion: The Adventures of Billy Stone","The Last Five Years","The Missing Person","Return of the Living Dead 3","London","Sherrybaby","Circle","Eden Lake","Plush","Lesbian Vampire Killers","Gangster's Paradise: Jerusalema","Freeze Frame","Grave Encounters","Stitches","Nine Dead","To Be Frank, Sinatra at 100","Bananas","Supercapitalist","Rockaway","The Lady from Shanghai","No Man's Land: The Rise of Reeker","Highway","Small Apartments","Coffee Town","The Ghastly Love of Johnny X","All Is Bright","The Torture Chamber of Dr. Sadism","Straight A's","A Funny Thing Happened on the Way to the Forum","Slacker Uprising","The Legend of Hell's Gate: An American Conspiracy","The Walking Deceased","The Curse of Downers Grove","Shark Lake","River's Edge","Northfork","The Marine 4: Moving Target","Buried","Submarine","The Square","One to Another","ABCD (Any Body Can Dance)","Man on Wire","Abandoned","Brotherly Love","The Last Exorcism","Nowhere Boy","A Streetcar Named Desire","Dr. Strangelove or: How I Learned to Stop Worrying and Love the Bomb","The Crime of Padre Amaro","Beasts of the Southern Wild","Battle for the Planet of the Apes","Songcatcher","Higher Ground","Vaalu","The Greatest Movie Ever Sold","Ed and His Dead Mother","Travellers and Magicians","Hang 'em High","Deadline - U.S.A.","Sublime","A Beginner's Guide to Snuff","Independence Daysaster","Dysfunctional Friends","Run Lola Run","May","Against the Wild","Under the Same Moon","Conquest of the Planet of the Apes","In the Bedroom","I Spit on Your Grave","Happy, Texas","My Summer of Love","The Lunchbox","Yes","You Can't Take It With You","From Here to Eternity","She Wore a Yellow Ribbon","Grace Unplugged","Foolish","N-Secure","Caramel","Out of the Dark","The Bubble","The Conversation","Dil Jo Bhi Kahey...","Mississippi Mermaid","I Love Your Work","Cabin Fever","Waitress","Bloodsport","Mr. Smith Goes to Washington","Kids","The Squid and the Whale","Kissing Jessica Stein","Kickboxer: Vengeance","Spellbound","Exotica","Buffalo '66","Insidious","Repo Man","Nine Queens","The Gatekeepers","The Ballad of Jack and Rose","The To Do List","Killing Zoe","The Believer","Snow Angels","Unsullied","Session 9","I Want Someone to Eat Cheese With","Mooz-lum","Hatchet","Modern Times","Stolen Summer","My Name Is Bruce","The Salon","Road Hard","Forty Shades of Blue","Amigo","Pontypool","Trucker","Me You and Five Bucks","The Lords of Salem","Housebound","Wal-Mart: The High Cost of Low Price","Fetching Cody","Last I Heard","Closer to the Moon","Mutant World","Growing Up Smith","Checkmate","#Horror","Wind Walkers","Snow White and the Seven Dwarfs","The Holy Girl","Shalako","Incident at Loch Ness","The Dog Lover","GirlHouse","The Blue Room","House at the End of the Drive","Batman","Lock, Stock and Two Smoking Barrels","The Ballad of Gregorio Cortez","The Celebration","Trees Lounge","Journey from the Fall","The Basket","Eddie: The Sleepwalking Cannibal","Queen of the Mountains","Def-Con 4","The Hebrew Hammer","Neal 'n' Nikki","The 41–Year–Old Virgin Who Knocked Up Sarah Marshall and Felt Superbad About It","Forget Me Not","Rebecca","Friday the 13th Part 2","The Lost Weekend","C.H.U.D.","Filly Brown","The Lion of Judah","Niagara","How Green Was My Valley","Da Sweet Blood of Jesus","Sex, Lies, and Videotape","Saw","Super Troopers","The Algerian","The Amazing Catfish","Monsoon Wedding","You Can Count on Me","The Trouble with Harry","But I'm a Cheerleader","Home Run","Reservoir Dogs","The Blue Bird","The Good, the Bad and the Ugly","The Second Mother","Blue Like Jazz","Down & Out With The Dolls","Pink Ribbons, Inc.","Certifiably Jonathan","Desire","The Blade of Don Juan","Grand Theft Parsons","Extreme Movie","The Charge of the Light Brigade","Below Zero","Crowsnest","Airborne","Cotton Comes to Harlem","The Wicked Within","Bleeding Hearts","Waiting...","Dead Man's Shoes","From a Whisper to a Scream","Sex With Strangers","Dracula: Pages from a Virgin's Diary","Faith Like Potatoes","Beyond the Black Rainbow","The Raid","The Dead Undead","The Vatican Exorcisms","Casablanca","Lake Mungo","Rocket Singh: Salesman of the Year","Silent Running","Rocky","The Sleepwalker","Tom Jones","Unfriended","Taxi Driver","The Howling","Dr. No","Chernobyl Diaries","Hellraiser","God's Not Dead 2","Cry_Wolf","Godzilla 2000","Blue Valentine","Transamerica","The Devil Inside","Beyond the Valley of the Dolls","Love Me Tender","An Inconvenient Truth","Sands of Iwo Jima","Shine a Light","The Green Inferno","Departure","The Sessions","Food, Inc.","October Baby","Next Stop Wonderland","The Skeleton Twins","Martha Marcy May Marlene","Obvious Child","Frozen River","20 Feet from Stardom","Two Girls and a Guy","Walking and Talking","Who Killed the Electric Car?","The Broken Hearts Club: A Romantic Comedy","Bubba Ho-tep","Slam","Brigham City","Fiza","Orgazmo","All the Real Girls","Dream with the Fishes","Blue Car","Palo Alto","Ajami","Wristcutters: A Love Story","I Origins","The Battle of Shaker Heights","The Act of Killing","Taxi to the Dark Side","Once in a Lifetime: The Extraordinary Story of the New York Cosmos","Guiana 1838","Lisa Picard Is Famous","Antarctica: A Year on Ice","A LEGO Brickumentary","Hardflip","Chocolate: Deep Dark Secrets","The House of the Devil","The Perfect Host","Safe Men","Speedway Junky","The Last Big Thing","The Specials","16 to Life","Alone With Her","Creative Control","Special","Sparkler","The Helix... Loaded","In Her Line of Fire","The Jimmy Show","Heli","Karachi se Lahore","Loving Annabelle","Hits","Jimmy and Judy","Frat Party","The Party's Over","Proud","The Poker House","Childless","ZMD: Zombies of Mass Destruction","Snow White: A Deadly Summer","Hidden Away","My Last Day Without You","Steppin: The Movie","Doc Holliday's Revenge","Black Rock","Truth or Dare","The Pet","Bang Bang Baby","Fear Clinic","Zombie Hunter","A Fine Step","Charly","Banshee Chapter","Ask Me Anything","And Then Came Love","Food Chains","On the Waterfront","L!fe Happens","4 Months, 3 Weeks and 2 Days","The Horror Network Vol. 1","Hard Candy","The Quiet","Circumstance","Fruitvale Station","The Brass Teapot","Bambi","The Hammer","Latter Days","Elza","1982","For a Good Time, Call...","Celeste & Jesse Forever","Time Changer","London to Brighton","American Hero","Windsor Drive","A Separation","Crying with Laughter","Welcome to the Dollhouse","Ruby in Paradise","Raising Victor Vargas","Pandora's Box","Harrison Montgomery","Live-In Maid","Deterrence","The Mudge Boy","The Young Unknowns","Not Cool","Dead Snow","Saints and Soldiers","Vessel","American Graffiti","Iraq for Sale: The War Profiteers","Aqua Teen Hunger Force Colon Movie Film for Theaters","Safety Not Guaranteed","Kevin Hart: Laugh at My Pain","Kill List","The Innkeepers","The Conformist","Interview with the Assassin","Donkey Punch","All the Boys Love Mandy Lane","Bled","High Noon","Hoop Dreams","Rize","L.I.E.","The Sisterhood of Night","B-Girl","Half Nelson","Naturally Native","Hav Plenty","Adulterers","Escape from Tomorrow","Starsuckers","The Hadza:  Last of the First","After","Treachery","Walter","Top Hat","The Blair Witch Project","Woodstock","The Kentucky Fried Movie","Mercy Streets","Carousel of Revenge","Broken Vessels","Water & Power","They Will Have to Kill Us First","Light from the Darkroom","The Country Doctor","The Maid's Room","A Hard Day's Night","The Harvest (La Cosecha)","Love Letters","Juliet and Alfa Romeo","Fireproof","Faith Connections","Benji","Open Water","High Road","Kingdom of the Spiders","Mad Hot Ballroom","The Station Agent","To Save A Life","Wordplay","Beyond the Mat","The Singles Ward","Osama","Sholem Aleichem: Laughing In The Darkness","Groove","The R.M.","Twin Falls Idaho","Mean Creek","Hurricane Streets","Never Again","Civil Brand","Lonesome Jim","Drinking Buddies","Deceptive Practice: The Mysteries and Mentors of Ricky Jay","Seven Samurai","The Other Dream Team","Johnny Suede","Finishing The Game","Rubber","Kiss the Bride","The Slaughter Rule","Monsters","The Californians","The Living Wake","Detention of the Dead","Crazy Stone","Scott Walker: 30 Century Man","Everything Put Together","Good Kill","The Outrageous Sophie Tucker","Now Is Good","Girls Gone Dead","America Is Still the Place","Subconscious","Enter Nowhere","El Rey de Najayo","Fight to the Finish","Alleluia! The Devil's Carnival","The Sound and the Shadow","Rodeo Girl","Born to Fly: Elizabeth Streb vs. Gravity","The Little Ponderosa Zoo","The Toxic Avenger","Straight Out of Brooklyn","Bloody Sunday","Diamond Ruff","Conversations with Other Women","Poultrygeist: Night of the Chicken Dead","Mutual Friends","42nd Street","Rise of the Entrepreneur: The Search for a Better Way","Metropolitan","As It Is in Heaven","Roadside","Napoleon Dynamite","Blue Ruin","Paranormal Activity","Dogtown and Z-Boys","Monty Python and the Holy Grail","Quinceañera","Gory Gory Hallelujah","Tarnation","I Want Your Money","Love in the Time of Monsters","The Beyond","What Happens in Vegas","The Dark Hours","My Beautiful Laundrette","Fabled","Show Me","Cries and Whispers","Intolerance","Trekkies","The Broadway Melody","The Evil Dead","Maniac","Censored Voices","Murderball","American Ninja 2: The Confrontation","51 Birch Street","Rotor DR1","12 Angry Men","My Dog Tulip","It Happened One Night","Dogtooth","Tupac: Resurrection","Tumbleweeds","The Prophecy","When the Cat's Away","Pieces of April","The Big Swap","Old Joy","Wendy and Lucy","3 Backyards","Pierrot le Fou","Sisters in Law","Ayurveda: Art of Being","Nothing But a Man","First Love, Last Rites","Fighting Tommy Riley","Royal Kill","The Looking Glass","Death Race 2000","Locker 13","Midnight Cabaret","Anderson's Cross","Bizarre","Graduation Day","Some Guy Who Kills People","Compliance","Chasing Amy","Lovely & Amazing","Death Calls","Better Luck Tomorrow","The Incredibly True Adventure of Two Girls In Love","Chuck & Buck","American Desi","Amidst the Devil's Wings","Cube","Love and Other Catastrophes","I Married a Strange Person!","November","Like Crazy","Teeth and Blood","Sugar Town","The Motel","The Canyons","On the Outs","Shotgun Stories","Exam","The Sticky Fingers of Time","Sunday School Musical","Rust","Ink","The Christmas Bunny","Butterfly","UnDivided","The Frozen","Horse Camp","Give Me Shelter","The Big Parade","Little Big Top","Along the Roadside","Bronson","Western Religion","Burn","Urbania","The Stewardesses","The Beast from 20,000 Fathoms","Mad Max","Swingers","A Fistful of Dollars","She Done Him Wrong","Short Cut to Nirvana: Kumbh Mela","The Grace Card","Middle of Nowhere","Three","The Business of Fancydancing","Call + Response","Malevolence","Reality Show","Super Hybrid","Baghead","American Beast","The Case of the Grinning Cat","Ordet","Good Dick","The Man from Earth","The Trials Of Darryl Hunt","Samantha: An American Girl Holiday","Yesterday Was a Lie","Theresa Is a Mother","H.","Archaeology of a Woman","Children of Heaven","Weekend","She's Gotta Have It","Butterfly Girl","The World Is Mine","Another Earth","Sweet Sweetback's Baadasssss Song","Perfect Cowboy","Tadpole","Once","The Woman Chaser","The Horse Boy","When the Lights Went Out","Heroes of Dirt","A Charlie Brown Christmas","Antarctic Edge: 70° South","Aroused","Top Spin","Roger & Me","An American in Hollywood","Sound of My Voice","The Blood of My Brother: A Story of Death in Iraq","Your Sister's Sister","A Dog's Breakfast","The Married Woman","The Birth of a Nation","The Work and The Story","Facing the Giants","The Gallows","Eraserhead","Hollywood Shuffle","The Mighty","Penitentiary","The Lost Skeleton of Cadavra","Dude Where's My Dog?","Cheap Thrills","Indie Game: The Movie","Straightheads","Open Secret","Echo Dr.","The Night Visitor","The Past Is a Grotesque Animal","Peace, Propaganda & the Promised Land","Pi","I Love You, Don't Touch Me!","20 Dates","Queen Crab","Super Size Me","The FP","Happy Christmas","The Brain That Wouldn't Die","Tiger Orange","Supporting Characters","Absentia","The Brothers McMullen","The Dirties","Gabriela","Tiny Furniture","Hayride","The Naked Ape","Counting","The Call of Cthulhu","Bending Steel","The Signal","The Image Revolution","This Is Martin Bonner","A True Story","George Washington","Smiling Fish & Goat On Fire","Dawn of the Crescent Moon","Raymond Did It","The Last Waltz","Run, Hide, Die","The Exploding Girl","The Legend of God's Gun","Mutual Appreciation","Her Cry: La Llorona Investigation","Down Terrace","Clerks","Pink Narcissus","Funny Ha Ha","In the Company of Men","Manito","Rampage","Slacker","Dutch Kills","Dry Spell","Flywheel","Backmask","The Puffy Chair","Stories of Our Lives","Breaking Upwards","All Superheroes Must Die","Pink Flamingos","Clean","The Circle","Tin Can Man","Cure","On The Downlow","Sanctuary: Quite a Conundrum","Bang","Primer","Cavite","El Mariachi","Newlyweds","Signed, Sealed, Delivered","Shanghai Calling","My Date with Drew",]
        
        
function checkSimilarity(){
    filtered_names = []
    var str1 = document.getElementById("movie_name").value;
    for(var i=0;i<all_titles.length;i++){
        var str2 = all_titles[i];
        var score = similarity(str1, str2);
        if(score>0.50){
            filtered_names.push(str2+'<br />');
        }
    }
    if(filtered_names.length<1){
        document.getElementById("suggestions").innerHTML = "Please try again. Either input movie name is misspelled badly or not present in database.";
    }else{
        document.getElementById("suggestions").innerHTML = filtered_names;  
    }
}

function similarity(s1, s2) {
      var longer = s1;
      var shorter = s2;
      if (s1.length < s2.length) {
        longer = s2;
        shorter = s1;
      }
      var longerLength = longer.length;
      if (longerLength == 0) {
        return 1.0;
      }
      return (longerLength - editDistance(longer, shorter)) / parseFloat(longerLength);
    }

    function editDistance(s1, s2) {
      s1 = s1.toLowerCase();
      s2 = s2.toLowerCase();

      var costs = new Array();
      for (var i = 0; i <= s1.length; i++) {
        var lastValue = i;
        for (var j = 0; j <= s2.length; j++) {
          if (i == 0)
            costs[j] = j;
          else {
            if (j > 0) {
              var newValue = costs[j - 1];
              if (s1.charAt(i - 1) != s2.charAt(j - 1))
                newValue = Math.min(Math.min(newValue, lastValue),
                  costs[j]) + 1;
              costs[j - 1] = lastValue;
              lastValue = newValue;
            }
          }
        }
        if (i > 0)
          costs[s2.length] = lastValue;
      }
      return costs[s2.length];
    }
        
    checkSimilarity()

function randomNum()
        {
            "use strict";
            return Math.floor(Math.random() * 9)+1;
        }
            var loop1,loop2,loop3,time=30, i=0, number, selector3 = document.querySelector('.thirdDigit'), selector2 = document.querySelector('.secondDigit'),
                selector1 = document.querySelector('.firstDigit');
            loop3 = setInterval(function()
            {
              "use strict";
                if(i > 40)
                {
                    clearInterval(loop3);
                    selector3.textContent = 4;
                }else
                {
                    selector3.textContent = randomNum();
                    i++;
                }
            }, time);
            loop2 = setInterval(function()
            {
              "use strict";
                if(i > 80)
                {
                    clearInterval(loop2);
                    selector2.textContent = 0;
                }else
                {
                    selector2.textContent = randomNum();
                    i++;
                }
            }, time);
            loop1 = setInterval(function()
            {
              "use strict";
                if(i > 100)
                {
                    clearInterval(loop1);
                    selector1.textContent = 4;
                }else
                {
                    selector1.textContent = randomNum();
                    i++;
                }
            }, time);
</script>

</body>
</html>
```





