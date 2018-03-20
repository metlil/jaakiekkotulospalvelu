from flask import Flask, render_template
app = Flask(__name__)

class Item:
    def __init__(self, name):
        self.name = name

nimi = "Essi Esimerkki"

lista = [1, 1, 2, 3, 5, 8, 11]

esineet = []
esineet.append(Item("Eka 111"))
esineet.append(Item("Toka 222"))
esineet.append(Item("Kolmas"))
esineet.append(Item("Neljäs"))

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/demo")
def content():
    return render_template("demo.html", nimi=nimi, lista=lista, 
esineet=esineet)

if __name__ == "__main__":
    app.run(debug=True)


