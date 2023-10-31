from allauth.socialaccount.models import SocialToken
import requests

from custom_settings import ADMIN_NAME
from website.utils.oauth import ensure_valid_token


FOLDER_MIMETYPE = "application/vnd.google-apps.folder"
google_drive_files = ({}, {})


def get_google_drive_token(request):
    token = SocialToken.objects.get(app__provider="google", account__user__username=ADMIN_NAME)
    ensure_valid_token(request, token)
    return token


def check_error(data):
    if "error" in data:
        error = data.get("error", {})
        raise ValueError(f"{error.get('status', '')}: {error.get('message', '')}")


def populate_file_list(request, folder_id="root", path: list[str] | None = None, recursive=False):
    token = get_google_drive_token(request)
    auth_header = {"Authorization": f"Bearer {token.token}"}

    if path is None:
        path = []

    files = []
    next_page_token = None
    while True:
        next_page_token_param = {"pageToken": next_page_token} if next_page_token is not None else {}
        data = requests.get(
            "https://www.googleapis.com/drive/v3/files",
            {
                **next_page_token_param,
                "orderBy": "name_natural",
                "q": f"'{folder_id}' in parents and trashed = false",
            },
            headers=auth_header,
        ).json()
        check_error(data)
        files.extend(data["files"])
        if data["incompleteSearch"]:
            next_page_token = data["nextPageToken"]
        else:
            break

    file_tree = google_drive_files
    for el in path:
        file_tree = file_tree[0][el]

    for file in files:
        file_name = file.get("name", "")
        file_tree[1][file_name] = file

        if file.get("mimeType", "") == FOLDER_MIMETYPE:
            if file_name not in file_tree[0]:
                file_tree[0][file_name] = ({}, {})
            if recursive:
                populate_file_list(request, file.get("id", ""), path + [file_name], True)


_export_formats = {}


def get_export_formats(request):
    global _export_formats
    if _export_formats:
        return _export_formats

    token = get_google_drive_token(request)
    auth_header = {"Authorization": f"Bearer {token.token}"}
    data = requests.get(
        "https://www.googleapis.com/drive/v3/about",
        {"fields": "exportFormats"},
        headers=auth_header,
    ).json()

    ret = {}
    for format, export_formats in data.get("exportFormats", {}).items():
        for export_format in export_formats:
            if "office" in export_format:
                ret[format] = export_format
                break
        else:
            ret[format] = export_formats[0]
    _export_formats = ret
    return ret
