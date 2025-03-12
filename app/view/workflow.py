import pandas as pd
from io import StringIO
from flask import Blueprint, render_template, jsonify, request
from jinja2.utils import markupsafe
from app.extensions import db
from app.models.maps import LulcMap, LulcMapLegend, LulcMapVersion, LulcMapDownload, LulcMapSpatialData

workflows = Blueprint('workflow_view', __name__)
workflow_svg_mapping = {
    'molca': 'MOLCA.svg',
    'molcap': 'MOLCAP.svg',
}

@workflows.route('/<name>', methods=['GET'])
def show_workflow(name):
    '''展示工作流详细信息。'''
    svg_name = workflow_svg_mapping.get(name)

    return render_template('workflow/show.html', name=name.upper(), svg_name=svg_name)