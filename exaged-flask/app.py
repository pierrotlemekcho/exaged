import configparser
import io
from datetime import datetime
from pathlib import Path

import cv2
import magic
from flask import Flask, Response, request, send_file
from flask_restful import Api, Resource
from pdf2image import convert_from_bytes
from PIL import Image
from smb.smb_structs import OperationFailure
from smb.SMBConnection import SMBConnection

from exaged import database, samba
from exaged.constants import EXACT_STATUS_CANCELLED, EXACT_STATUS_CLOSED
from exaged.model.commande import Commande
from exaged.model.ligne_de_commande import LigneDeCommande
from exaged.model.tier_client import TierClient
from exaged.schema.order_line import OrderLineSchema

cameras = {}


class HelloWorld(Resource):
    def get(self):
        return {"hello": "world"}


class Cameras(Resource):
    def get(self):
        return [camera for camera in cameras]


class ClientsResource(Resource):
    def get(self):
        db = database.factory()
        clients = (
            db.query(TierClient)
            .join(Commande, TierClient.exact_id == Commande.exact_tier_id)
            .filter(Commande.exact_status != EXACT_STATUS_CLOSED)
            .order_by(TierClient.exact_name)
            .all()
        )
        return [
            {"id": client.exact_id, "name": client.exact_name} for client in clients
        ]


class ClientCommandeResource(Resource):
    def get(self, client_exact_id):
        db = database.factory()
        commandes = (
            db.query(Commande)
            .filter(Commande.exact_tier_id == client_exact_id)
            .filter(Commande.exact_status != 21)
        )
        return [commande.to_json() for commande in commandes]


def list_path(conn, path):
    path_parts = Path(path).parts
    share = path_parts[1]
    folder = "/".join(path_parts[2:])
    return conn.listPath(share, folder)


def find_file_mime_type(conn, path):
    path_parts = Path(path).parts
    share = path_parts[1]
    file_path = "/".join(path_parts[2:])
    # Read first 2048 bytes
    file_buffer = io.BytesIO()
    conn.retrieveFileFromOffset(share, file_path, file_buffer, max_length=2048)
    file_buffer.seek(0)

    return magic.from_buffer(file_buffer.read(), mime=True)


def retrieve_file(conn, path):
    path_parts = Path(path).parts
    share = path_parts[1]
    file_path = "/".join(path_parts[2:])
    file_buffer = io.BytesIO()
    conn.retrieveFile(share, file_path, file_buffer)
    file_buffer.seek(0)
    return file_buffer


def store_file_and_create_folders(conn, file_path, file_binary):
    file_path = Path(file_path)
    share = file_path.parts[1]
    folders = file_path.parts[2:-1]

    last_folder = "/"
    for folder in folders:
        last_folder += f"{folder}/"
        try:
            conn.createDirectory(share, last_folder)
        except OperationFailure:
            pass

    conn.storeFile(share, f'/{"/".join(file_path.parts[2:])}', file_binary)


class CaptureVideoFeed(Resource):
    def post(self, camera_id, commande_id):
        db = database.factory()
        commande = (
            db.query(Commande).filter(Commande.exact_order_id == commande_id).first()
        )
        if camera_id == "custom-file":
            image = request.files["file"]
        else:
            video_capture = cv2.VideoCapture(f"{cameras[camera_id]}/profile1")
            ret, frame = video_capture.read()
            image = io.BytesIO(cv2.imencode(".jpg", frame)[1].tobytes())
        smb_connection = samba.factory()
        if commande:
            tier = commande.tier
            filename = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"//Workspace$/documents/32-Clients/{tier.exact_name}/C{commande.exact_order_number}/{filename}.jpg"
        else:
            date = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"//Documentsv7$/OFFICE One Documents/spool/{date}.jpg"
        store_file_and_create_folders(smb_connection, filename, image)
        return {"filename": filename}


class VideoFeed(Resource):
    def get(self, id):
        video_capture = cv2.VideoCapture(f"{cameras[id]}/profile3")
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (640, 375))
        return Response(
            cv2.imencode(".jpg", small_frame)[1].tobytes(), mimetype="image/jpeg"
        )


