from flask import Blueprint, jsonify, request
from shapely.geometry import shape, Polygon
import geopandas as gpd

from app.extensions import db
from app.models.maps import LulcMap, LulcMapLegend, LulcMapVersion, LulcMapDownload, LulcMapSpatialData

maps = Blueprint('maps_api', __name__)

@maps.route('/', methods=['GET'])
def get_lulc_maps():
    '''获取所有 LULC 地图集列表。'''
    lulc_maps = LulcMap.query.all()
    return jsonify([{'id': map.id, 'name': map.name} for map in lulc_maps])

@maps.route('/<int:id>', methods=['GET'])
def get_map_by_id(id):
    '''获取单个地图集详细信息。'''
    map = LulcMap.query.get(id)
    if map:
        return jsonify({'id': map.id, 'name': map.name})
    else:
        return jsonify({'error': '地图集不存在'}), 404

@maps.route('/<int:id>/downloads', methods=['GET'])
def get_map_downloads(id):
    '''获取单个地图集的下载链接列表。'''
    map = LulcMap.query.get(id)
    if map:
        downloads = db.session.query(LulcMapDownload).filter_by(map_id=id).all()
        return jsonify([{'id': download.id, 'url': download.download_url} for download in downloads])
    else:
        return jsonify({'error': '地图集不存在'}), 404

@maps.route('/search', methods=['POST'])
def search_maps():
    '''根据关键词搜索 LULC 地图集。'''
    data = request.get_json()
    if 'keyword' not in data:
        return jsonify({'error': '缺少关键词参数'}), 400
    keyword = data['keyword']
    maps = LulcMap.query.filter(or_(LulcMap.name.like(f'%{keyword}%'), LulcMap.description.like(f'%{keyword}%'))).all()
    return jsonify([{'id': map.id, 'name': map.name} for map in maps])

@maps.route('/query/coverage/<ctype>', methods=['GET'])
def query_map_by_coverage(ctype):
    ctype = ctype.capitalize()
    global_lulc_maps = LulcMap.query.filter(LulcMap.coverage == ctype).all()
    #print("global_lulc_maps:", global_lulc_maps)
    res = []
    all_years = set()
    for ele in global_lulc_maps:
        info = {"name": ele.name, "resolution": ele.resolution, "crs": ele.crs}
        # query all version for this map
        versions = LulcMapVersion.query.filter(
            LulcMapVersion.map_id == ele.id).all()
        accuracy, years = [], []
        for version in versions:
            if version.accuracy.strip():
                accuracy.append(version.accuracy)
            years.extend(version.temporal_extent)
        info["accuracy"] = accuracy
        info["years"] = years
        all_years.update(years)
        res.append(info)
    return jsonify({"coverage":ctype, "data": res, "years": list(all_years)})

@maps.route('/query/point', methods=['POST'])
def query_maps_by_point():
    '''查询特定坐标涉及的 LULC 地图集。'''
    req_data = request.get_json()
    #print(req_data)
    latlng = req_data.get('coords')
    longitude, latitude = latlng['lng'], latlng['lat']
    if not longitude or not latitude:
        return jsonify({'error': 'longitude or latitude missing'}), 400
    longitude = float(longitude)
    latitude = float(latitude)
    # 根据经纬度筛选 LULC 地图集数据
    unique_data = set()
    ## Assumption: all the global maps are included
    global_lulc_maps = LulcMap.query.filter(LulcMap.coverage == 'Global').all()
    #print("global_lulc_maps:", global_lulc_maps)
    for ele in global_lulc_maps:
        versions = LulcMapVersion.query.filter(
            LulcMapVersion.map_id == ele.id).all()
        for version in versions:
            #print(version.temporal_extent)
            unique_data = unique_data.union(
                [(te, ele.name) for te in version.temporal_extent]
            )

    ## query by geometry
    common_crs = "EPSG:4326"
    spatial_data = LulcMapSpatialData.query.all()
    point = gpd.GeoSeries.from_xy(x=[longitude], y=[latitude], crs=common_crs)
    #print("****************>>>>", point)

    for ele in spatial_data:
        # check if the coordinates is in the geometry
        #print("****************\n", ele.geometry)
        region = gpd.GeoDataFrame.from_features(ele.geometry['features'], crs=ele.geometry['crs']['properties']['name'])
        region = region.to_crs(common_crs)
        print("********>>", point.within(region.unary_union))
        if point.within(region.unary_union).iloc[0]:
            unique_data = unique_data.union(
                [(te, ele.map.name) for te in ele.map_version.temporal_extent]
            )
        

    #print("Data: ", unique_data)
    # 统计匹配的LULC Map数据的数量
    data = {}
    for ele in unique_data:
        year, name = ele[0], ele[1]
        if year not in data: data[year] = []
        data[year].append(name)

    # Sort list by name
    data = {k: sorted(v) for k, v in data.items()}
    # Sort data by year
    sorted_data = dict(sorted(data.items(), key=lambda item: int(item[0]))) 

    return jsonify({"coordinate":{"lat": latitude, 'lon': longitude}, "data": sorted_data})

