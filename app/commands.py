# -*— coding:utf-8 -*—
import click
from .models import User, Category
from app import db
from datetime import datetime

def register_commands(app):
    @app.cli.command()
    @click.option('--category',default=10,help='Quantity of categorys, default is 10.')
    @click.option('--tag', default=10, help='Quantity of tags, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--note', default=10, help='Quantity of notes, default is 10.')
    @click.option('--comment', default=300, help='Quantity of comments, default is 300.')
    @click.option('--message', default=300, help='Quantity of messages, default is 300.')
    def forge(category,tag,post,note,comment,message):
        from .fakes import fake_user, fake_category, fake_tag, fake_post, fake_note, fake_comment, fake_message

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator... ')
        fake_user()

        click.echo('Generating %d categorys... ' %category)
        fake_category()

        click.echo('Generating %d tags... ' % tag)
        fake_tag()

        click.echo('Generating %d posts... ' % post)
        fake_post()

        click.echo('Generating %d notes... ' % note)
        fake_note()

        click.echo('Generating %d comments... ' % comment)
        fake_comment()

        click.echo('Generating %d comments... ' % message)
        fake_message()

        click.echo('Done.')

    @app.cli.command()
    def bloginit():
        # 创建数据表
        click.echo('博客初始化... ')
        db.drop_all()
        db.create_all()

        # 创建管理员账户
        click.echo('创建管理员账户... ')
        admin = User(username='admin', password='acer1215', title='知行合一', subtitle='', nickname='一蓑烟雨',
                     about='编程爱好者，Web开发爱好者，此博客为练习作品...')
        db.session.add(admin)
        db.session.commit()

        # 创建默认分类
        click.echo('创建默认分类... ')
        category = Category(name='默认分类',date=datetime.now())
        db.session.add(category)
        db.session.commit()

        click.echo('博客初始化成功... ')


