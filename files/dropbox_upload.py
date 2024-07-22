import argparse
import dropbox
import os
import time
import requests
import requests.auth

dropbox_app_key = os.environ["DROPBOX_APP_KEY"]
dropbox_app_secret = os.environ["DROPBOX_APP_SECRET"]
dropbox_refresh_token = os.environ["DROPBOX_REFRESH_TOKEN"]
TOKEN_URL = "https://api.dropbox.com/oauth2/token"


class DropBoxUpload:
    def __init__(self, timeout=900, chunk=8):
        self.timeout = timeout
        self.chunk = chunk

    @staticmethod
    def get_access_token():
        client_auth = requests.auth.HTTPBasicAuth(dropbox_app_key, dropbox_app_secret)
        post_data = {"grant_type": "refresh_token", "refresh_token": dropbox_refresh_token}
        response = requests.post(TOKEN_URL, auth=client_auth, data=post_data)
        response_json = response.json()
        return response_json["access_token"]

    def upload_file(self, access_token, file_path):
        dbx = dropbox.Dropbox(access_token, timeout=self.timeout)
        file_size = os.path.getsize(file_path)
        chunk_size = self.chunk * 1024 * 1024
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
                cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                           offset=f.tell())
                commit = dropbox.files.CommitInfo(path=dest_path)
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', nargs='+',
                        type=str, help='path to file to upload')
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--chunk', type=int, default=50, help='chunk size in MB')
    args = parser.parse_args()

    dbu = DropBoxUpload(timeout=args.timeout, chunk=args.chunk)
    access_token = dbu.get_access_token()
    for file_path in args.file_path:
        dbu.upload_file(access_token, file_path)


if __name__ == "__main__":
    main()
