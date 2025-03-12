import os
import time
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio import features
from rasterio.warp import transform_geom
import geojson
from shapely.geometry import box, mapping
from shapely.ops import unary_union
import json

############ [BEGIN] FROM XXXX to GEOJSON ############
# get raster borders and save as geojson
def rasterborder2geojson(rpath, save_to):
    with rasterio.open(rpath) as src:
        # 获取栅格的边界信息 (bounding box)
        bounds = src.bounds
        # 获取栅格的 CRS (坐标参考系)
        crs = src.crs

        border_polygon = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
        border_feature = geojson.Feature(geometry=mapping(border_polygon), properties={})
        geojson_data = geojson.FeatureCollection([border_feature])

        # Adding CRS information to the GeoJSON
        crs_info = {
            "type": "name",
            "properties": {
                "name": crs.to_string()
            }
        }
        geojson_data['crs'] = crs_info

        with open(save_to, 'w') as f:
            geojson.dump(geojson_data, f)

        print(f"Raster [{rpath}] border with CRS saved to {save_to}")
        return json.dumps(geojson_data)

# get borders of rasters in a dir, and save them as a geojson
def rastersborder2geojson(raster_dir, save_to):
   # 用于存储所有栅格边界的多边形列表
    polygons = []
    crs = None  # 用于存储CRS信息

    # 遍历目录下的所有文件
    for filename in os.listdir(raster_dir):
        if filename.endswith('.tif'):  # 假设栅格文件为tif格式
            filepath = os.path.join(raster_dir, filename)
            with rasterio.open(filepath) as src:
                # 获取栅格的边界（bounding box）
                bounds = src.bounds
                polygon = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
                
                # 获取栅格的CRS信息
                if crs is None:
                    crs = src.crs

                # 将边界多边形添加到列表中
                polygons.append(polygon)

   # 合并所有边界多边形为一个单一的多边形
    merged_polygon = unary_union(polygons)

    # 创建一个GeoDataFrame
    gdf = gpd.GeoDataFrame({'geometry': [merged_polygon]}, crs=crs)

    # 保存为GeoJSON文件，包含CRS信息
    gdf.to_file(save_to, driver='GeoJSON')
    return gdf.to_json()

# from raster to geojson
def raster2geojson(rpath, save_to, non_val=0):
    # 打开 Raster 文件
    with rasterio.open(rpath) as src:
        raster_data = src.read(1)
        # Generate shapes (polygons) for all the regions in the raster
        results = (
            {'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v) 
            in enumerate(
                features.shapes(raster_data, mask=None, transform=src.transform))
            if v > non_val
        )

        # Create a GeoDataFrame from the shapes
        geoms = list(results)
        gdf = gpd.GeoDataFrame.from_features(geoms)

        # Dissolve polygons to get a single boundary
        boundary = gdf.dissolve(by='raster_val')

        # Set the CRS
        boundary.set_crs(src.crs, inplace=True)

    boundary.to_file(save_to, driver='GeoJSON')

    print(f'GeoJSON saved to {save_to}')

# from shapefile to geojson
def shapefile2geojson(spath, save_to):
    sf = gpd.read_file(spath)
    sf.to_file(save_to, driver='GeoJSON')

############ [END] FROM XXXX to GEOJSON ############


# read download link from db where geometry is missing, download it, get geojson and update db item
import random
from batch_db import CONN_INFO
from download import download_and_extract
from file_folder import remove
import psycopg2
def get_geojson_from_link(link):
    ## download
    postfix = '.'.join(link.split('?')[0].split('/')[-1].split('.')[1:])
    #link_postfix.append(postfix)
    if postfix == 'pdf': print(link)
    fpath = download_and_extract(link)
    if fpath is None:
        print(f"Cannot get {link}")
        return None
    ## get geojson
    geojson_str = '{}'
    save_geojson_path = f"update_{time.time()}.geojson"
    if os.path.isfile(fpath):
        geojson_str = rasterborder2geojson(fpath, save_geojson_path)
    elif os.path.isdir(fpath):
        geojson_str = rastersborder2geojson(fpath, save_geojson_path)
        
    remove(save_geojson_path)
    return geojson_str, postfix, fpath

def update_geojson_in_csv(csv_path, link_column, geo_column, map_version_ids_with_same_geojson=None):
    csv_df = pd.read_csv(csv_path, on_bad_lines="warn")
    link_postfix = []
    csv_df = csv_df.sample(frac = 1)
    try:
        geojson_maps = {}
        for index, row in csv_df.iterrows():
            print(f"begin to hande {row}")
            if row[geo_column] == "": continue
            # handled before and it is reusable
            mvid = row['map_version_id']
            if mvid in geojson_maps:
                csv_df.at[index, geo_column] = geojson_maps[mvid]
                continue
            # no handled before
            link = row[link_column]
            ## download
            geojson_str, postfix, fpath = get_geojson_from_link(link)
            link_postfix.append(postfix)
            if geojson_str is None: continue
            ## update records
            csv_df.at[index, geo_column] = geojson_str
            print(f"handle {row} succeeds!")
            # remove downloaded
            remove(fpath)
            if map_version_ids_with_same_geojson is not None and mvid in map_version_ids_with_same_geojson and mvid not in geojson_maps:
                geojson_maps[mvid] = geojson_str

    except Exception as e:
        print("Exception: ", e)
    finally:
        print('all postfix:', set(link_postfix))
        # save back
        csv_df.to_csv(f"{csv_path}.udpated.{time.time()}", index=False)
        
def update_geojson_in_db(table, link_column, geo_column, conn_info=CONN_INFO):
    conn = psycopg2.connect(**conn_info)
    conn.autocommit = True
    # creating a cursor 
    cursor = conn.cursor() 
    try:
        # get
        sql = f"select id, {link_column} from {table} where {geo_column} is NULL or {geo_column} = '{{}}'"
        cursor.execute(sql) 
        results = cursor.fetchall() 
        print(f"Number of items with geometry is not set: {len(results)}")

        # shuffle to prevent DOS behavior
        random.shuffle(results)
        # update 
        link_postfix = []
        for rid, link in results:
            ## download
            geojson_str, postfix, fpath = get_geojson_from_link(link)
            link_postfix.append(postfix)
            if geojson_str is None: continue
            ## update records
            upd_sql = f"update {table} set {geo_column} = %s where id=%s"
            cursor.execute(upd_sql, (geojson_str, rid))
            # remove downloaded
            remove(fpath)

        print('all postfix:', set(link_postfix))
        conn.commit() 
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close() 



if __name__ == '__main__':
    raster2geojson(
        r'/Users/qiong/Downloads/brasil_coverage_2022.tif',
        r'/Users/qiong/Downloads/brasil_coverage_2022.geojson'
    )
    #rasterborder2geojson(r'/Users/qiong/Downloads/JRC_GFC2020_V1_N80_W170.tif', 'JRC_GFC2020_V1_N80_W170.geojson')
    #rastersborder2geojson(r'/Users/qiong/Downloads/ESA_WorldCover_10m_2021_v200_60deg_macrotile_S90E000', 'ESA_WorldCover_10m_2021_v200_60deg_macrotile_S90E000.geojson')
    #rastersborder2geojson(r'/Users/qiong/Downloads/GLC_FCS30D_19852022maps_W175-W180', 'GLC_FCS30D_19852022maps_W175-W180.geojson')
    #update_geojson_in_db('lulc_map_downloads', 'download_url', 'geometry')
    #update_geojson_in_csv(r"C:\Users\XU\Documents\GitHub\open-lulc-map\db\lulc_map_downloads\all.csv", "download_url", "geometry", [30, 31,])
    