"""
批量添加测试用户
python manage.py seed_users
"""
from django.core.management.base import BaseCommand
from apps.users.models import User


class Command(BaseCommand):
    help = '添加10个测试用户'

    def handle(self, *args, **options):
        created_count = 0
        
        for i in range(1, 11):
            username = f'user{i}'
            
            if User.objects.filter(username=username).exists():
                self.stdout.write(f'用户 {username} 已存在，跳过')
                continue
            
            user = User.objects.create_user(
                username=username,
                password='123456',
                real_name=f'测试用户{i}',
                email=f'user{i}@example.com',
                phone=f'1380000{i:04d}',
                role=0,  # 读者
                status=1,  # 正常
            )
            created_count += 1
            self.stdout.write(f'创建用户: {username}')
        
        self.stdout.write(self.style.SUCCESS(f'成功添加 {created_count} 个用户'))
