一个 LULC 地图集管理系统，使用 Python Flask + Leaflet 框架。

## 系统架构和设计

```
+----------------------+
|  前端 (Flask + Leaflet) |
+----------------------+
    ^                   ^
    |                   |
    |   用户交互      |   
    |   (查看、更新、导入、导出)  |
    |                   |
    +------------------+
           |           
           |
           v
+----------------------+
| 后端 (Python Flask) |
+----------------------+
    ^                   ^
    |                   |
    |   API 接口      |   
    |   (数据管理、查询)  |
    |                   |
    +------------------+
           |
           |
           v
+----------------------+
| 数据存储 (PostgreSQL) |
+----------------------+
    ^
    |
    |  LULC 地图集信息
    |  下载链接
    |  空间数据
    v


```

### 功能分解

1. **前端 (Flask + Leaflet):**

   - **地图视图:** 使用 Leaflet 创建交互地图，展示 LULC 地图集的覆盖范围。
   - **数据集列表:**  显示 LULC 地图集列表，每个地图集包含基本信息 (名称、描述、空间分辨率、CRS 等)。
   - **数据集详情:** 点击地图集，显示详细页面，包含：
     - 地图集信息 (描述、时间分辨率、空间分辨率、CRS、覆盖范围、更新频率、准确率、provider、引用、legend)。
     - 下载链接列表。
   - **区域查询:** 用户选择地图区域，查询该区域内有多少个 LULC 地图集。

2. **后端 (Python Flask):**

   - **API 接口:** 
     - `/maps`: 获取所有 LULC 地图集列表。
     - `/maps/<id>`: 获取单个地图集详细信息。
     - `/maps/<id>/downloads`: 获取单个地图集的下载链接列表。
     - `/maps/search`: 根据关键词搜索 LULC 地图集。
     - `/maps/query`: 查询特定区域内的 LULC 地图集。
     - `/maps/update`: 更新 LULC 地图集信息。
     - `/maps/import`: 导入新的 LULC 地图集数据。
     - `/maps/export`: 导出 LULC 地图集数据。

   - **数据处理:**
     - 存储 LULC 地图集信息 (名称、描述、空间分辨率、CRS 等)。
     - 存储下载链接列表。
     - 处理区域查询请求，返回包含在特定区域内的 LULC 地图集列表。

3. **数据存储 (PostgreSQL):**

   - 使用 PostgreSQL 数据库存储 LULC 地图集信息、下载链接和空间数据。


### 技术栈

- **前端:**
    - HTML, CSS, JavaScript
    - Leaflet (地图库)
- **后端:**
    - Flask (Python Web Framework)
    - Flask-Admin: 管理模型
- **数据库:**
    - PostgreSQL: 数据库存储地理数据


### 开发步骤

1.  **数据库设计:**
    -  设计 PostGRE SQL 表来存储 LULC 地图集信息、下载链接和空间数据。
2.  **Flask 应用开发:**
    -  创建 Flask 应用，定义 API 接口来处理用户请求。
    -  使用 Leaflet 构建前端地图视图和数据集列表。
3.  **数据处理逻辑:**
    -  实现 API 接口的逻辑，处理用户请求，查询数据，更新数据，导入数据等。
4.  **测试和部署:**
    -  测试 Flask 应用和 API 接口。
    -  部署 Flask 应用到 web 服务器。



## 目录结构
```
open-lulc-map/
├── app/          # Flask 应用程序代码
│   ├── models.py   # 数据库模型定义
│   ├── views.py    # API 路由和视图函数
│   ├── static/     # 静态文件，例如 CSS, JS
│   │   └── leaflet/ # Leaflet 库文件
│   ├── templates/ # 模板文件
│   └── __init__.py  
├── db/          # 数据库配置和脚本
│   └── config.py  # 数据库连接配置
├── requirements.txt # 项目依赖
├── Dockerfile      # Docker 构建文件（可选）
└── README.md      # 项目说明文件

```

**目录说明:**

-   **`lulc_map_project`:** 项目根目录。
-   **`app`:** Flask 应用程序代码目录。
    -   **`models`:** 定义数据库模型，例如 `LulcMap`, `LulcMapVersion`, `Legend` 等。
    -   **`api`:** 定义 API 路由和视图函数，处理用户请求和数据交互。
    -   **`static`:** 静态文件目录。
        -   **`leaflet`:**  包含 Leaflet 库文件。
    -   **`templates`:** HTML 模板目录。
    -   **`__init__.py`:**  Python 模块初始化文件。
    -   **`__config.py`:** 配置
-   **`db`:** 数据库配置和脚本目录。
    -   **`init.sql`:**  数据库初始化脚本
-   **`requirements.txt`:** 项目依赖包清单文件。
-   **`Dockerfile`:**  用于构建 Docker 容器的构建文件（可选）。
-   **`README.md`:**  项目说明文件，描述项目概述、功能、使用方法、依赖等信息。
