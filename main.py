import json

from libs.GoogleDriveManager import GoogleDriveManager

with open("config.json") as f:
    config = json.load(f)

google_drive_manager = GoogleDriveManager(
    credentials_file_path=config["credentials_file_path"],
    data_folder_path=config["data_folder_path"],
)


google_drive_manager.get_files(folder_id=config["folder_id"])
