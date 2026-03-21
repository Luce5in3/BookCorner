"""
分页配置模块
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    标准分页类
    - page: 页码
    - page_size: 每页数量（默认10，最大100）
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        统一分页响应格式
        {
            "code": 200,
            "message": "success",
            "data": {
                "count": 100,
                "next": "...",
                "previous": "...",
                "results": [...]
            }
        }
        """
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
            }
        })
