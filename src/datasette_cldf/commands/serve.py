"""
Serve dataset with datasette
"""
import os
import pathlib
import argparse

from clldutils.clilib import PathType
from clldutils import jsonlib

from pycldf import Database, Dataset
from pycldf.dataset import sniff, iter_datasets
from zenodoclient import Zenodo

from cldfbench.cli_util import get_dataset

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
    parser.add_argument(
        'dataset',
        help='specify dataset(s) by metadata file, Zenodo DOI or python module'
    )
    parser.add_argument('--entry-point', help=argparse.SUPPRESS, default=None)


def run(args):
    ds = None
    if Zenodo.DOI_PATTERN.match(args.dataset):
        z = Zenodo()
        out = z.download_record(z.record_from_doi(args.dataset), pathlib.Path('.'))
        args.log.info('Downloaded files for {0} to {1}'.format(args.dataset, out))
        for cldf_ds in iter_datasets(out):
            break
        else:
            raise ValueError('No CLDF dataset discovered in {0}'.format(out))
    else:
        p = pathlib.Path(args.dataset)
        if p.exists() and sniff(p):
            cldf_ds = Dataset.from_metadata(p)
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
