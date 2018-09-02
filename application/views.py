from application import app, get_render_page_function

render_page = get_render_page_function('index')


@app.route("/")
def index():
    return render_page("index.html")
