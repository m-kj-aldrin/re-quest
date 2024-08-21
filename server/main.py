from flask import Flask, request, render_template
from random import randint
from uuid import uuid4
from dataclasses import dataclass

app = Flask(__name__)


@dataclass
class User:
    id = str(uuid4())
    name: str


table_columns = ["id", "name"]
users = [User("Benny")]


@app.get("/")
def index():
    return render_template(
        "index.jinja", table_columns=table_columns, users=users, n=randint(0, 1024)
    )


@app.post("/")
def newUser():
    form_data = request.form
    name = form_data.get("name")

    users.append(User(name))

    return render_template(
        "partials/users-rows.jinja",
        table_columns=table_columns,
        users=users,
    ) + render_template("partials/n.jinja", n=randint(0, 1024))


def dUser(users, id):
    return [user for user in users if user.id != id]


@app.delete("/<id>")
def deleteUser(id):
    if users:
        user_to_remove = next((user for user in users if user.id == id), None)
        if user_to_remove:
            users.remove(user_to_remove)

    return render_template(
        "partials/users-rows.jinja",
        table_columns=table_columns,
        users=users,
    )


if __name__ == "__main__":
    app.run(debug=True)
