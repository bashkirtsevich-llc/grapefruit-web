from os.path import splitext

from functools import wraps
from time import time


def async_timing(f):
    @wraps(f)
    async def wrap(*args, **kwargs):
        ts = time()
        result = await f(*args, **kwargs)
        te = time()

        return te - ts, result

    return wrap


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)

        num /= 1024.0

    return "%.1f %s%s" % (num, "Y", suffix)


def get_files_list(files, first_ten=False):
    return [
        {"name": "/".join(file["path"]),
         "size": sizeof_fmt(file["length"]),
         "icon": get_file_icon(file["path"][~0])}
        for file in (files[:10] if first_ten else files)
    ]


def get_files_size(files):
    return sizeof_fmt(sum(file["length"] for file in files))


def get_file_icon(file_name):
    icons = {
        "image": "fa-file-image-o",
        "pdf": "fa-file-pdf-o",
        "word": "fa-file-word-o",
        "powerpoint": "fa-file-powerpoint-o",
        "excel": "fa-file-excel-o",
        "audio": "fa-file-audio-o",
        "video": "fa-file-video-o",
        "zip": "fa-file-zip-o",
        "code": "fa-file-code-o",
        "text": "fa-file-text-o",
        "file": "fa-file-o"
    }

    extensions = {
        ".gif": icons["image"],
        ".jpeg": icons["image"],
        ".jpg": icons["image"],
        ".png": icons["image"],
        ".svg": icons["image"],
        ".bmp": icons["image"],

        ".pdf": icons["pdf"],

        ".txt": icons["text"],
        ".nfo": icons["text"],
        ".diz": icons["text"],
        ".md": icons["text"],

        ".doc": icons["word"],
        ".docx": icons["word"],

        ".ppt": icons["powerpoint"],
        ".pptx": icons["powerpoint"],

        ".xls": icons["excel"],
        ".xlsx": icons["excel"],

        ".aac": icons["audio"],
        ".mp3": icons["audio"],
        ".ogg": icons["audio"],
        ".flac": icons["audio"],
        ".wav": icons["audio"],

        ".avi": icons["video"],
        ".flv": icons["video"],
        ".mkv": icons["video"],
        ".mp4": icons["video"],
        ".mpg": icons["video"],
        ".3gp": icons["video"],
        ".mov": icons["video"],

        ".gz": icons["zip"],
        ".zip": icons["zip"],
        ".rar": icons["zip"],
        ".7z": icons["zip"],
        ".tar": icons["zip"],
        ".xz": icons["zip"],
        ".arc": icons["zip"],

        ".py": icons["code"],
        ".css": icons["code"],
        ".html": icons["code"],
        ".js": icons["code"],
        ".c": icons["code"],
        ".cpp": icons["code"]
    }

    return extensions.get(splitext(file_name)[1].lower(), icons["file"])
