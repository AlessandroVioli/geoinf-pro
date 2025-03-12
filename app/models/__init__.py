from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app.extensions import db
from app.models.maps import LulcMap, LulcMapLegend, LulcMapVersion, LulcMapDownload, LulcMapSpatialData

from app.models.admin import LulcMapView, LulcMapVersionView, LulcMapDownloadView, LulcMapSpatialDataView, LulcMapLegendView
from app.models.admin import AnalyticsView


admin = None
def init_admin(app):
    admin = Admin(app, name="Open LULC Map", template_mode='bootstrap3')

    # maps
    admin.add_view(LulcMapView(LulcMap, db.session))
    admin.add_view(LulcMapLegendView(LulcMapLegend, db.session))
    admin.add_view(LulcMapVersionView(LulcMapVersion, db.session))
    admin.add_view(LulcMapDownloadView(LulcMapDownload, db.session))
    admin.add_view(LulcMapSpatialDataView(LulcMapSpatialData, db.session))
    #admin
    admin.add_view(AnalyticsView(name='Analytics', endpoint='analytics'))

    return admin