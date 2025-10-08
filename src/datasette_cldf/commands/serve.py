"""
Serve dataset with datasette
"""
import os
import pathlib

from clldutils.clilib import PathType
from clldutils import jsonlib

from pycldf import Database
from pycldf.cli_util import add_dataset, get_dataset

import datasette_cldf


def register(parser):
    add_dataset(parser)
    parser.add_argument(
        '--cfg-path',
        default='datasette_metadata.json',
        type=PathType(type='file', must_exist=False))
    parser.add_argument(
        '--db-path',
        default=None,
        type=PathType(type='file', must_exist=False))


def run(args):
    cldf_ds = get_dataset(args)
    dsid = cldf_ds.properties.get('rdf:ID') or 'cldf_db'

    try:
        count_p = len(list(cldf_ds['ParameterTable']))
    except KeyError:
        count_p = 100

    default_page_size = 100
    while default_page_size < count_p and default_page_size < 600:
        default_page_size += 100  # pragma: no cover

    #  max_returned_rows            Maximum rows that can be returned from a table
    #                               or custom query (default=1000)

    db_path = args.db_path or pathlib.Path('{0}.sqlite'.format(dsid))
    if not db_path.exists():
        db = Database(cldf_ds, fname=db_path, infer_primary_keys=True)
        db.write_from_tg()
        args.log.info('{0} loaded in {1}'.format(db.dataset, db.fname))

    jsonlib.dump(
        datasette_cldf.metadata({db_path.stem: cldf_ds}),
        args.cfg_path,
        indent=4)

    os.system(
        'datasette {} -m {} --template-dir {} --config default_page_size:{}'.format(
            str(db_path),
            args.cfg_path,
            pathlib.Path(datasette_cldf.__file__).parent / 'templates',
            default_page_size))
