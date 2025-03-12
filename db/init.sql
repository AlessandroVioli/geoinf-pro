create type coverage_type as enum('Global', 'Regional');

-- 创建 lulc_maps 表
CREATE TABLE lulc_maps (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL, -- 地图集名称
    description TEXT, -- 地图集描述
    resolution REAL, -- 空间分辨率，单位: 米或度
    crs VARCHAR(255), -- 空间参考系统，例如 "EPSG:4326"
    coverage coverage_type, -- 覆盖范围描述
    update_frequency VARCHAR(255), -- 更新频率，例如 "每年", "每月", "实时"
    provider VARCHAR(255), -- 数据提供者
    citation TEXT -- 引用信息
);

-- 创建 legends 表
CREATE TABLE lulc_map_legends (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255), -- Legend名称
    legend_text TEXT -- 图例内容
);

-- 创建 lulc_map_versions 表
CREATE TABLE lulc_map_versions (
    id SERIAL PRIMARY KEY,
    map_id INT REFERENCES lulc_maps(id), -- 外键，指向 lulc_maps 表的 id
    version VARCHAR(255), -- 版本号
    temporal_extent INT, -- 时间分辨率
    accuracy TEXT, -- OA等信息
    legend_id INT REFERENCES lulc_map_legends(id)-- 外键，指向 lulc_map_legends 表的 id
);

-- 创建 map_legend_downloads 表
CREATE TABLE lulc_map_downloads (
    id SERIAL PRIMARY KEY,
    map_id INTEGER NOT NULL REFERENCES lulc_maps(id),
    download_url VARCHAR(255) NOT NULL, -- 下载链接
    download_link_name VARCHAR(255) NOT NULL,
    description TEXT --下载说明
    geometry JSONB NOT NULL, -- Geometry 对象
);

-- 创建 lulc_map_spatial_data 表
CREATE TABLE lulc_map_spatial_data (
    id SERIAL PRIMARY KEY,
    map_id INTEGER NOT NULL REFERENCES lulc_maps(id),
    map_version_id INTEGER NOT NULL REFERENCES lulc_map_versions(id),
    spatial_type VARCHAR(50) NOT NULL, -- 空间类型（点、线、面）
    geometry JSONB NOT NULL, -- Geometry 对象
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);