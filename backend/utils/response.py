"""
统一响应封装模块
"""
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import status


class APIResponse(Response):
    """
    统一 API 响应格式
    {
        "code": 200,
        "message": "success",
        "data": {...}
    }
    """
    
    def __init__(self, data=None, code=200, message='success', status_code=None, **kwargs):
        response_data = {
            'code': code,
            'message': message,
            'data': data
        }
        if status_code is None:
            status_code = status.HTTP_200_OK
        super().__init__(data=response_data, status=status_code, **kwargs)


def success_response(data=None, message='success', code=200):
    """成功响应"""
    return APIResponse(data=data, code=code, message=message)


def error_response(message='error', code=400, data=None, status_code=None):
    """错误响应"""
    if status_code is None:
        status_code = status.HTTP_400_BAD_REQUEST
    return APIResponse(data=data, code=code, message=message, status_code=status_code)


def custom_exception_handler(exc, context):
    """
    自定义异常处理器，统一响应格式
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        # 获取错误信息
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                message = str(response.data['detail'])
            else:
                # 处理字段验证错误
                errors = []
                for field, msgs in response.data.items():
                    if isinstance(msgs, list):
                        errors.append(f"{field}: {', '.join(str(m) for m in msgs)}")
                    else:
                        errors.append(f"{field}: {msgs}")
                message = '; '.join(errors) if errors else '请求错误'
        elif isinstance(response.data, list):
            message = '; '.join(str(item) for item in response.data)
        else:
            message = str(response.data)
        
        # 构建统一响应格式
        response.data = {
            'code': response.status_code,
            'message': message,
            'data': None
        }
    
    return response
