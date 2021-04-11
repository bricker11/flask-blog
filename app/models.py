# -*— coding:utf-8 -*—
from flask_login import UserMixin #其中实现了一些LoginManager需要的回调函数，具有通用性，用户不用自己实现
from werkzeug.security import generate_password_hash, check_password_hash
from . import db,login_manager
from datetime import datetime

# 用户表
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    title = db.Column(db.String(64))
    subtitle = db.Column(db.String(64))
    nickname = db.Column(db.String(64))
    about = db.Column(db.Text)

    # 密码加密及验证
    @property
    def password(self):
        raise AttributeError('密码不可读')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
# 分类表
class Category(db.Model):
    __tablename__ = 'categorys'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    date = db.Column(db.DateTime, default=datetime.utcnow(), index=True)
    posts = db.relationship('Post', back_populates='category')
    notes = db.relationship('Note', back_populates='category')
# 标签表
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    color = db.Column(db.String(32))
    date = db.Column(db.DateTime, default=datetime.utcnow(), index=True)
# 多对多中间表
post_tag = db.Table('post_tags',
                    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True))
note_tag = db.Table('note_tags',
                    db.Column('note_id', db.Integer, db.ForeignKey('notes.id'), primary_key=True),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True))
# 文章表
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    content_md = db.Column(db.Text)    #Markdown源文档
    content_html = db.Column(db.Text)  #渲染后的Html文档
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow(), index=True)
    read_count = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categorys.id'))  #分类
    category = db.relationship('Category', back_populates='posts')
    tags = db.relationship('Tag', secondary=post_tag, backref=db.backref('posts'))  #标签，Tag表中通过Tag.posts可访问当前标签下的文章
    logo_image_url = db.Column(db.String(256))  #首页缩略图url
    draft_flag = db.Column(db.Boolean,default=False) #是否是草稿
    comments = db.relationship('Comment', back_populates='post', cascade='all')  #评论，级联删除
    attachments = db.relationship('Attachment', back_populates='post')  #附件
# 笔记表
class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    content_md = db.Column(db.Text)
    content_html = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.now(), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categorys.id'))
    category = db.relationship('Category', back_populates='notes')
    tags = db.relationship('Tag', secondary=note_tag, backref=db.backref('notes'))  #Tag表中通过Tag.notes可访问当前标签下的笔记
    attachments = db.relationship('Attachment', back_populates='note')
# 评论表
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    post = db.relationship('Post', back_populates='comments')
    content = db.Column(db.Text)  #纯文本评论
    author = db.Column(db.String(64))
    email = db.Column(db.String(64))
    date = db.Column(db.DateTime, default=datetime.now(), index=True)
    admin_flag = db.Column(db.Boolean, default=False)
    # 邻接表,用于回复评论，回复本质上也是评论
    replied_id = db.Column(db.Integer, db.ForeignKey('comments.id'))  #回复，属于某一条评论
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id]) #一条回复
    replies = db.relationship('Comment', back_populates='replied', cascade='all') #评论删除，则回复也级联删除
# 留言表
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    author = db.Column(db.String(64))
    email = db.Column(db.String(64))
    date = db.Column(db.DateTime, default=datetime.now(), index=True)
    admin_flag = db.Column(db.Boolean, default=False)
    # 邻接表
    replied_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    replied = db.relationship('Message', back_populates='replies', remote_side=[id])
    replies = db.relationship('Message', back_populates='replied', cascade='all')
# 附件表
class Attachment(db.Model):
    __tablename__ = 'attachments'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256))    #文件全名（含后缀）
    securename = db.Column(db.String(256))  #唯一文件名
    filesize = db.Column(db.String(32))     #文件大小（字符串格式）
    date = db.Column(db.DateTime, default=datetime.now(), index=True)
    local = db.Column(db.String(256))       #本地存储地址，用于存储/删除
    url = db.Column(db.String(256))         #网络url，用于Markdown链接图片
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    post = db.relationship('Post', back_populates='attachments')
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'))
    note = db.relationship('Note', back_populates='attachments')
# login_manger需要实现的获取用户对象的函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))