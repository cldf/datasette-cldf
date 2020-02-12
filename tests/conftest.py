import json
from urllib.parse import quote, unquote
import pathlib
import tempfile

import pytest
from asgiref.sync import async_to_sync
from asgiref.testing import ApplicationCommunicator
from datasette.app import Datasette
from pycldf import Database, Dataset

import datasette_cldf


def _make_client(cldf_md, tmpdir):
    cldf = Dataset.from_metadata(cldf_md)
    dbpath = tmpdir / 'db.sqlite'
    db = Database(cldf, fname=dbpath, infer_primary_keys=True)
    db.write_from_tg()
    return make_app_client(dbpath, metadata=datasette_cldf.metadata(cldf, 'db'))


@pytest.fixture(scope='session')
def StructureDataset():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield _make_client(
            pathlib.Path(__file__).parent / 'cldf_StructureDataset' / 'StructureDataset-metadata.json',
            pathlib.Path(tmpdir))


class Response:
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body

    @property
    def json(self):
        return json.loads(self.text)

    @property
    def text(self):
        return self.body.decode("utf8")


class Client:
    max_redirects = 5

    def __init__(self, asgi_app):
        self.asgi_app = asgi_app

    @async_to_sync
    async def get(self, path, allow_redirects=True, redirect_count=0, method="GET"):
        return await self._get(path, allow_redirects, redirect_count, method)

    async def _get(self, path, allow_redirects=True, redirect_count=0, method="GET"):
        query_string = b""
        if "?" in path:
            path, _, query_string = path.partition("?")
            query_string = query_string.encode("utf8")
        if "%" in path:
            raw_path = path.encode("latin-1")
        else:
            raw_path = quote(path, safe="/:,").encode("latin-1")
        scope = {
            "type": "http",
            "http_version": "1.0",
            "method": method,
            "path": unquote(path),
            "raw_path": raw_path,
            "query_string": query_string,
            "headers": [[b"host", b"localhost"]],
        }
        instance = ApplicationCommunicator(self.asgi_app, scope)
        await instance.send_input({"type": "http.request"})
        # First message back should be response.start with headers and status
        messages = []
        start = await instance.receive_output(2)
        messages.append(start)
        assert start["type"] == "http.response.start"
        headers = dict(
            [(k.decode("utf8"), v.decode("utf8")) for k, v in start["headers"]]
        )
        status = start["status"]
        # Now loop until we run out of response.body
        body = b""
        while True:
            message = await instance.receive_output(2)
            messages.append(message)
            assert message["type"] == "http.response.body"
            body += message["body"]
            if not message.get("more_body"):
                break
        response = Response(status, headers, body)
        if allow_redirects and response.status in (301, 302):
            assert (
                redirect_count < self.max_redirects
            ), "Redirected {} times, max_redirects={}".format(
                redirect_count, self.max_redirects
            )
            location = response.headers["Location"]
            return await self._get(
                location, allow_redirects=True, redirect_count=redirect_count + 1
            )
        return response


def make_app_client(database, metadata=None):
    ds = Datasette(
        [database],
        immutables=[],
        metadata=metadata,
        template_dir=pathlib.Path(datasette_cldf.__file__).parent / 'templates')
    client = Client(ds.app())
    client.ds = ds
    return client
