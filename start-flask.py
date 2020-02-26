from flask import Flask, Response
from flask_restful import Resource, Api
import cv2
import configparser
from exaged import database
from exaged.model.tier_client import TierClient
from exaged.model.commande import Commande

app = Flask(__name__)
api = Api(app)

cameras = {}


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class Cameras(Resource):
    def get(self):
        return [camera for camera in cameras]


class ClientsResource(Resource):
    def get(self):
        db = database.factory()
        clients = db.query(
            TierClient
        ).join(
            Commande, TierClient.exact_id == Commande.exact_tier_id
        ).filter(
            Commande.exact_status != 21
        ).order_by(TierClient.exact_name).all()
        return [{"id": client.exact_id, "name": client.exact_name} for client in clients]


class ClientCommandeResource(Resource):
    def get(self, client_exact_id):
        db = database.factory()
        commandes = db.query(Commande).filter(Commande.exact_tier_id == client_exact_id).filter(Commande.exact_status != 21)
        return [commande.to_json() for commande in commandes]


class CaptureVideoFeed(Resource):
    def post():
        pass


class VideoFeed(Resource):
    def get(self, id):
        video_capture = cv2.VideoCapture(cameras[id])
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (640, 375))
        return Response(
            cv2.imencode('.jpg', small_frame)[1].tobytes(), mimetype='image/jpeg')


config = configparser.ConfigParser()
config.read('exaged.ini')
cameras = config["exacams"]
database.configure(url=config['exaged']['database_url'])

api.add_resource(HelloWorld, '/')
api.add_resource(VideoFeed, '/video_feed/<string:id>')
api.add_resource(ClientsResource, '/clients')
api.add_resource(ClientCommandeResource, '/client/<string:client_exact_id>/commandes')

if __name__ == '__main__':
    app.run(debug=True)
