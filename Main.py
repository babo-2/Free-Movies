from imdb import IMDb
from flask import Flask, render_template, jsonify
import json

ia = IMDb()
ia.doAdult = True
app = Flask(__name__)


def encode_(str_):
    return str_.replace("'", "531634").replace('"', "972348")


def search(keyword, amount=24):
    print("searching: " + keyword)
    movies = ia.search_movie_advanced(keyword, results=amount, adult=True)
    movie_list = []

    #print("keys: " + str(movies[0].keys()))
    #print("values: " + str(movies[0].values()))
    for movie in movies:
        thumnail = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/1665px-No-Image-Placeholder.svg.png"
        if "full-size cover url" in movie.keys():
            thumnail = movie["full-size cover url"]
        elif "cover url" in movie.keys():
            thumnail = movie["cover url"]

        if thumnail == "https://m.media-amazon.png":
            thumnail = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/1665px-No-Image-Placeholder.svg.png"

        movie_info = {
            "title": movie["title"],
            "id": movie.getID(),
            "thumbnail": thumnail,
            "year": movie.get("year", "N/A"),
            "type": movie.get("kind", "N/A"),
            "restriction": movie.get("certificates", "N/A"),
            "lenght": movie.get("runtimes", ["0"])[0],
            "genres": movie.get("genres", "N/A"),
            "rating": movie.get("rating", "N/A"),
            "plot":  movie.get("plot", "N/A"),
        }

        movie_list.append(movie_info)

    return movie_list


@app.route("/search/<keyword>", methods=["GET"])
def search_endpoint(keyword):
    results = search(keyword)
    return jsonify(results)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/play/<string:video_id>/<string:season>/<string:episode>")
def play(video_id, season="1", episode="1"):
    movie = ia.get_movie(video_id)
    if movie == None:
        return "Error: " + video_id + " doesn't exist"
    episodes = ""
    url = ""
    if movie.get("kind", "N/A").upper() == "TV SERIES":
        # print(ia.search_episode(movie["title"])[0].keys())
        episodes = [[obj["title"], movie.getID()]
                    for obj in ia.search_episode(movie["title"])]
        url = "https://vidsrc.to/embed/tv/tt" + video_id + "/" + season + "/" + episode
    else:
        url = "https://vidsrc.to/embed/movie/" + video_id
    return render_template("play.html", video_url=url, episodes=encode_(json.dumps(episodes)))


if __name__ == "__main__":
    app.run(debug=True, port="0.0.0.0")
