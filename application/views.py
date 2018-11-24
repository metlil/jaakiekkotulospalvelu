from flask_login import current_user

from application import app, get_render_page_function
from application.stats.models import standings
from application.usergame.models import UserGame

render_page = get_render_page_function('index')


@app.route("/")
def index():
    usergames = []
    if current_user.is_authenticated:
        usergames = UserGame.get_games_for_user(current_user.id)
    return render_page("index.html", standings=standings(), usergames=usergames)
