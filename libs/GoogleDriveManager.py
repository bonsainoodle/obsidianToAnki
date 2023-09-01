import os
import shutil
import json
import re
import io

from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build


class GoogleDriveManager:
    def __init__(
        self, credentials_file_path: str, data_folder_path: str, obsidian_separator: str
    ) -> None:
        self.credentials_file_path = credentials_file_path
        self.data_folder_path = data_folder_path

        self.obsidian_separator = obsidian_separator

        self.SCOPES = ["https://www.googleapis.com/auth/drive"]

        self.processed_data = []

        self._authenticate()

    def _authenticate(self) -> None:
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_file_path, scopes=self.SCOPES
        )

        self.drive_service = build("drive", "v3", credentials=credentials)

    def extract_tags(self, content) -> list:
        extracted_tags = re.findall(r"#(\w+)", content)

        tags = [tag.lower() for tag in extracted_tags]

        return tags

    def extract_backlinks(self, content) -> list:
        extracted_backlinks = re.findall(r"\[\[(.*?)\]\]", content)

        backlinks = [backlink.lower() for backlink in extracted_backlinks]

        return backlinks

    def delete_data_folder(self) -> None:
        if os.path.exists(self.data_folder_path):
            shutil.rmtree(self.data_folder_path)

    def download_file(self, file_id: str, folder_path: str) -> None:
        request = self.drive_service.files().get_media(fileId=file_id)
        with open(folder_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

    def download_files_recursive(self, folder_id: str, folder_path: str) -> None:
        results = (
            self.drive_service.files()
            .list(q=f"'{folder_id}' in parents", fields="files(id, name, mimeType)")
            .execute()
        )
        files = results.get("files", [])

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for file in files:
            file_id = file["id"]
            file_name = file["name"]
            file_type = file["mimeType"]

            local_path = os.path.join(folder_path, file_name)

            if file_type == "application/vnd.google-apps.folder":
                subfolder_path = os.path.join(folder_path, file_name)
                self.download_files_recursive(
                    folder_id=file_id, folder_path=subfolder_path
                )
            else:
                try:
                    self.download_file(file_id=file_id, folder_path=local_path)
                    print(f"Downloaded: {local_path}")
                    self.process_markdown_file(
                        file_path=local_path, file_id=file_id, file_name=file_name
                    )
                except HttpError as e:
                    print(f"Error downloading {file_name}: {e}")

    def process_markdown_file(
        self, file_path: str, file_id: str, file_name: str
    ) -> None:
        if file_path.endswith(".md"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

                try:
                    content_before, content_after = content.split(
                        self.obsidian_separator
                    )
                except Exception:
                    return

                backlinks = self.extract_backlinks(content)
                tags = self.extract_tags(content)

                data = {
                    "id": file_id,
                    "name": file_name,
                    "backlinks": backlinks,
                    "tags": tags,
                    "content_before": content_before,
                    "content_after": content_after,
                }

                self.processed_data.append(data)

    def save_processed_data(self) -> None:
        with open(f"{self.data_folder_path}/data.json", "w", encoding="utf-8") as f:
            json.dump(self.processed_data, f, ensure_ascii=False, indent=4)

    def get_files(self, folder_id: str) -> None:
        self.delete_data_folder()
        self.download_files_recursive(
            folder_id=folder_id, folder_path=self.data_folder_path
        )
        self.save_processed_data()

    def upload_file(self, parent_folder_id: str, file_name: str, content: str) -> None:
        file_metadata = {"name": file_name, "parents": [parent_folder_id]}
        media = MediaIoBaseUpload(io.BytesIO(content), mimetype="text/plain")
        self.drive_service.files().create(
            body=file_metadata, media_body=media
        ).execute()

    def get_file_link(self, parent_folder_id: str, file_name: str) -> str:
        results = (
            self.drive_service.files()
            .list(
                q=f"'{parent_folder_id}' in parents and name='{file_name}'",
                fields="files(webViewLink)",
            )
            .execute()
        )

        files = results.get("files", [])

        if files:
            return files[0]["webViewLink"]
        else:
            return "File not found"