class Folder(Resource):
    def get(self, order_number):
        db = database.factory()
        smb_connection = samba.factory()
        commande = (
            db.query(Commande)
            .filter(Commande.exact_order_number == order_number)
            .first()
        )
        folder_content = list_path(smb_connection, commande.folder_path)
        result = []
        for content in folder_content:
            if not content.isDirectory:
                url = f"/file/{commande.exact_order_id}/{content.filename}"
                full_path = f"{commande.folder_path}/{content.filename}"
                mimetype = find_file_mime_type(smb_connection, full_path)
                if mimetype.startswith("image") or mimetype == "application/pdf":
                    result.append(
                        {
                            "filename": content.filename,
                            "last_write_time": content.last_write_time,
                            "file_size": content.file_size,
                            "thumbnail_url": f"{url}/preview",
                            "url": url,
                            "mimetype": find_file_mime_type(smb_connection, full_path),
                        }
                    )
        return result


class Thumbnail(Resource):
    THUMBNAIL_SIZE = (400, 400)

    def get(self, order_id, filename):
        db = database.factory()
        smb_connection = samba.factory()
        commande = (
            db.query(Commande).filter(Commande.exact_order_id == order_id).first()
        )
        full_path = f"{commande.folder_path}/{filename}"
        file_type = find_file_mime_type(smb_connection, full_path)
        if file_type.startswith("image"):
            buffer_file = retrieve_file(smb_connection, full_path)
            result = io.BytesIO()

            file = Image.open(buffer_file)
            file.thumbnail(self.THUMBNAIL_SIZE)
            file.save(result, "PNG", compress_level=9)
            result.seek(0)
            return send_file(result, mimetype="image/png")
        elif file_type == "application/pdf":
            buffer_file = retrieve_file(smb_connection, full_path)
            images = convert_from_bytes(
                buffer_file.read(), size=self.THUMBNAIL_SIZE[0], fmt="png"
            )
            image = images[0]
            result = io.BytesIO()
            image.save(result, "PNG", compress_level=9)
            result.seek(0)
            return send_file(result, mimetype="image/png")
        return


class File(Resource):
    def get(self, order_id, filename):
        db = database.factory()
        smb_connection = samba.factory()
        commande = (
            db.query(Commande).filter(Commande.exact_order_id == order_id).first()
        )
        full_path = f"{commande.folder_path}/{filename}"
        buffer_file = retrieve_file(smb_connection, full_path)
        mimetype = magic.from_buffer(buffer_file.read(), mime=True)
        buffer_file.seek(0)
        return send_file(buffer_file, mimetype=mimetype)


class PlannifCommande(Resource):
    """
    We get all active commande and all commandes scheduled for last 10 days
    and next 10 days
    """

    def get(self):
        db = database.factory()
        # TODO add scheduled at filter
        commandes = db.query(Commande).filter(
            Commande.exact_status != EXACT_STATUS_CLOSED,
            Commande.exact_status != EXACT_STATUS_CANCELLED,
        )
        return [commande.to_json() for commande in commandes]


class PlannifLines(Resource):
    """
    We only care about saving the lines scheduled_at and schedule priority
    """

    def put(self):
        schema = OrderLineSchema(many=True)
        lines = schema.load(request.json)
        result_lines = []
        db = database.factory()
        for line in lines:
            db_line = (
                db.query(LigneDeCommande)
                .filter(LigneDeCommande.exact_id == line["exact_id"])
                .first()
            )
            db_line.scheduled_at = line["scheduled_at"]
            db_line.schedule_priority = line["schedule_priority"]
            db.add(db_line)
            result_lines.append(db_line)
        db.commit()
        return schema.dump(result_lines)


def make_app():
    app = Flask("exacam")
    api = Api(app)
    config = configparser.ConfigParser()
    config.read("exaged.ini")
    cameras.update(**config["exacams"])
    samba.configure(**config["samba"])
    database.configure(url=config["exaged"]["database_url"])

    api.add_resource(HelloWorld, "/")
    api.add_resource(Cameras, "/cameras")
    api.add_resource(VideoFeed, "/video_feed/<string:id>")
    api.add_resource(ClientsResource, "/clients")
    api.add_resource(
        ClientCommandeResource, "/client/<string:client_exact_id>/commandes"
    )
    api.add_resource(
        CaptureVideoFeed, "/video_feed/<string:camera_id>/<string:commande_id>"
    )
    api.add_resource(Folder, "/folder/<string:order_number>")
    api.add_resource(Thumbnail, "/file/<string:order_id>/<string:filename>/preview")
    api.add_resource(File, "/file/<string:order_id>/<string:filename>")
    api.add_resource(PlannifCommande, "/plannif_commandes")
    api.add_resource(PlannifLines, "/plannif_lines")
    return app
