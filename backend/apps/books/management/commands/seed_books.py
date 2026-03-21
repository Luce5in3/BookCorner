"""
批量添加测试图书数据
python manage.py seed_books
"""
import random
from decimal import Decimal
from datetime import date
from django.core.management.base import BaseCommand
from apps.books.models import Category, Book


class Command(BaseCommand):
    help = '添加50条测试图书数据'

    def handle(self, *args, **options):
        # 先创建分类
        categories = self.create_categories()
        
        # 图书数据
        books_data = [
            # 文学类
            {'title': '红楼梦', 'author': '曹雪芹', 'publisher': '人民文学出版社', 'category': '文学'},
            {'title': '西游记', 'author': '吴承恩', 'publisher': '人民文学出版社', 'category': '文学'},
            {'title': '三国演义', 'author': '罗贯中', 'publisher': '人民文学出版社', 'category': '文学'},
            {'title': '水浒传', 'author': '施耐庵', 'publisher': '人民文学出版社', 'category': '文学'},
            {'title': '围城', 'author': '钱钟书', 'publisher': '人民文学出版社', 'category': '文学'},
            {'title': '活着', 'author': '余华', 'publisher': '作家出版社', 'category': '文学'},
            {'title': '平凡的世界', 'author': '路遥', 'publisher': '北京十月文艺出版社', 'category': '文学'},
            {'title': '白鹿原', 'author': '陈忠实', 'publisher': '人民文学出版社', 'category': '文学'},
            {'title': '百年孤独', 'author': '加西亚·马尔克斯', 'publisher': '南海出版公司', 'category': '文学'},
            {'title': '1984', 'author': '乔治·奥威尔', 'publisher': '北京十月文艺出版社', 'category': '文学'},
            
            # 计算机类
            {'title': 'Python编程从入门到实践', 'author': 'Eric Matthes', 'publisher': '人民邮电出版社', 'category': '计算机'},
            {'title': 'JavaScript高级程序设计', 'author': 'Nicholas C.Zakas', 'publisher': '人民邮电出版社', 'category': '计算机'},
            {'title': '深入理解计算机系统', 'author': 'Randal E.Bryant', 'publisher': '机械工业出版社', 'category': '计算机'},
            {'title': '算法导论', 'author': 'Thomas H.Cormen', 'publisher': '机械工业出版社', 'category': '计算机'},
            {'title': '设计模式', 'author': 'Erich Gamma', 'publisher': '机械工业出版社', 'category': '计算机'},
            {'title': 'Java核心技术 卷I', 'author': 'Cay S.Horstmann', 'publisher': '机械工业出版社', 'category': '计算机'},
            {'title': 'C++ Primer', 'author': 'Stanley B.Lippman', 'publisher': '电子工业出版社', 'category': '计算机'},
            {'title': '代码整洁之道', 'author': 'Robert C.Martin', 'publisher': '人民邮电出版社', 'category': '计算机'},
            {'title': '重构:改善既有代码的设计', 'author': 'Martin Fowler', 'publisher': '人民邮电出版社', 'category': '计算机'},
            {'title': '数据结构与算法分析', 'author': 'Mark Allen Weiss', 'publisher': '机械工业出版社', 'category': '计算机'},
            
            # 经济管理类
            {'title': '经济学原理', 'author': '曼昆', 'publisher': '北京大学出版社', 'category': '经济管理'},
            {'title': '国富论', 'author': '亚当·斯密', 'publisher': '商务印书馆', 'category': '经济管理'},
            {'title': '穷爸爸富爸爸', 'author': '罗伯特·清崎', 'publisher': '四川人民出版社', 'category': '经济管理'},
            {'title': '影响力', 'author': '罗伯特·西奥迪尼', 'publisher': '万卷出版公司', 'category': '经济管理'},
            {'title': '从0到1', 'author': '彼得·蒂尔', 'publisher': '中信出版社', 'category': '经济管理'},
            {'title': '思考快与慢', 'author': '丹尼尔·卡尼曼', 'publisher': '中信出版社', 'category': '经济管理'},
            {'title': '高效能人士的七个习惯', 'author': '史蒂芬·柯维', 'publisher': '中国青年出版社', 'category': '经济管理'},
            {'title': '卓有成效的管理者', 'author': '彼得·德鲁克', 'publisher': '机械工业出版社', 'category': '经济管理'},
            {'title': '创新者的窘境', 'author': '克莱顿·克里斯坦森', 'publisher': '中信出版社', 'category': '经济管理'},
            {'title': '精益创业', 'author': '埃里克·莱斯', 'publisher': '中信出版社', 'category': '经济管理'},
            
            # 历史类
            {'title': '史记', 'author': '司马迁', 'publisher': '中华书局', 'category': '历史'},
            {'title': '全球通史', 'author': '斯塔夫里阿诺斯', 'publisher': '北京大学出版社', 'category': '历史'},
            {'title': '人类简史', 'author': '尤瓦尔·赫拉利', 'publisher': '中信出版社', 'category': '历史'},
            {'title': '枪炮、病菌与钢铁', 'author': '贾雷德·戴蒙德', 'publisher': '上海译文出版社', 'category': '历史'},
            {'title': '明朝那些事儿', 'author': '当年明月', 'publisher': '浙江人民出版社', 'category': '历史'},
            {'title': '万历十五年', 'author': '黄仁宇', 'publisher': '中华书局', 'category': '历史'},
            {'title': '中国大历史', 'author': '黄仁宇', 'publisher': '生活·读书·新知三联书店', 'category': '历史'},
            {'title': '叫魂', 'author': '孔飞力', 'publisher': '上海三联书店', 'category': '历史'},
            {'title': '天朝的崩溃', 'author': '茅海建', 'publisher': '生活·读书·新知三联书店', 'category': '历史'},
            {'title': '剑桥中国史', 'author': '费正清', 'publisher': '中国社会科学出版社', 'category': '历史'},
            
            # 科学类
            {'title': '时间简史', 'author': '史蒂芬·霍金', 'publisher': '湖南科学技术出版社', 'category': '科学'},
            {'title': '物种起源', 'author': '达尔文', 'publisher': '商务印书馆', 'category': '科学'},
            {'title': '自私的基因', 'author': '理查德·道金斯', 'publisher': '中信出版社', 'category': '科学'},
            {'title': '上帝掷骰子吗', 'author': '曹天元', 'publisher': '北京联合出版公司', 'category': '科学'},
            {'title': '费曼物理学讲义', 'author': '理查德·费曼', 'publisher': '上海科学技术出版社', 'category': '科学'},
            {'title': '宇宙的琴弦', 'author': '布莱恩·格林', 'publisher': '湖南科学技术出版社', 'category': '科学'},
            {'title': '从一到无穷大', 'author': '乔治·伽莫夫', 'publisher': '科学出版社', 'category': '科学'},
            {'title': '果壳中的宇宙', 'author': '史蒂芬·霍金', 'publisher': '湖南科学技术出版社', 'category': '科学'},
            {'title': '数学之美', 'author': '吴军', 'publisher': '人民邮电出版社', 'category': '科学'},
            {'title': '三体', 'author': '刘慈欣', 'publisher': '重庆出版社', 'category': '科学'},
        ]
        
        created_count = 0
        for i, book_data in enumerate(books_data):
            category_name = book_data.pop('category')
            category = categories.get(category_name)
            
            # 生成ISBN
            isbn = f'978{random.randint(1000000000, 9999999999)}'
            
            book, created = Book.objects.get_or_create(
                title=book_data['title'],
                defaults={
                    'author': book_data['author'],
                    'publisher': book_data['publisher'],
                    'category': category,
                    'isbn': isbn,
                    'price': Decimal(str(random.randint(20, 150))),
                    'publish_date': date(random.randint(2010, 2024), random.randint(1, 12), 1),
                    'language': 'zh',
                    'status': 1,
                    'description': f'《{book_data["title"]}》是{book_data["author"]}的代表作品。',
                    'total_copies': random.randint(3, 10),
                    'available_copies': random.randint(1, 5),
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'成功添加 {created_count} 本图书'))

    def create_categories(self):
        """创建分类"""
        category_data = [
            ('文学', 'WX'),
            ('计算机', 'JSJ'),
            ('经济管理', 'JJGL'),
            ('历史', 'LS'),
            ('科学', 'KX'),
        ]
        categories = {}
        
        for name, code in category_data:
            try:
                cat = Category.objects.get(name=name)
            except Category.DoesNotExist:
                cat = Category.add_root(name=name, code=code)
            categories[name] = cat
        
        return categories
