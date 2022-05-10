import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

from data import USERS, ORDER, OFFERS
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    email = db.Column(db.String(50))
    role = db.Column(db.String(50))
    phone = db.Column(db.String(50))


class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(250))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(50))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    #user = relationship("User")
    #offer = relationship("Offer")


class Offer(db.Model):
    __tablename__ = 'offer'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    #user = relationship("User")
    #offer = relationship("Order")


def main():
    db.create_all()
    insert_data()
    app.run(debug=False)


def function_json_user(user):
    """ Формат данных при обращение к вьюшке"""
    return User(
         id=user['id'],
         first_name=user['first_name'],
         last_name=user['last_name'],
         age=user['age'],
         email=user['email'],
         role=user['role'],
         phone=user['phone']
     )


def function_json_order(order):
    """ Формат данных при обращение к вьюшке"""
    return Order(
        id=order['id'],
        name=order['name'],
        description=order['description'],
        start_date=datetime.strptime(order['start_date'], '%m/%d/%Y'),  # перевод времени из JSON in python
        end_date=datetime.strptime(order['end_date'], '%m/%d/%Y'),  # перевод времени из JSON in python
        address=order['address'],
        price=order['price'],
        customer_id=order['customer_id'],
        executor_id=order['executor_id']
    )


def function_json_offer(offer):
    """ Формат данных при обращение к вьюшке"""
    return Offer(
        id=offer['id'],
        order_id=offer['order_id'],
        executor_id=offer['executor_id']
    )


def insert_data():
    users = []
    order = []
    offer = []
    for us in USERS:
        users.append(function_json_user(us))
    for ord in ORDER:
        order.append(function_json_order(ord))
    for off in OFFERS:
        offer.append(function_json_offer(off))

    with db.session.begin():
        db.session.add_all(offer)
        db.session.add_all(order)
        db.session.add_all(users)


@app.route('/users/', methods=['GET'])
def users_index():
    """ вьюшка для обработки запросов в таблице User"""
    if request.method == 'GET':
        data = []
        for user in User.query.all():
            data.append({
             "id": user.id,
             "first_name": user.first_name,
             "last_name": user.last_name,
             "age": user.age,
             "email": user.email,
             "role": user.role,
             "phone": user.phone
             }
            )
        return jsonify(data)


@app.route('/users/<int:uid>/', methods=['POST', 'PUT', 'DELETE'])
def users_id(uid):
    """ вьюшка для использования различных методов """
    if request.method == "POST":
        data = request.get_json()
        new_user = function_json_user(data)

        with db.session.begin():
            db.session.add(new_user)

        return '', 201

    elif request.method == "PUT":
        data = request.get_json()
        user = User.query.get(uid)
        user.first_name = data['first_name'],
        user.last_name = data['last_name'],
        user.age = data['age'],
        user.email = data['email'],
        user.role = data['role'],
        user.phone = data['phone']

        with db.session.begin():
            db.session.add(user)

        return '', 203

    elif request.method == 'DELETE':
        user = User.query.get(uid)
        with db.session.begin():
            db.session.delete(user)

        return '', 202


@app.route('/orders/', methods=['GET', 'POST'])
def orders_index():
    """ вьюшка для обработки запросов в таблице Order"""
    if request.method == 'GET':
        data = []
        for order in Order.query.all():
            data.append({
                "id": order.id,
                "name": order.name,
                "description": order.description,
                "start_date": order.start_date,
                "end_date": order.end_date,
                "address": order.address,
                "price": order.price,
                "customer_id": order.customer_id,
                "executor_id": order.executor_id
                }
            )
        return jsonify(data)
    elif request.method == "POST":
        data = request.get_json()
        new_order = Order(
            name=data['name'],
            description=data['description'],
            start_date=datetime.strptime(data['start_date'], '%m/%d/%Y'),  # перевод времени из JSON in python
            end_date=datetime.strptime(data['end_date'], '%m/%d/%Y'),  # перевод времени из JSON in python
            address=data['address'],
            price=data['price'],
            customer_id=data['customer_id'],
            executor_id=data['executor_id']
        )
        with db.session.begin():
            db.session.add(new_order)

        return '', 201


@app.route('/orders/<int:gid>/', methods=['GET', 'PUT', 'DELETE'])
def orders_id(gid):
    """ вьюшка для использования различных методов """
    if request.method == 'GET':
        order = Order.query.get(gid)
        data = {
                "id": order.id,
                "name": order.name,
                "description": order.description,
                "start_date": order.start_date,
                "end_date": order.end_date,
                "address": order.address,
                "price": order.price,
                "customer_id": order.customer_id,
                "executor_id": order.executor_id
            }
        return jsonify(data)

    elif request.method == "PUT":
        data = request.get_json()
        order = Order.query.get(gid)
        order.name = data['name']
        order.description = data['description']
        order.start_date = datetime.strptime(data['start_date'], '%m/%d/%Y')  # перевод времени из JSON in python
        order.end_date = datetime.strptime(data['end_date'], '%m/%d/%Y')  # перевод времени из JSON in python
        order.address = data['address']
        order.price = data['price']
        order.customer_id = data['customer_id']
        order.executor_id = data['executor_id']

        with db.session.begin():
            db.session.add(order)

        return '', 203

    elif request.method == 'DELETE':
        order = Order.query.get(gid)
        with db.session.begin():
            db.session.delete(order)

        return '', 202


@app.route('/offers/', methods=['GET'])
def offer_index():
    """ вьюшка для обработки запросов в таблице Offer"""
    if request.method == 'GET':
        data = []
        for offer in Offer.query.all():
            data.append({
                 "id": offer.id,
                 "order_id": offer.order_id,
                 "executor_id": offer.executor_id
             }
            )
        return jsonify(data)


@app.route('/offers/<int:oid>/', methods=['POST', 'PUT', 'DELETE'])
def offer_id(oid):
    """ вьюшка для использования различных методов """
    if request.method == "POST":
        data = request.get_json()
        new_offer = function_json_user(data)

        with db.session.begin():
            db.session.add(new_offer)

        return '', 201

    elif request.method == "PUT":
        data = request.get_json()
        offer = Offer.query.get(oid)
        offer.order_id = data['order_id']
        offer.executor_id = data['executor_id']

        with db.session.begin():
            db.session.add(offer)

        return '', 203

    elif request.method == 'DELETE':
        offer = Offer.query.get(oid)
        with db.session.begin():
            db.session.delete(offer)

        return '', 202


if __name__ == '__main__':
    main()
