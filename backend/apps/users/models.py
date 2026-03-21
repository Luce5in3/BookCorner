"""
用户模型模块
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserRole(models.IntegerChoices):
    """用户角色枚举"""
    READER = 0, '读者'
    ADMIN = 1, '管理员'
    SUPER_ADMIN = 2, '超级管理员'


class UserStatus(models.IntegerChoices):
    """用户状态枚举"""
    DISABLED = 0, '禁用'
    ACTIVE = 1, '正常'


class UserManager(BaseUserManager):
    """自定义用户管理器"""
    
    def create_user(self, username, password=None, **extra_fields):
        """创建普通用户"""
        if not username:
            raise ValueError('用户名不能为空')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        """创建超级管理员"""
        extra_fields.setdefault('role', UserRole.SUPER_ADMIN)
        extra_fields.setdefault('status', UserStatus.ACTIVE)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('real_name', username)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级管理员必须设置 is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级管理员必须设置 is_superuser=True')
        
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    自定义用户模型
    - role: 0=读者, 1=管理员, 2=超级管理员
    - status: 0=禁用, 1=正常
    """
    
    username = models.CharField(
        '用户名',
        max_length=50,
        unique=True,
        help_text='登录用户名'
    )
    real_name = models.CharField(
        '真实姓名',
        max_length=50
    )
    email = models.EmailField(
        '邮箱',
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )
    phone = models.CharField(
        '手机号',
        max_length=20,
        null=True,
        blank=True
    )
    role = models.SmallIntegerField(
        '角色',
        choices=UserRole.choices,
        default=UserRole.READER,
        db_index=True
    )
    status = models.SmallIntegerField(
        '状态',
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
        db_index=True
    )
    avatar_url = models.URLField(
        '头像地址',
        max_length=255,
        null=True,
        blank=True
    )
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='是否可以登录 admin 后台'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.username} ({self.real_name})'
    
    @property
    def is_reader(self):
        """是否为读者"""
        return self.role == UserRole.READER
    
    @property
    def is_admin(self):
        """是否为管理员"""
        return self.role >= UserRole.ADMIN
    
    @property
    def is_super_admin(self):
        """是否为超级管理员"""
        return self.role == UserRole.SUPER_ADMIN
