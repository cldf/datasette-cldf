import pathlib
import argparse

from datasette_cldf.commands import serve


def test_serve(tmpdir, mocker):
    parser = argparse.ArgumentParser()
    serve.register(parser)
    args = parser.parse_args(args=[
        '--db-path',
        str(tmpdir.join('db.sqlite')),
        str(pathlib.Path(__file__).parent / 'cldf_Dictionary' / 'Dictionary-metadata.json')
    ])
    args.log = mocker.Mock()
    mocker.patch('datasette_cldf.commands.serve.os', mocker.Mock())
    serve.run(args)
