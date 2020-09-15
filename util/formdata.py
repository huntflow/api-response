import uuid
import mimetypes
from typing import Sequence, Tuple


def get_content_type(filename: str) -> str:
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"


def encode_multipart_formdata(
    fields: Sequence[Tuple[str, str]], files: Sequence[Tuple[str, str, str]]
) -> Tuple[str, bytes]:
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be
    uploaded as files.
    Return (content_type, body)
    """

    boundary = "----------%s" % uuid.uuid4().hex
    boundary_bytes = boundary.encode()
    body = b""

    for (key, value) in fields:
        key_bytes = key.encode()

        body += b"--%s\r\n" % boundary_bytes
        body += b'Content-Disposition: form-data; name="%s"\r\n' % key_bytes
        body += b"\r\n"
        body += value.encode()
        body += b"\r\n"

    for (key, filename, value) in files:
        key_bytes = key.encode()
        filename_bytes = filename.encode()

        body += b"--%s\r\n" % boundary_bytes

        body += b'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (
            key_bytes,
            filename_bytes,
        )
        body += b"Content-Type: %s\r\n" % get_content_type(filename).encode()
        body += b"\r\n"
        body += value
        body += b"\r\n"

    body += b"--%s--\r\n" % boundary_bytes
    body += b"\r\n"

    content_type = "multipart/form-data; boundary=%s" % boundary
    return content_type, body
