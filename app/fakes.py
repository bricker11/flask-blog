# -*— coding:utf-8 -*—
from .models import User, Category, Tag, Post, Note, Comment, Message
from app import db
from faker import Faker
import random
from markdown import markdown
from bs4 import BeautifulSoup
from flask import Markup
from app.auth.views import colortable

# markdown转html
def md2html(content_md):
    extensions = ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables',
            'markdown.extensions.toc', 'markdown.extensions.fenced_code']
    content = Markup(markdown(content_md, output_format='html', extensions=extensions))
    return content


def fake_user():
    admin = User(username='admin',password='123456',title='知行合一',subtitle='点滴记录',nickname='一蓑烟雨',about='编程爱好者，Web开发爱好者，此博客为练习作品...')
    db.session.add(admin)
    db.session.commit()

fake = Faker()

def fake_category(count=10):
    category = Category(name='Default')
    db.session.add(category)

    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except db.IntegrityError:
            db.session.rollback()

def fake_tag(count=10):
    for i in range(count):
        tag = Tag(name=fake.word(),color=colortable[random.randint(0,len(colortable))])
        db.session.add(tag)
        try:
            db.session.commit()
        except db.IntegrityError:
            db.session.rollback()

def fake_post(count=50):
    for i in range(count):
        content_md = fake.text(2000)
        content_html = md2html(content_md)
        post = Post(title=fake.sentence(),content_md=content_md,content_html=content_html,
                    category=Category.query.get(random.randint(1,Category.query.count())),
                    date=fake.date_time_this_year()
                    )

        post.tags.append(Tag.query.get(random.randint(1,Tag.query.count())),)
        db.session.add(post)
    db.session.commit()

def fake_note(count=30):
    for i in range(count):
        content_md = fake.text(500)
        content_html = md2html(content_md)
        note = Note(title=fake.sentence(),
                    content_md=content_md,content_html=content_html,
                    category=Category.query.get(random.randint(1,Category.query.count())),
                    date=fake.date_time_this_year()
                    )
        db.session.add(note)
    db.session.commit()

def fake_comment(count=300):
    for i in range(count):
        if random.randint(1,10) > 5:
            flag = True
        else:
            flag = False
        # Post.query.get返回的是行对象，应该用post，不能用post_id
        comment = Comment(post=Post.query.get(random.randint(1,Post.query.count())),
                           content=fake.sentence(),
                           author=fake.name(),
                           email=fake.email(),
                           date=fake.date_time_this_year(),
                           admin_flag=flag
                           )
        db.session.add(comment)
    for i in range(50):
        if random.randint(1,10) > 5:
            flag = True
        comment = Comment(post=Post.query.get(random.randint(1,Post.query.count())),
                           content=fake.sentence(),
                           author=fake.name(),
                           email=fake.email(),
                           date=fake.date_time_this_year(),
                           admin_flag=flag,
                           replied=Comment.query.get(random.randint(1,Comment.query.count()))
                           )
        db.session.add(comment)
    db.session.commit()

def fake_message(count=300):
    for i in range(count):
        if random.randint(1,10) > 5:
            flag = True
        else:
            flag = False
        # Post.query.get返回的是行对象，应该用post，不能用post_id
        message = Message( content=fake.sentence(),
                           author=fake.name(),
                           email=fake.email(),
                           date=fake.date_time_this_year(),
                           admin_flag=flag
                           )
        db.session.add(message)
    for i in range(50):
        if random.randint(1,10) > 5:
            flag = True
        message = Message( content=fake.sentence(),
                           author=fake.name(),
                           email=fake.email(),
                           date=fake.date_time_this_year(),
                           admin_flag=flag,
                           replied=Message.query.get(random.randint(1,Comment.query.count()))
                           )
        db.session.add(message)
    db.session.commit()