@maps.route('/query/region', methods=['POST'])
def query_maps_by_region():
    '''查询特定区域涉及的 LULC 地图集。'''
    req_data = request.get_json()
    #print(req_data)
    region_coords = req_data.get('coords')
    # 根据区域筛选 LULC 地图集数据
    unique_data = set()
    ## Assumption: all the global maps are included
    global_lulc_maps = LulcMap.query.filter(LulcMap.coverage == 'Global').all()
    #print("global_lulc_maps:", global_lulc_maps)
    for ele in global_lulc_maps:
        versions = LulcMapVersion.query.filter(
            LulcMapVersion.map_id == ele.id).all()
        for version in versions:
            unique_data = unique_data.union(
                (te, ele.name) for te in version.temporal_extent
            )

    ## query by geometry
    common_crs = "EPSG:4326"
    spatial_data = LulcMapSpatialData.query.all()
    polygon = gpd.GeoSeries([shape(region_coords)], crs=common_crs)
    print("********>>", polygon)

    for ele in spatial_data:
        # check if the coordinates is in the geometry
        region = gpd.GeoDataFrame.from_features(ele.geometry['features'], crs=ele.geometry['crs']['properties']['name'])
        region = region.to_crs(common_crs)
        is_intersects = region.geometry.intersects(polygon)
        #print("********>>", is_intersects)
        if is_intersects.any():
            print("********>> Include", ele.map.name)
            unique_data = unique_data.union(
                (te, ele.map.name) for te in ele.map_version.temporal_extent
            )
        

    #print("Data: ", unique_data)
    # 统计匹配的LULC Map数据的数量
    data = {}
    for ele in unique_data:
        year, name = ele[0], ele[1]
        if year not in data: data[year] = []
        data[year].append(name)

    # Sort list by name
    data = {k: sorted(v) for k, v in data.items()}
    # Sort data by year
    sorted_data = dict(sorted(data.items(), key=lambda item: int(item[0]))) 

    return jsonify({"data": sorted_data})

@maps.route('/update', methods=['PUT'])
def update_map():
    '''更新 LULC 地图集信息。'''
    data = request.get_json()
    if 'id' not in data or 'name' not in data:
        return jsonify({'error': '缺少 ID 和名称参数'}), 400
    id = int(data['id'])
    name = data['name']
    map = LulcMap.query.get(id)
    if map:
        map.name = name
        db.session.commit()
        return jsonify({'message': '更新成功'})
    else:
        return jsonify({'error': '地图集不存在'}), 404

@maps.route('/import', methods=['POST'])
def import_map():
    '''导入新的 LULC 地图集数据。'''
    data = request.get_json()
    if 'name' not in data or 'description' not in data:
        return jsonify({'error': '缺少名称和描述参数'}), 400
    name = data['name']
    description = data['description']
    # 导入新的 LULC 地图集数据，具体实现方式根据实际需求调整
    map = LulcMap(name=name, description=description)
    db.session.add(map)
    db.session.commit()
    return jsonify({'message': '导入成功'})

@maps.route('/export', methods=['GET'])
def export_map():
    '''导出 LULC 地图集数据。'''
    # 导出 LULC 地图集数据，具体实现方式根据实际需求调整
    maps = LulcMap.query.all()
    data = [{'id': map.id, 'name': map.name} for map in maps]
    return jsonify(data)
    