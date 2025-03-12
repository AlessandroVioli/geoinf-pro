import pandas as pd
import csv

from io import StringIO

from jinja2.utils import markupsafe

from flask import request, send_file, flash
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_admin.actions import action
from flask_admin.babel import gettext

from app.models.maps import LulcMap, LulcMapLegend, LulcMapVersion, LulcMapDownload, LulcMapSpatialData


# Map Model View
class LulcMapView(ModelView):
    column_exclude_list = ['terms_of_use',]
    can_export = True

    column_formatters = {
        'description': lambda v, c, m, p: m.description[:100]+"...",
        'citation': lambda v, c, m, p: m.citation[:100]+"...",
        #'terms_of_use': lambda v, c, m, p: m.terms_of_use[:100]+"...",
    }


def format_legend_text(v, c, m, p):
    value = m.legend_text
    content = '<div style="overflow: auto;max-height: 20vh;">'
    if value:
        df = pd.read_csv(StringIO(value), sep=",")
        df = df.dropna(axis=1, how="all")
        content += df.to_html(index=False).replace('\\r\\n', '<br>')
    content += "</div>"
    return markupsafe.Markup(content)

class LulcMapLegendView(ModelView):
    #column_exclude_list = ['legend_text',]
    #column_list = ('name', 'legend_text')

    #field_list = ['name', 'legend_text'] 

    column_formatters = {
        "legend_text": format_legend_text,
    }

    
class LulcMapVersionView(ModelView):
    form_ajax_refs = {
        'map': {
            'fields': ['name'],
            'page_size': 0,
        },
        'legend': {
            'fields': ['name'],
            'page_size': 0,
        },
    }

    can_export = True

class LulcMapDownloadView(ModelView):
    form_ajax_refs = {
        'map_version': {
            'fields': ['map', 'version'],
            'page_size': 0,
        },
    }

    can_export = True

    #TODO
    @expose('/import/', methods=['POST'])
    def import_csv(self):
        csv_file = request.files.get('csv_file')

    #export selected
    @action('export_to_csv', 'Export to csv', 'Are you sure you want to export selected rows to csv file?')
    def action_export_to_csv(self, ids):
        if len(ids) == 0:
            #TODO report
            return
        try:
            query = LulcMapDownload.query.filter(LulcMapDownload.id.in_(ids))
            #TODO
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash(gettext('Failed to export. %(error)s', error=str(ex)), 'error')

class LulcMapSpatialDataView(ModelView):
    form_ajax_refs = {
        'map': {
            'fields': ['name'],
            'page_size': 0,
        },
        'map_version': {
            'fields': ['map', 'version'],
            'page_size': 0,
        },
    }

    can_export = True


# Admin View
class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/analytics.html')
    
