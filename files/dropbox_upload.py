import argparse
import dropbox
import os
import time

token = os.environ["DROPBOX_ACCESS_TOKEN"]


class DropBoxUpload:
    def __init__(self, token, timeout=900, chunk=8):
        self.token = token
        self.timeout = timeout
        self.chunk = chunk

    def upload_file(self, file_path):
        dbx = dropbox.Dropbox(self.token, timeout=self.timeout)
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

    dbu = DropBoxUpload(token, timeout=args.timeout, chunk=args.chunk)
    for file_path in args.file_path:
        dbu.upload_file(file_path)


if __name__ == "__main__":
    main()
