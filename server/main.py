from flask import Flask, request, render_template
from random import randint, choice
from uuid import uuid4
from dataclasses import dataclass

app = Flask(__name__)


@dataclass
class User:
    id = str(uuid4())
    name: str


# users = {
#     str(uuid4()): {"name": "Hello"},
#     str(uuid4()): {"name": "Yes"},
#     str(uuid4()): {"name": "Dog"},
# }

table_columns = ["id", "name"]
users = [User("Benny")]


@app.get("/")
def index():
    print(users)
    return render_template("index.jinja", table_columns=table_columns, users=users)


@app.post("/")
def newUser():
    form_data = request.form
    name = form_data.get("name")

    users.append(User(name))

    return render_template(
        "partials/users-rows.jinja", table_columns=table_columns, users=users
    )


# @app.delete("/<id>")
# def deleteUser(id):
#     if users:
#         del users[id]

#     return render_template("partials/users-list.jinja", users=users)


# @app.get("/random-number")
# def testPost():
#     n = randint(0, 1024)

#     return render_template("partials/number.jinja", number=n)


# @app.get("/random-name")
# def randomName():
#     name = choice(["Bob", "Mob", "Lisa", "Pisa", "Jon", "Job"])

#     print(name)

#     return render_template("partials/name.jinja", name=name)


if __name__ == "__main__":
    app.run(debug=True)
