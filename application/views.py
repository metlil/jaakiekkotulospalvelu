from application import app, get_render_page_function
from application.stats.models import standings

render_page = get_render_page_function('index')


@app.route("/")
def index():
    return render_page("index.html", standings=standings())
