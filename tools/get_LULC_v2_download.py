import os
import requests
import pandas as pd

def check_exist(url):
    resp = requests.head(url)
    return resp.status_code == 200

def get_link(exists = None):
    start_year, end_year = 2017, 2023
    alphas = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    link_tpl = "https://lulctimeseries.blob.core.windows.net/lulctimeseriesv003/lc{year}/{index:02d}{code}_{year}0101-{next_year}0101.tif"
    for year in range(start_year, end_year+1):
        print(f"Begin to get link for year {year}")
        for index in range(100):
            for code in alphas:
                url = link_tpl.format(year=year, index=index, code=code, next_year=year+1)
                if exists and url in exists: continue
                if check_exist(url):
                    print("Exist:", url)
                    yield (year, url)

def generate_downloads_csv(save_to):
    items = []
    exists = []
    if os.path.exists(save_to):
        df = pd.read_csv(save_to)
        for index, row in df.iterrows():
            items.append({
                "map_version_id": row["map_version_id"],
                "download_url": row["download_url"],
                "download_link_name": row["download_link_name"],
                "description": row["description"],
                "year": row["year"],
            })
            exists.append(row["download_url"])

    try:
        for year, url in get_link(exists):
            items.append({
                "map_version_id": 3,
                "download_url": url,
                "download_link_name": url.split("/")[-1],
                "description": "Source: https://livingatlas.arcgis.com/landcoverexplorer",
                "year": year,
            })
    except Exception as e:
        print("Exception: ", e)
    finally:
        df = pd.DataFrame(items)
        df.to_csv(save_to, index=False)

if __name__ == '__main__':
    # TODO Must run
    generate_downloads_csv(r"/Users/qiong/Lab/GitHub/open-lulc-map/db/lulc_map_downloads/LULC Annual v2.csv")