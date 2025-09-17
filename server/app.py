#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


@app.route('/')
def index():
    return '<h1>Bakery API</h1>'


# ------------------ GET ROUTES ------------------

@app.route('/bakeries')
def bakeries():
    bakeries = Bakery.query.all()
    return make_response(jsonify([b.to_dict() for b in bakeries]), 200)


@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = Bakery.query.get_or_404(id)

    if request.method == 'GET':
        return make_response(jsonify(bakery.to_dict()), 200)

    elif request.method == 'PATCH':
        # update bakery name (or any other attributes sent)
        for attr in request.form:
            setattr(bakery, attr, request.form.get(attr))

        db.session.commit()
        return make_response(jsonify(bakery.to_dict()), 200)


@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    return make_response(jsonify([bg.to_dict() for bg in baked_goods]), 200)


@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    baked_good = BakedGood.query.order_by(BakedGood.price.desc()).first()
    return make_response(jsonify(baked_good.to_dict()), 200)


# ------------------ POST ROUTE ------------------

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    name = request.form.get("name")
    price = request.form.get("price")
    bakery_id = request.form.get("bakery_id")

    if not name or not price or not bakery_id:
        return make_response(jsonify({"error": "Missing required fields"}), 400)

    baked_good = BakedGood(
        name=name,
        price=float(price),
        bakery_id=int(bakery_id)
    )

    db.session.add(baked_good)
    db.session.commit()

    return make_response(jsonify(baked_good.to_dict()), 201)


# ------------------ DELETE ROUTE ------------------

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get_or_404(id)
    db.session.delete(baked_good)
    db.session.commit()

    return make_response(jsonify({"message": "Baked good deleted successfully"}), 200)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
