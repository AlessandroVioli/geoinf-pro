import pandas as pd
from io import StringIO
from flask import Blueprint, render_template, jsonify, request
from jinja2.utils import markupsafe
from app.extensions import db
from app.models.maps import LulcMap, LulcMapLegend, LulcMapVersion, LulcMapDownload, LulcMapSpatialData

maps = Blueprint('maps_view', __name__)

@maps.route('/<int:map_id>', methods=['GET'])
def show_map_details(map_id):
    '''展示单个地图集详细信息。'''
    map_data = LulcMap.query.get_or_404(map_id)

    # 查询关联的数据
    versions = LulcMapVersion.query.filter_by(map_id=map_data.id).all()
    ## handle version.legend.legend_text
    for version in versions:
        try:
            # legend
            if version.legend.legend_text:
                df = pd.read_csv(StringIO(version.legend.legend_text), sep=",")
                df = df.dropna(axis=1, how="all")
                version.legend.legend_text = df.to_html(index=False)
            # download link
            
        except Exception as e:
            print("Error", e, "\noriginal data:", version.legend.legend_text)
    #downloads = LulcMapDownload.query.filter_by(map_id=map_data.id).all()
    #legend = LulcMapLegend.query.filter_by(id=map_data.legend_id).first()

    return render_template('map/detail.html', map=map_data, versions=versions)