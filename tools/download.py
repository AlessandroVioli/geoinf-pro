import os
import requests
import zipfile
import tarfile
import rarfile
from urllib.parse import urlparse
from tqdm import tqdm
from file_folder import remove
    
TMP_DIR = r'./tmp'
# 下载并解压的函数
def download_and_extract(url, save_dir=TMP_DIR):
    # 创建保存目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    try:
        # 获取文件名
        local_filename = os.path.join(save_dir, os.path.basename(urlparse(url).path))

        # 下载文件
        print(f"Downloading {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 1024

        # 使用tqdm显示下载进度
        with open(local_filename, 'wb') as file, tqdm(
            desc=local_filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                bar.update(len(data))

        # 根据文件扩展名解压文件，并返回解压目录或文件路径
        if local_filename.endswith('.zip'):
            print(f"Extracting {local_filename}...")
            with zipfile.ZipFile(local_filename, 'r') as zip_ref:
                extract_dir = os.path.join(save_dir, os.path.splitext(local_filename)[0])
                zip_ref.extractall(extract_dir)
            remove(local_filename)
            return extract_dir

        elif local_filename.endswith('.tar.gz') or local_filename.endswith('.tgz'):
            print(f"Extracting {local_filename}...")
            extract_dir = os.path.join(save_dir, os.path.splitext(local_filename)[0])
            with tarfile.open(local_filename, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_dir)
            remove(local_filename)
            return extract_dir

        elif local_filename.endswith('.rar'):
            print(f"Extracting {local_filename}...")
            extract_dir = os.path.join(save_dir, os.path.splitext(local_filename)[0])
            with rarfile.RarFile(local_filename, 'r') as rar_ref:
                rar_ref.extractall(extract_dir)
            remove(local_filename)
            return extract_dir

        elif local_filename.endswith('.tif') or local_filename.endswith('.tiff'):
            print(f"Downloaded {local_filename}, no extraction needed.")
            return local_filename

        else:
            print(f"Unsupported file type for {local_filename}")
            return None

    except Exception as e:
        print(f"Failed to download or extract {url}. Error: {e}")
        return None


