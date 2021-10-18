import io
from pathlib import Path

import magic
from django.conf import settings
from smb.smb_structs import OperationFailure
from smb.SMBConnection import SMBConnection


def factory():
    config = settings.SAMBA
    connection = SMBConnection(
        config["user"],
        config["password"],
        "abcd",
        config["server_name"],
        use_ntlm_v2=True,
    )
    connection.connect(config["server_ip"], int(config["port"]))
    return connection


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
