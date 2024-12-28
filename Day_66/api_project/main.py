from random import choice
import json
import load_dotenv
import os
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean

app = Flask(__name__)

# CREATE DB


class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=["GET"])
def random():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = choice(all_cafes)
    # return jsonify(cafe={
    #     "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #     "has_sockets": random_cafe.has_sockets,
    #     "has_toilet": random_cafe.has_toilet,
    #     "has_wifi": random_cafe.has_wifi,
    #     "can_take_calls": random_cafe.can_take_calls,
    #     "seats": random_cafe.seats,
    #     "coffee_price": random_cafe.coffee_price
    # })
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all", methods=["GET"])
def all():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    return jsonify(cafes_info=[cafe.to_dict() for cafe in all_cafes])


@app.route("/search_loc", methods=["GET"])
def search_loc():
    query_loc = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(
        Cafe.location == query_loc)).scalars().all()
    if result:
        return jsonify(cafes=[cafe.to_dict() for cafe in result])
    else:
        return jsonify(error={"No results of that area found": "Error Not Found", "Know a good one?": "Please send details!"})


@app.route("/search_wifi", methods=["GET"])
def search_wifi():
    query_wifi = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(
        Cafe.location == query_wifi and Cafe.has_wifi == 1)).scalars().all()
    if result:
        return jsonify(cafes=[cafe.to_dict() for cafe in result])
    else:
        return jsonify(Error={"No cafes with WiFi found": "Error no Wifi in database"})


@app.route("/add", methods=["GET", "POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.get_or_404(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = new_price  # type: ignore
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


@app.route("/report_closed/<int:cafe_id>", methods=["DELETE"])
def cafe_closed(cafe_id):
    key = os.getenv("KEY")
    if request.args.get("secret_key") == key:
        cafe = db.get_or_404(Cafe, cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"sucess": "The cafe has been removed from the database"}), 200
    elif request.args.get("secret_key") != key:
        return jsonify(response={"Unauthorised": "please check the secret key you used"}), 403
    else:
        return jsonify(response={"Cafe Not Found": "The cafe was not found, please check the id"}), 404

# HTTP GET - Read Record

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record


# HTTP DELETE - Delete Record
if __name__ == '__main__':
    app.run(debug=True)
