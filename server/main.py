from flask import Flask, request, render_template
from random import randint
import uuid

app = Flask(__name__)

# Initial list of items
# items = [uuid.uuid4() for i in range(3)]
items = {str(uuid.uuid4()): {"name": ""} for i in range(3)}


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", items=items)

    elif request.method == "POST":
        form_data = request.form
        name = form_data.get("name")

        items[str(uuid.uuid4())] = {"name": name}

        return render_template("list.html", items=items)


@app.delete("/<id>")
def deleteUser(id):
    if items:
        del items[id]
    return render_template("list.html", items=items)


if __name__ == "__main__":
    app.run(debug=True)
