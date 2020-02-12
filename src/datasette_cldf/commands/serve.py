"""
Serve dataset with datasette
"""
import os
import pathlib

from clldutils.clilib import PathType
from clldutils import jsonlib

from pycldf import Database, Dataset

from cldfbench.cli_util import get_dataset, add_dataset_spec

import datasette_cldf


def register(parser):
    parser.add_argument(
        '--cfg-path',
        default='datasette_metadata.json',
        type=PathType(type='file', must_exist=False))
    parser.add_argument(
        '--db-path',
        default=None,
        type=PathType(type='file', must_exist=False))
    add_dataset_spec(parser)


def run(args):
    p = pathlib.Path(args.dataset)
    if p.suffix == '.json' and p.exists():
        cldf_ds = Dataset.from_metadata(p)
        ds = None
    else:  # pragma: no cover
        ds = get_dataset(args)
        cldf_ds = ds.cldf_reader()

    try:
        count_p = len(list(cldf_ds['ParameterTable']))
    except KeyError:
        count_p = 100

    default_page_size = 100
    while default_page_size < count_p and default_page_size < 600:
        default_page_size += 100  # pragma: no cover

    #  max_returned_rows            Maximum rows that can be returned from a table
    #                               or custom query (default=1000)

    if not args.db_path:  # pragma: no cover
        args.db_path = pathlib.Path('{0}.sqlite'.format(ds.id if ds else 'cldf_db'))

    if not args.db_path.exists():
        db = Database(
            cldf_ds,
            fname=args.db_path,
            infer_primary_keys=True,
        )
        db.write_from_tg()
        args.log.info('{0} loaded in {1}'.format(db.dataset, db.fname))

    jsonlib.dump(datasette_cldf.metadata(cldf_ds, args.db_path.stem), args.cfg_path, indent=4)

    os.system(
        'datasette {0} -m {1} --template-dir {2} --config default_page_size:{3}'.format(
            args.db_path,
            args.cfg_path,
            pathlib.Path(datasette_cldf.__file__).parent / 'templates',
            default_page_size))
