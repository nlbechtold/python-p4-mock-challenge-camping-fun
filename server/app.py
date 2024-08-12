#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_restful import Api, Resource
from flask_migrate import Migrate
# from flask_cors import CORS
from models import db, Activity, Camper, Signup
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
# CORS(app)
db.init_app(app)

api = Api(app)

class CampersResource(Resource):
    def get(self):
        campers = Camper.query.all()
        list_of_campers = []
        for camper in campers:
            list_of_campers.append({
                'id': camper.id,
                'name': camper.name,
                'age': camper.age
            })
        return list_of_campers, 200
    def post(self):
        try:
            data = request.get_json()
            camper = Camper(name=data['name'], age=data['age'])
            db.session.add(camper)
            db.session.commit()
            return camper.to_dict(), 201
        except Exception as e:
            return {"errors": ["validation errors"]}, 400

class CamperResource(Resource):
    def get(self, id):
        camper = Camper.query.get(id)
        if camper:
            return camper.to_dict(rules=('-signups.camper', '-activities.campers')), 200
        return {"error": "Camper not found"}, 404

    def patch(self, id):
        camper = Camper.query.get(id)
        if not camper:
            return {"error": "Camper not found"}, 404

        try:
            data = request.get_json()
            if 'name' in data:
                camper.name = data['name']
            if 'age' in data:
                camper.age = data['age']
            db.session.commit()
            return camper.to_dict(), 202
        except Exception as e:
            return {"errors": ["validation errors"]}, 400

class ActivitiesResource(Resource):
    def get(self):
        activities = Activity.query.all()
        return [activity.to_dict() for activity in activities], 200

    def delete(self, id):
        activity = Activity.query.get(id)
        if activity:
            db.session.delete(activity)
            db.session.commit()
            return {}, 204
        return {"error": "Activity not found"}, 404

class SignupsResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            signup = Signup(camper_id=data['camper_id'], activity_id=data['activity_id'], time=data['time'])
            db.session.add(signup)
            db.session.commit()
            return signup.to_dict(), 201
        except Exception as e:
            return {"errors": ["validation errors"]}, 400

api.add_resource(CampersResource, '/campers')
api.add_resource(CamperResource, '/campers/<int:id>')
api.add_resource(ActivitiesResource, '/activities', '/activities/<int:id>')
api.add_resource(SignupsResource, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
