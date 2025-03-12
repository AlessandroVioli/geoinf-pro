from app.extensions import db
from sqlalchemy.dialects.postgresql import JSON
from enum import Enum

class CoverageType(Enum):
    Global = 'Global'
    Regional = 'Regional'

class Lulc_Type(Enum):
    BARELAND = 'bareland'
    BUILTUP = 'built-up'
    CROPLAND = 'cropland'
    FOREST = 'forest'
    GRASSLAND = 'grassland'
    SHRUBLAND = 'shrubland'
    WATER = 'water'
    WETLAND = 'wetland'
    PERMANENTICEANDSNOW = 'permanent ice and snow'


# 数据库模型定义
class LulcMap(db.Model):
    __tablename__ = 'lulc_maps'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    resolution = db.Column(db.Float)
    crs = db.Column(db.String(255))
    coverage = db.Column(db.Enum(CoverageType)) 
    update_frequency = db.Column(db.String(255))
    provider = db.Column(db.String(255))
    citation = db.Column(db.Text)
    terms_of_use = db.Column(db.Text)  # Terms of Use
    homepage_url = db.Column(db.String(255))  # Dataset home page URL
    supported_lulc_types = db.Column(db.ARRAY(db.Enum(Lulc_Type))) # Supported LULC types

    def __repr__(self):
        return f'<Map {self.name}>'


class LulcMapLegend(db.Model):
    __tablename__ = 'lulc_map_legends'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    legend_text = db.Column(db.Text)

    def __repr__(self):
        return f'<Legend {self.name}>'

class LulcMapVersion(db.Model):
    __tablename__ = 'lulc_map_versions'

    id = db.Column(db.Integer, primary_key=True)
    map_id = db.Column(db.Integer, db.ForeignKey('lulc_maps.id'), nullable=False)
    map = db.relationship('LulcMap', backref='lulc_map_versions', lazy=False)

    version = db.Column(db.String(255))
    temporal_extent = db.Column(JSON)
    accuracy = db.Column(db.Text)
    legend_id = db.Column(db.Integer, db.ForeignKey('lulc_map_legends.id'), nullable=False)
    legend = db.relationship('LulcMapLegend', backref='lulc_map_versions', lazy=False)

    def __repr__(self):
        return f'<LulcMapVersion {self.map.name} - Version {self.version}>'


class LulcMapDownload(db.Model):
    __tablename__ = 'lulc_map_downloads'

    id = db.Column(db.Integer, primary_key=True)
    #map_id = db.Column(db.Integer, db.ForeignKey('lulc_maps.id'), nullable=False)
    #map = db.relationship('LulcMap', backref='lulc_map_downloads', lazy=False)
    map_version_id = db.Column(db.Integer, db.ForeignKey('lulc_map_versions.id'), nullable=False)
    map_version = db.relationship('LulcMapVersion', backref='downloads', lazy=False)
    download_url = db.Column(db.String(255), nullable=False)
    download_link_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    years = db.Column(db.JSON)
    geometry = db.Column(JSON) # range


class LulcMapSpatialData(db.Model):
    __tablename__ = 'lulc_map_spatial_data'

    id = db.Column(db.Integer, primary_key=True)
    map_id = db.Column(db.Integer, db.ForeignKey('lulc_maps.id'), nullable=False)
    map = db.relationship('LulcMap', backref='lulc_map_spatial_data', lazy=False)
    map_version_id = db.Column(db.Integer, db.ForeignKey('lulc_map_versions.id'), nullable=False)
    map_version = db.relationship('LulcMapVersion', backref='lulc_map_spatial_data', lazy=False)
    spatial_type = db.Column(db.String(50), nullable=False)
    geometry = db.Column(JSON, nullable=False)


