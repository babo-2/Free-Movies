from imdb import Cinemagoer
from flask import Flask, render_template, jsonify, request
import json

ia = Cinemagoer()
ia.doAdult = True
app = Flask(__name__)

CURRENT_MOVIE=None

def search(keyword, amount=5):#the amount is a big bottleneck due to thumbnail only updating with main
    movies = ia.search_movie_advanced(keyword, results=amount, adult=True)
    movie_list = []
    for movie in movies:
        thumnail = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/1665px-No-Image-Placeholder.svg.png"
        ia.update(movie, 'main')
        if "full-size cover url" in movie.keys():
            thumnail = movie["full-size cover url"]
        elif "cover url" in movie.keys():
            thumnail = movie["cover url"]

        if thumnail == "https://m.media-amazon.png":
            thumnail = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/1665px-No-Image-Placeholder.svg.png"

        movie_info = {
            "IsMovie": (movie.get("kind", "N/A").upper() == "MOVIE"),
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
    results = search(keyword, amount=int(request.headers.get("Search-Amount", "3")))
    return jsonify(results)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/play/<string:video_id>/<string:season>/<string:episode>")
def play(video_id, season="1", episode="1"):
    global CURRENT_MOVIE
    if CURRENT_MOVIE and str(CURRENT_MOVIE.getID())==video_id:
        movie=CURRENT_MOVIE.copy()
    else:
        movie = ia.get_movie(video_id)

    if movie == None:
        return "Error: " + video_id + " doesn't exist"
    if movie.get("kind", "N/A").upper() == "TV SERIES":
        if "episodes" not in movie:
            ia.update(movie, "episodes")
        CURRENT_MOVIE=movie.copy()
        episodes = [episode["title"] for episode in movie['episodes'][int(season)].values()]
        url = "https://vidsrc.to/embed/tv/tt" + video_id + "/" + season + "/" + episode
        return render_template("play.html", video_url=url, is_movie=False, title=movie["title"], video_id=video_id, current_season=season, episodes=json.dumps(episodes), seasons=sorted(movie['episodes'].keys(), key=lambda x: (isinstance(x, str), x)))
    else:
        CURRENT_MOVIE=movie.copy()
        url = "https://vidsrc.to/embed/movie/tt" + video_id
        return render_template("play.html", video_url=url, is_movie=True, title=movie["title"])


if __name__ == "__main__":
    app.run(debug=True, port=2235)
