import re

import jinja2
from pycldf.terms import TERMS
from uritemplate import URITemplate

from datasette import hookimpl

P = re.compile('where cldf_languageReference = (?P<id>[0-9a-zA-Z_\-]+)')


@hookimpl
def render_cell(value, column):
    prefix, _, lname = column.partition('_')
    if prefix == 'cldf' and lname in TERMS:
        term = TERMS[lname]
        valueUrl = term.csvw_prop('valueUrl')
        if valueUrl:
            templ = URITemplate(valueUrl)
            return jinja2.Markup('<a href="{0}">{1}</a>'.format(
                templ.expand(dict(zip(templ.variable_names, [value]))),
                value))
        if lname in ['analyzedWord', 'gloss']:
            return '\t'.join(value.split('\\t'))


def linked_tables(foreign_key_tables):
    return [o['other_table'] for o in foreign_key_tables]


def render_igt(obj, columns):
    t = """<p class="cldf_primaryText">{0}</p>
<table><tr><tr class="col-cldf_analyzedWord">{1}</tr><tr>{2}</tr></table>
<p class="col-cldf_translatedText">{3}</p>""".format(
        obj['cldf_primaryText'],
        ''.join(['<td>{0}</td>'.format(w) for w in obj['cldf_analyzedWord'].split('\\t')]),
        ''.join(['<td>{0}</td>'.format(w) for w in obj['cldf_gloss'].split('\\t')]),
        obj['cldf_translatedText'],
    )
    return jinja2.Markup(t)


@hookimpl
def extra_template_vars():
    return {
        "render_cell": render_cell,
        "linked_tables": linked_tables,
        "render_igt": render_igt,
    }


@hookimpl
def extra_js_urls():
    return['/-/static-plugins/datasette_cldf/cldf.js']


@hookimpl
def extra_css_urls():
    return['/-/static-plugins/datasette_cldf/cldf.css']
