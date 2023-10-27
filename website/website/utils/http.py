from urllib.parse import quote


def encode_filename(filename: str):
    try:
        filename.encode("ascii")
        return 'filename="{}"'.format(filename.replace("\\", "\\\\").replace('"', r"\""))
    except UnicodeEncodeError:
        return "filename*=utf-8''{}".format(quote(filename))
