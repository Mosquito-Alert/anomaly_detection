import sys
import requests
from pathlib import Path

# Constants
FOLDER_PATH = Path("/home/gsanz/Documents/bites/test_predict")
URL = "http://localhost:8000/api/v1/metrics/batch/"
TOKEN = "ccedc275300cdb98fd2282b60809332706539c4b"
HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Token {TOKEN}"
}


def sorted_csv_files(folder):
    """Return list of CSV files sorted by name."""
    return sorted(
        [f for f in folder.glob("bites_*.csv") if f.is_file()],
        key=lambda f: f.name
    )


def send_file(file_path):
    """Send a single CSV file to the server."""
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f, 'text/csv')}
        print(f"Sending: {file_path.name}")
        response = requests.post(URL, files=files, headers=HEADERS)
        if response.status_code != 201:
            print(f"ERROR: Failed to upload {file_path.name}.")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)
        else:
            print(f"Uploaded successfully: {file_path.name}")


def main():
    if not FOLDER_PATH.exists():
        print(f"Folder '{FOLDER_PATH}' does not exist.")
        return

    csv_files = sorted_csv_files(FOLDER_PATH)

    if not csv_files:
        print("No CSV files found in the folder.")
        return

    for file_path in csv_files:
        send_file(file_path)


if __name__ == "__main__":
    main()
