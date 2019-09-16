# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

from ... import tools
from .. import context


def to_csv(ctx, raw_data, **kwargs):
    """Pass."""
    rows = []

    kvtmpl = "{}: {}".format

    for raw_row in tools.listify(raw_data, dictkeys=False):
        row = {
            k: context.join_cr(v, is_cell=True)
            for k, v in raw_row.items()
            if context.is_los(v)
        }
        rows.append(row)

        view = raw_row.get("view", {})
        query = view.get("query", {})
        fields = view.get("fields", [])
        colfilters = view.get("colFilters", {})
        colfilters = [kvtmpl(k, v) for k, v in colfilters.items()]
        sort = view.get("sort", {})

        row["query"] = query.get("filter", None)
        row["fields"] = context.join_cr(fields, is_cell=True)
        row["column_filters"] = context.join_cr(colfilters, is_cell=True)
        row["sort_descending"] = format(sort.get("desc"))
        row["sort_field"] = sort.get("field")

    return context.dictwriter(rows=rows)