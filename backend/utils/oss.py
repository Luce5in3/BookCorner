"""
阿里云 OSS 文件上传工具
"""
import os
import uuid
from datetime import datetime

import oss2
from django.conf import settings


def get_oss_bucket():
    """获取 OSS Bucket 实例"""
    auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
    endpoint = f'https://{settings.OSS_ENDPOINT}'
    bucket = oss2.Bucket(auth, endpoint, settings.OSS_BUCKET)
    return bucket


def upload_file_to_oss(file_obj, folder='covers'):
    """
    上传文件到 OSS
    :param file_obj: Django UploadedFile 对象
    :param folder: 子文件夹名称
    :return: 文件的公网访问 URL
    """
    # 生成唯一文件名
    ext = os.path.splitext(file_obj.name)[1].lower()
    if not ext:
        ext = '.jpg'
    date_path = datetime.now().strftime('%Y%m')
    filename = f"{uuid.uuid4().hex}{ext}"
    object_key = f"{settings.OSS_PREFIX}{folder}/{date_path}/{filename}"

    bucket = get_oss_bucket()
    # 上传文件
    bucket.put_object(object_key, file_obj.read())

    # 返回公网访问 URL
    url = f"https://{settings.OSS_BASE_URL}/{object_key}"
    return url
