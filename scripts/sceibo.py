import io
import requests


class Sciebo:
    @staticmethod
    def mkcol(webdav_url: str, dest: str, token: str, password: str) -> None:
        """
        create a collection if it doesn't exist
        """
        url = f"{webdav_url}/{dest}"
        response = requests.request(
            "MKCOL",
            url,
            auth=(token, password),
        )
        try:
            response.raise_for_status()
            print(f"Sceibo collection created: {dest}")
        except requests.exceptions.HTTPError:
            if response.status_code == 405:  # collection exists
                print(f"Sciebo collection exists: {dest}")

    @staticmethod
    def upload(
        webdav_url: str,
        filepath: str,
        content: str,
        token: str,
        password: str,
    ) -> None:
        """
        upload article data as virtual text file
        """
        file_io = io.BytesIO(content.encode("utf-8"))
        url = f"{webdav_url}/{filepath}"

        response = requests.put(
            url,
            data=file_io,
            auth=(token, password),
        )

        if response.status_code in (200, 201):
            print(f"✅ File uploaded successfully to {filepath}")
        else:
            print(
                f"❌ Upload failed to {filepath} with status code {response.status_code}"
            )
            if response.status_code == 403:
                print("The file likely exists")
