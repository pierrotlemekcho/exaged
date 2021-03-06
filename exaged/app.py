from flask import Flask, Response, request
from flask_restful import Resource, Api
import cv2
import configparser
from exaged import database
from exaged.model.tier_client import TierClient
from exaged.model.commande import Commande
from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure
from datetime import datetime
from pathlib import Path
import io


cameras = {}
samba = {}


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


def store_file_and_create_folders(conn, file_path, file_binary):
    file_path = Path(file_path)
    share = file_path.parts[1]
    folders = file_path.parts[2:-1]

    last_folder = '/'
    for folder in folders:
        last_folder += f'{folder}/'
        try:
            conn.createDirectory(
                share,
                last_folder
            )
        except OperationFailure:
            pass

    conn.storeFile(
        share,
        f'/{"/".join(file_path.parts[2:])}',
        file_binary
    )


class CaptureVideoFeed(Resource):
    def post(self, camera_id, commande_id):
        db = database.factory()
        commande = db.query(Commande).filter(Commande.exact_order_id == commande_id).first();
        if camera_id == 'custom-file':
            image = request.files['file']
        else:
            video_capture = cv2.VideoCapture(f"{cameras[camera_id]}/profile1")
            ret, frame = video_capture.read()
            image = io.BytesIO(cv2.imencode('.jpg', frame)[1].tobytes())
        conn = SMBConnection(
            samba["user"],
            samba["password"],
            "abcd",
            samba["server_name"],
            use_ntlm_v2=True)
        conn.connect(samba["server_ip"], int(samba["port"]))
        if (commande):
            tier = commande.tier
            filename = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"//Workspace$/documents/32-Clients/{tier.exact_name}/C{commande.exact_order_number}/{filename}.jpg"
        else:
            date = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"//Documentsv7$/OFFICE One Documents/spool/{date}.jpg"
        store_file_and_create_folders(conn, filename, image)
        return {"filename": filename}


class VideoFeed(Resource):
    def get(self, id):
        video_capture = cv2.VideoCapture(f"{cameras[id]}/profile3")
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (640, 375))
        return Response(
            cv2.imencode('.jpg', small_frame)[1].tobytes(), mimetype='image/jpeg')


def make_app():
    app = Flask('exacam')
    api = Api(app)
    config = configparser.ConfigParser()
    config.read('exaged.ini')
    cameras.update(**config["exacams"])
    samba.update(**config["samba"])
    database.configure(url=config['exaged']['database_url'])

    api.add_resource(HelloWorld, '/')
    api.add_resource(Cameras, '/cameras')
    api.add_resource(VideoFeed, '/video_feed/<string:id>')
    api.add_resource(ClientsResource, '/clients')
    api.add_resource(ClientCommandeResource, '/client/<string:client_exact_id>/commandes')
    api.add_resource(CaptureVideoFeed, '/video_feed/<string:camera_id>/<string:commande_id>')
    return app
