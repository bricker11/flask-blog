# -*— coding:utf-8 -*—
import os
from app import create_app,db
from app.commands import register_commands
from flask_migrate import Migrate
from flask_script import Manager
from bs4 import BeautifulSoup

# 不同配置选用不同的数据库
app = create_app('development')
migrate = Migrate(app,db)
manager = Manager(app)

# 注册自定义命令
register_commands(app)

#------------------------------------------------ 自定义jinja2过滤器 ----------------------------------------------#
# 蓝本中是不能定义过滤器的
# 格式化日期时间
@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    if fmt is None:
        fmt = '%Y-%m-%d %H:%M:%S'
    return date.strftime(fmt)

# html中提取纯文本
@app.template_filter('content_text')
def _jinja2_filter_content_text(content):
    return ''.join(BeautifulSoup(content,features="html.parser").findAll(text=True))

# 提取某一分类文章中的非草稿文章
@app.template_filter('notdraft')
def _jinja2_filter_notdraft(posts):
    realposts = []
    for post in posts:
        if not post.draft_flag:
            realposts.append(post)
    return realposts



