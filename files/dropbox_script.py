import argparse
import dropbox
import os
import time
import requests
import requests.auth
from dropbox.files import CommitInfo, UploadSessionCursor
from dropbox.exceptions import ApiError
from dropbox.exceptions import HttpError

dropbox_app_key = os.environ["DROPBOX_APP_KEY"]
dropbox_app_secret = os.environ["DROPBOX_APP_SECRET"]
dropbox_refresh_token = os.environ["DROPBOX_REFRESH_TOKEN"]
TOKEN_URL = "https://api.dropbox.com/oauth2/token"


def get_access_token():
    client_auth = requests.auth.HTTPBasicAuth(dropbox_app_key, dropbox_app_secret)
    post_data = {"grant_type": "refresh_token", "refresh_token": dropbox_refresh_token}
    response = requests.post(TOKEN_URL, auth=client_auth, data=post_data)
    try:
        response.raise_for_status()
    except Exception as e:
        print(e)
        print(response.json())
    else:
        response_json = response.json()
        return response_json["access_token"]


def upload_file(file_path, timeout, chunk):
    access_token = get_access_token()
    dbx = dropbox.Dropbox(access_token, timeout=timeout)
    file_size = os.path.getsize(file_path)
    chunk_size = chunk * 1024 * 1024
    dest_path = '/' + os.path.basename(file_path)
    since = time.time()
    with (open(file_path, 'rb') as f):
        uploaded_size = 0
        if file_size <= chunk_size:
            dbx.files_upload(f.read(), dest_path)
            time_elapsed = time.time() - since
            debug = 'Uploaded {:.2f}%'.format(100).ljust(15) + \
                    ' --- {:.0f}m {:.0f}s'.format(time_elapsed // 60, time_elapsed % 60).rjust(15)
            print(debug)
        else:
            upload_session_start_result = dbx.files_upload_session_start(f.read(chunk_size))
            cursor = UploadSessionCursor(session_id=upload_session_start_result.session_id, offset=f.tell())
            commit = CommitInfo(path=dest_path)
            while f.tell() <= file_size:
                if (file_size - f.tell()) <= chunk_size:
                    dbx.files_upload_session_finish(f.read(chunk_size), cursor, commit)
                    time_elapsed = time.time() - since
                    debug = 'Uploaded {:.2f}%'.format(100).ljust(15) + \
                            ' --- {:.0f}m {:.0f}s'.format(time_elapsed // 60, time_elapsed % 60).rjust(15)
                    print(debug)
                    break
                else:
                    dbx.files_upload_session_append_v2(f.read(chunk_size), cursor)
                    cursor.offset = f.tell()
                    uploaded_size += chunk_size
                    uploaded_percent = 100 * uploaded_size / file_size
                    time_elapsed = time.time() - since
                    debug = 'Uploaded {:.2f}%'.format(uploaded_percent).ljust(15) + \
                            ' --- {:.0f}m {:.0f}s'.format(time_elapsed // 60, time_elapsed % 60).rjust(15)
                    print(debug, end='\r')


def list_folder(timeout):
    access_token = get_access_token()
    dbx = dropbox.Dropbox(access_token, timeout=timeout)
    try:
        res = dbx.files_list_folder("")
    except ApiError as err:
        print('Folder listing failed', err)
    else:
        for entry in res.entries:
            print(entry.name)


def download(file_name, timeout):
    access_token = get_access_token()
    dbx = dropbox.Dropbox(access_token, timeout=timeout)
    try:
        md, res = dbx.files_download('/' + file_name)
    except HttpError as err:
        print('*** HTTP error', err)
        return None
    with open(file_name, 'wb') as f:
        f.write(res.content)
    print(f"Downloaded {file_name}")


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    upload_parser = subparsers.add_parser('upload')
    upload_parser.add_argument('file_path', nargs='+', type=str, help='path to file to upload')
    upload_parser.add_argument('--timeout', type=int, default=900)
    upload_parser.add_argument('--chunk', type=int, default=50, help='chunk size in MB')

    list_parser = subparsers.add_parser('list')
    list_parser.add_argument('--timeout', type=int, default=30)

    download_parser = subparsers.add_parser('download')
    download_parser.add_argument('file_name', nargs='+', type=str, help='file name to download')
    download_parser.add_argument('--timeout', type=int, default=900)

    args = parser.parse_args()

    if args.command == 'upload':
        for file_path in args.file_path:
            upload_file(file_path, args.timeout, args.chunk)
    elif args.command == 'list':
        list_folder(args.timeout)
    elif args.command == 'download':
        for file_name in args.file_name:
            download(file_name, args.timeout)
    else:
        print('Command not found')
        exit(1)


if __name__ == "__main__":
    main()
