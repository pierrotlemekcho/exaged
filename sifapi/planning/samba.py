from pathlib import Path
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
