from flask import Flask, request, render_template
from random import randint, choice
import uuid

app = Flask(__name__)

users = {str(uuid.uuid4()): {"name": ""} for i in range(3)}


@app.get("/")
def index():
    return render_template("index.jinja", users=users)


@app.post("/")
def newUser():
    form_data = request.form
    name = form_data.get("name")

    users[str(uuid.uuid4())] = {"name": name}

    return render_template("partials/users-list.jinja", users=users)


@app.delete("/<id>")
def deleteUser(id):
    if users:
        del users[id]

    return render_template("partials/users-list.jinja", users=users)


@app.get("/random-number")
def testPost():
    n = randint(0, 1024)

    return render_template("partials/number.jinja", number=n)


@app.get("/random-name")
def randomName():
    name = choice(["Bob", "Mob", "Lisa", "Pisa", "Jon", "Job"])

    print(name)

    return render_template("partials/name.jinja", name=name)


if __name__ == "__main__":
    app.run(debug=True)
