"""

种子用户数据命令
用法: python manage.py seed_users
密码统一: 123456
"""
from django.core.management.base import BaseCommand
from apps.users.models import User, UserRole, UserStatus


USERS_DATA = [
    # (username, real_name, email, phone, role, status, is_superuser, is_staff)
    ('admin',      '超级管理员', 'admin@bookcorner.com',      '13800000001', UserRole.SUPER_ADMIN, UserStatus.ACTIVE,   True,  True),
    ('librarian1', '李馆员',     'librarian1@bookcorner.com', '13800000002', UserRole.ADMIN,       UserStatus.ACTIVE,   False, True),
    ('librarian2', '王馆员',     'librarian2@bookcorner.com', '13800000003', UserRole.ADMIN,       UserStatus.ACTIVE,   False, True),
    ('user1',      '张三',       'zhangsan@bookcorner.com',   '13900000001', UserRole.READER,      UserStatus.ACTIVE,   False, False),
    ('user2',      '李四',       'lisi@bookcorner.com',       '13900000002', UserRole.READER,      UserStatus.ACTIVE,   False, False),
    ('user3',      '王五',       'wangwu@bookcorner.com',     '13900000003', UserRole.READER,      UserStatus.ACTIVE,   False, False),
    ('user4',      '赵六',       'zhaoliu@bookcorner.com',    '13900000004', UserRole.READER,      UserStatus.ACTIVE,   False, False),
    ('user5',      '孙七',       'sunqi@bookcorner.com',      '13900000005', UserRole.READER,      UserStatus.ACTIVE,   False, False),
    ('user6',      '周八',       'zhouba@bookcorner.com',     '13900000006', UserRole.READER,      UserStatus.ACTIVE,   False, False),
    ('user7',      '吴九',       'wujiu@bookcorner.com',      '13900000007', UserRole.READER,      UserStatus.DISABLED, False, False),
]

DEFAULT_PASSWORD = '123456'


class Command(BaseCommand):
    help = '初始化测试用户数据（密码统一为123456）'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for username, real_name, email, phone, role, status, is_superuser, is_staff in USERS_DATA:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'real_name': real_name,
                    'email': email,
                    'phone': phone,
                    'role': role,
                    'status': status,
                    'is_superuser': is_superuser,
                    'is_staff': is_staff,
                }
            )
            if created:
                user.set_password(DEFAULT_PASSWORD)
                user.save()
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  创建用户: {username} ({real_name})'))
            else:
                # 已存在则更新密码确保可登录
                user.set_password(DEFAULT_PASSWORD)
                user.real_name = real_name
                user.email = email
                user.phone = phone
                user.role = role
                user.status = status
                user.is_superuser = is_superuser
                user.is_staff = is_staff
                user.save()
                updated_count += 1
                self.stdout.write(f'  更新用户: {username} ({real_name})')

        self.stdout.write(self.style.SUCCESS(
            f'\n完成！创建 {created_count} 个用户，更新 {updated_count} 个用户。'
        ))
        self.stdout.write(f'统一密码: {DEFAULT_PASSWORD}')

