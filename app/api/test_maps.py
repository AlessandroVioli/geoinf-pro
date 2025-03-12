import unittest

from app import create_app

class MapsTestCase(unittest.TestCase):
    
    def setUp(self) -> None:
        app = create_app('development')
        self.client = app.test_client()  # 创建测试客户端
        self.runner = app.test_cli_runner()  # 创建测试命令运行器
        return super().setUp()
    
    # 测试：查询包含指定点的地图
    def test_query_maps_by_point(self):
        response = self.client.post('/query/point',
                                    data={"coords":{"lat":51.48235585812368,"lng":-0.08531570434570314}}
                                    )
        data = response.get_data(as_text=True)
        print(data)


if __name__ == '__main__':
    unittest.main()