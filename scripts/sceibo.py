import os
import io
import requests


class Sciebo:
    WEBDAV_URL = os.environ.get("WEBDAV_URL", None)
    TOKEN = os.environ.get("SCIEBO_TOKEN", None)
    PASSWORD = os.environ.get("SCIEBO_PASSWORD", None)

   
    @staticmethod
    def mkcol(dest: str) -> None:
        """
        create a collection
        """
        url = f"{Sciebo.WEBDAV_URL}/{dest}"
        response = requests.request(
            "MKCOL",
            url,
            auth=(
                Sciebo.TOKEN,
                Sciebo.PASSWORD,
            ),
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.status_code == 405:  # collection exists
                print(f"Sciebo collection exists: {dest}")

    @staticmethod
    def upload(filepath: str, content: str) -> None:
        """
        upload article data as text file
        accepts an article type
        need a filename like <YYYY-MM-DD>.<ARTICLE_ID>
        note: this method does not check for valid filepath
        """
        file_io = io.BytesIO(content.encode("utf-8"))
        url = f"{Sciebo.WEBDAV_URL}/{filepath}"

        response = requests.put(
            url,
            data=file_io,
            auth=(
                Sciebo.TOKEN,
                Sciebo.PASSWORD,
            ),
        )

        if response.status_code in (200, 201):
            print(f"✅ File uploaded successfully to {filepath}")
        else:
            print(
                f"❌ Upload failed to {filepath} with status code {response.status_code}"
            )