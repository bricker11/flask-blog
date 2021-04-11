# -*— coding:utf-8 -*—
from flask import render_template,request,session,redirect,url_for,abort,jsonify,current_app
from . import main
from .forms import SearchForm
from app import db
# 导入models时，models中定义的load_user生效
from app.models import User, Post, Note, Category, Tag, Comment, Message
from datetime import datetime
from sqlalchemy import and_, or_
import os, requests, re
from PIL import Image


# 首页
@main.route('/',defaults={'page':1})
@main.route('/page/<int:page>')
def index(page):
    # 获取当日bing图片,缩小分辨率并缓存为今日的背景图
    base_path = os.path.abspath(os.path.dirname('__FILE__')) + '/app/static/img/'
    img_path = base_path + datetime.now().strftime('%Y_%m_%d') + '.jpg'
    # 判断是否存在今日的背景图
    if  not os.path.exists(img_path):
        # 删除之前的背景图
        imgs = os.listdir(base_path)
        for img in imgs:
            if img[0:2] == '20':
                os.remove(base_path + img)
        # 获取今日的背景图
        bing_url = 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1'
        img_url = 'https://www.bing.com' + requests.get(bing_url).json()['images'][0]['url']
        r = requests.get(img_url)
        with open(img_path, 'wb') as f:
             f.write(r.content)
        # 降低图片分辨率
        img = Image.open(img_path)
        img = img.resize((480, 270))
        img.save(img_path)
    # 分页
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
    pagination = Post.query.filter_by(draft_flag=False).order_by(Post.date.desc()).paginate(page,per_page=per_page)
    posts = pagination.items
    # 渲染侧边栏信息
    form = SearchForm()
    categorys = Category.query.all()
    tags = Tag.query.all()
    # 管理员信息
    admin = User.query.first()
    # posts既用于显示列表，也可用于侧边栏显示最新文章
    return render_template('index.html',pagination=pagination,posts=posts,
                           categorys=categorys,tags=tags,form=form,
                           admin=admin,datetime=datetime.now())

# 正文页
@main.route('/post/<int:post_id>',defaults={'page':1},methods=['GET','POST'])
@main.route('/post/<int:post_id>/',defaults={'page':1},methods=['GET','POST'])
@main.route('/post/<int:post_id>/<int:page>',methods=['GET','POST'])
def post(post_id,page):
    post = Post.query.filter_by(id=post_id).first()
    post.read_count = post.read_count + 1
    db.session.commit()
    # 分页
    per_page = current_app.config['FLASKY_COMMENTS_PER_PAGE']
    pagination = Comment.query.filter(and_(Comment.post_id==post_id,Comment.replied_id.is_(None))).order_by(Comment.date.desc()).paginate(page, per_page=per_page)
    comments = pagination.items
    replies = Comment.query.filter(and_(Comment.post_id==post_id,Comment.replied_id.isnot(None))).order_by(Comment.date.desc()).all()
    # 渲染侧边栏信息
    form = SearchForm()
    posts = Post.query.filter_by(draft_flag=False).order_by(Post.date.desc()).limit(5)
    categorys = Category.query.all()
    tags = Tag.query.all()
    # 管理员信息
    admin = User.query.first()
    return render_template('post.html',post=post,comments=comments,pagination=pagination,replies=replies,
                           posts=posts,categorys=categorys,tags=tags,form=form,
                           admin=admin,datetime=datetime.now())

# 归档页
@main.route('/archive')
def archive():
    arch_posts = Post.query.filter_by(draft_flag=False).order_by(Post.date.desc()).all()
    arch_list = {}
    for post in arch_posts:
        # 必须确保数据库中文字时间字段值有效，可用try语句确保安全
        date = str(post.date.strftime("%Y-%m"))
        if date in arch_list:
            arch_list[date].append(post)
        else:
            arch_list[date] = [post]
    # 渲染侧边栏信息
    form = SearchForm()
    posts = Post.query.filter_by(draft_flag=False).order_by(Post.date.desc()).limit(5)
    categorys = Category.query.all()
    tags = Tag.query.all()
    # 管理员信息
    admin = User.query.first()
    return render_template('archive.html',arch_list=arch_list,
                           posts=posts,categorys=categorys,tags=tags,form=form,
                           admin=admin,datetime=datetime.now())

# 笔记页
@main.route('/note',defaults={'page':1})
@main.route('/note/<int:page>')
def note(page):
    # 分页
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
    pagination = Note.query.order_by(Note.date.desc()).paginate(page, per_page=per_page)
    notes = pagination.items
    # 渲染侧边栏信息
    form = SearchForm()
    categorys = Category.query.all()
    tags = Tag.query.all()
    # 管理员信息
    admin = User.query.first()
    return render_template('note.html',notes=notes,pagination=pagination,
                           categorys=categorys,tags=tags,form=form,
                           admin=admin,datetime=datetime.now())

# 留言页
@main.route('/message',defaults={'page':1},methods=['GET','POST'])
@main.route('/message/<int:page>',methods=['GET','POST'])
def message(page):
    # 分页
    per_page = current_app.config['FLASKY_MESSAGES_PER_PAGE']
    pagination = Message.query.filter(Message.replied_id.is_(None)).order_by(Message.date.desc()).paginate(page, per_page=per_page)
    messages = pagination.items
    replies = Message.query.filter(Message.replied_id.isnot(None)).order_by(Message.date.desc()).all()
    total = len(Message.query.all())
    # 渲染侧边栏信息
    form = SearchForm()
    posts = Post.query.filter_by(draft_flag=False).order_by(Post.date.desc()).limit(5)
    categorys = Category.query.all()
    tags = Tag.query.all()
    # 管理员信息
    admin = User.query.first()
    # 留言与文章无关，所以这里留言总数total要单独传入
    return render_template('message.html',total=total,messages=messages,replies=replies,pagination=pagination,
                           posts=posts,categorys=categorys,tags=tags,form=form,
                           admin=admin,datetime=datetime.now())

# 关于页
@main.route('/about')
def about():
    # 渲染侧边栏信息
    form = SearchForm()
    posts = Post.query.filter_by(draft_flag=False).order_by(Post.date.desc()).limit(5)
    categorys = Category.query.all()
    tags = Tag.query.all()
    # 管理员信息
    admin = User.query.first()
    return render_template('about.html',posts=posts,category=category,
                           categorys=categorys,tags=tags,form=form,
                           admin=admin,datetime=datetime.now())


# 文章使用的分类和标签
# 分类页
# 当传入 5 时，会自动加上 / ,变成 5/ ,导致路由匹配失败（why?），故这里增加一条结尾带 / 的路由
@main.route('/category/<int:cate_id>',defaults={'page':1})
@main.route('/category/<int:cate_id>/',defaults={'page':1})
@main.route('/category/<int:cate_id>/<int:page>')
def category(cate_id,page):
    # 分页
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
    pagination = Post.query.filter_by(draft_flag=False).filter_by(category_id=cate_id).order_by(Post.date.desc()).paginate(page, per_page=per_page)
    cate_posts = pagination.items
    category = Category.query.filter_by(id=cate_id).first()
    # 渲染侧边栏信息
    form = SearchForm()
    posts = Post.query.filter_by(draft_flag=False).order_by(Post.date.desc()).limit(5)
    categorys = Category.query.all()
    tags = Tag.query.all()
    # 管理员信息
    admin = User.query.first()
    return render_template('category.html',category=category,pagination=pagination,cate_posts=cate_posts,
                           posts=posts,categorys=categorys,tags=tags,form=form,
                           admin=admin,datetime=datetime.now())

# 标签页
@main.route('/tag/<int:tag_id>',defaults={'page':1})
@main.route('/tag/<int:tag_id>/',defaults={'page':1})
@main.route('/tag/<int:tag_id>/<int:page>')
def tag(tag_id,page):
    tag = Tag.query.filter_by(id=tag_id).first()
    # 文章按时间（id）倒序输出
    tag_posts = []
    for post in tag.posts:
        if not post.draft_flag:
            tag_posts.insert(0,post)
    # 自定义分页机制
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']          #每页条数
    class Pagination:
        has_prev = False   #有上一页
        has_next = False   #有下一页
        page = 1           #当前页
        pages = 1          #总页数
    pagination = Pagination()
    # 请求页超出总页面数时，返回404错误
    if len(tag_posts) <= per_page * (page-1) and len(tag_posts) != 0:
        abort(404)
    # 请求页有效时，根据请求页位置分类处理
    if len(tag_posts) <= per_page:
        pagination.has_prev = False
        pagination.has_next = False
        pagination.page = 1
        pagination.pages = 1
        tag_posts = tag_posts
    elif per_page * page >= len(tag_posts):
        pagination.has_prev = True
        pagination.has_next = False
        pagination.page = page
        pagination.pages = page
        tag_posts = tag_posts[(page-1)*per_page:]
    else:
        pagination.has_prev = True
        pagination.has_next = True
        pagination.page = page
        if len(tag_posts) % per_page == 0:
            pagination.pages = int(len(tag_posts) / per_page)
        else:
            pagination.pages = int(len(tag_posts) / per_page) + 1
        tag_posts = tag_posts[(page-1)*per_page:page*per_page]
    # 渲染侧边栏信息
    form = SearchForm()
    posts = Post.query.filter_by(draft_flag=False).order_by(Post.date.desc()).limit(5)
    categorys = Category.query.all()
    tags = Tag.query.all()
    # 管理员信息
    admin = User.query.first()
    return render_template('tag.html',tag=tag,pagination=pagination,tag_posts=tag_posts,
                           posts=posts,categorys=categorys,tags=tags,form=form,
                           admin=admin,datetime=datetime.now())

# 笔记使用的分类和标签
# 分类页
@main.route('/category_note/<int:cate_id>',defaults={'page':1})
@main.route('/category_note/<int:cate_id>/',defaults={'page':1})
@main.route('/category_note/<int:cate_id>/<int:page>')
def category_note(cate_id,page):
    # 分页
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
    pagination = Note.query.filter_by(category_id=cate_id).order_by(Note.date.desc()).paginate(page, per_page=per_page)
    cate_notes = pagination.items
    category = Category.query.filter_by(id=cate_id).first()
    # 渲染侧边栏信息
    form = SearchForm()
    categorys = Category.query.all()
    tags = Tag.query.all()
    # 管理员信息
    admin = User.query.first()
    return render_template('category_note.html',category=category,pagination=pagination,cate_notes=cate_notes,
                           categorys=categorys,tags=tags,form=form,
                           admin=admin,datetime=datetime.now())

# 标签页
@main.route('/tag_note/<int:tag_id>',defaults={'page':1})
@main.route('/tag_note/<int:tag_id>/',defaults={'page':1})
@main.route('/tag_note/<int:tag_id>/<int:page>')
def tag_note(tag_id,page):
    tag = Tag.query.filter_by(id=tag_id).first()
    # 文章按时间（id）倒序输出
    tag_notes = []
    for note in tag.notes:
        tag_notes.insert(0,note)
    # 自定义分页机制
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']           #每页条数
    class Pagination:
        has_prev = False   #有上一页
        has_next = False   #有下一页
        page = 1           #当前页
        pages = 1          #总页数
    pagination = Pagination()
    # 请求页超出总页面数时，返回404错误
    if len(tag_notes) <= per_page * (page-1) and len(tag_notes) != 0:
        abort(404)
    # 请求页有效时，根据请求页位置分类处理
    if len(tag_notes) <= per_page:
        pagination.has_prev = False
        pagination.has_next = False
        pagination.page = 1
        pagination.pages = 1
        tag_notes = tag_notes
    elif per_page * page >= len(tag_notes):
        pagination.has_prev = True
        pagination.has_next = False
        pagination.page = page
        pagination.pages = page
        tag_notes = tag_notes[(page-1)*per_page:]
    else:
        pagination.has_prev = True
        pagination.has_next = True
        pagination.page = page
        if len(tag_notes) % per_page == 0:
            pagination.pages = int(len(tag_notes) / per_page)
        else:
            pagination.pages = int(len(tag_notes) / per_page) + 1
        tag_notes = tag_notes[(page-1)*per_page:page*per_page]
    # 渲染侧边栏信息
    form = SearchForm()
    categorys = Category.query.all()
    tags = Tag.query.all()
    # 管理员信息
    admin = User.query.first()
    return render_template('tag_note.html',tag=tag,pagination=pagination,tag_notes=tag_notes,
                           categorys=categorys,tags=tags,form=form,
                           admin=admin,datetime=datetime.now())

# 文章搜索结果页面
@main.route('/search_post',defaults={'page':1},methods=['GET','POST'])
@main.route('/search_post/<int:page>',methods=['GET','POST'])
def search_post(page):
    # 渲染侧边栏信息
    form = SearchForm()
    posts = Post.query.filter_by(draft_flag=False).order_by(Post.date.desc()).limit(5)
    categorys = Category.query.all()
    tags = Tag.query.all()
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
    # 管理员信息
    admin = User.query.first()
    # 搜索结果
    if form.validate_on_submit():
        pagination = Post.query.filter(or_(Post.title.like('%' + form.keyword.data + '%'),Post.content_md.like('%' + form.keyword.data + '%'))) \
            .order_by(Post.date.desc()).paginate(page, per_page=per_page)
        match_posts = pagination.items
        session['searched'] = True
        session['keyword'] = form.keyword.data
        return render_template('search_post.html', pagination=pagination, match_posts=match_posts,
                               posts=posts,categorys=categorys, tags=tags, form=form,
                               admin=admin,datetime=datetime.now())
    if session.get('searched') == True:
        pagination = Post.query.filter(or_(Post.title.like('%' + session.get('keyword') + '%'), Post.content_md.like('%' + session.get('keyword') + '%'))) \
            .order_by(Post.date.desc()).paginate(page, per_page=per_page)
        match_posts = pagination.items
        return render_template('search_post.html', pagination=pagination, match_posts=match_posts,
                                posts=posts,categorys=categorys, tags=tags, form=form,
                               admin=admin,datetime=datetime.now())
    else:
        return redirect(url_for('main.index'))

# 笔记搜索结果页面
@main.route('/search_note',defaults={'page':1},methods=['GET','POST'])
@main.route('/search_note/<int:page>',methods=['GET','POST'])
def search_note(page):
    # 渲染侧边栏信息
    form = SearchForm()
    categorys = Category.query.all()
    tags = Tag.query.all()
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
    # 管理员信息
    admin = User.query.first()
    # 搜索结果
    if form.validate_on_submit():
        pagination = Note.query.filter(or_(Note.title.like('%' + form.keyword.data + '%'),Note.content_md.like('%' + form.keyword.data + '%'))) \
            .order_by(Note.date.desc()).paginate(page, per_page=per_page)
        notes = pagination.items
        session['searched'] = True
        session['keyword'] = form.keyword.data
        return render_template('search_note.html', pagination=pagination, notes=notes,
                               categorys=categorys, tags=tags, form=form,
                               admin=admin,datetime=datetime.now())
    if session.get('searched') == True:
        pagination = Note.query.filter(or_(Note.title.like('%' + session.get('keyword') + '%'), Note.content_md.like('%' + session.get('keyword') + '%'))) \
            .order_by(Note.date.desc()).paginate(page, per_page=per_page)
        notes = pagination.items
        return render_template('search_note.html', pagination=pagination, notes=notes,
                               categorys=categorys, tags=tags, form=form,
                               admin=admin,datetime=datetime.now())
    else:
        return redirect(url_for('main.note'))


#-------------------------------------------------- api -----------------------------------------------#
# 发布评论处理
@main.route('/api/comment',methods=['GET','POST'])
def comment_api():
    post_id = request.form['post_id']
    content = request.form['content']
    author = request.form['author']
    email = request.form['email']
    password = request.form['password']

    pattern = '^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'
    email_ok = re.match(pattern, email, flags=0)
    if content != '' and author != '' and email != '':
        if email_ok != None:
            admin_flag = False
            user = User.query.first()
            if user.verify_password(password):
                admin_flag = True
                author = user.nickname
            comment = Comment(post_id=post_id, content=content, author=author,
                              email=email, date=datetime.now(), admin_flag=admin_flag)
            db.session.add(comment)
            db.session.commit()
            result = {'status': 0}
        else:
            result = {'status': 1}
    else:
        result = {'status': 2}
    return jsonify(result)

# 发布留言处理
@main.route('/api/message',methods=['GET','POST'])
def message_api():
    content = request.form['content']
    author = request.form['author']
    email = request.form['email']
    password = request.form['password']

    pattern = '^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'
    email_ok = re.match(pattern, email, flags=0)
    if content != '' and author != '' and email != '':
        if email_ok != None:
            admin_flag = False
            user = User.query.first()
            if user.verify_password(password):
                admin_flag = True
                author = user.nickname
            message = Message(content=content, author=author,
                              email=email, date=datetime.now(), admin_flag=admin_flag)
            db.session.add(message)
            db.session.commit()
            result = {'status': 0}
        else:
            result = {'status': 1}
    else:
        result = {'status': 2}
    return jsonify(result)

# 回复评论处理
@main.route('/api/comment_reply',methods=['GET','POST'])
def comment_reply_api():
    content = request.form['content']
    author = request.form['author']
    email = request.form['email']
    comment_id = request.form['comment_id']
    password = request.form['password']
    code = int(request.form['code'])

    post_id = Comment.query.filter_by(id=comment_id).first().post_id
    pattern = '^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'
    email_ok = re.match(pattern,email,flags=0)
    if content != '' and author != '' and email != '':
        if email_ok != None:
            admin_flag = False
            user = User.query.first()
            if user.verify_password(password):
                admin_flag = True
                author = user.nickname
            if code == 0:
                comment = Comment(post_id=post_id,content=content, author=author,
                              email=email, date=datetime.now(), admin_flag=admin_flag, replied_id=comment_id)
            else:
                origin_author = request.form['origin_author']
                content = '回复@' + origin_author + '#  ' + content
                comment = Comment(post_id=post_id, content=content, author=author,
                                  email=email, date=datetime.now(), admin_flag=admin_flag, replied_id=comment_id)
            db.session.add(comment)
            db.session.commit()
            result = {'status': 0}
        else:
            result = {'status': 1}
    else:
        result = {'status': 2}
    return jsonify(result)

# 回复留言处理
@main.route('/api/message_reply',methods=['GET','POST'])
def message_reply_api():
    content = request.form['content']
    author = request.form['author']
    email = request.form['email']
    message_id = request.form['message_id']
    password = request.form['password']
    code = int(request.form['code'])

    pattern = '^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'
    email_ok = re.match(pattern,email,flags=0)
    if content != '' and author != '' and email != '':
        if email_ok != None:
            admin_flag = False
            user = User.query.first()
            if user.verify_password(password):
                admin_flag = True
                author = user.nickname
            if code == 0:
                message = Message(content=content, author=author,
                              email=email, date=datetime.now(), admin_flag=admin_flag, replied_id=message_id)
            else:
                origin_author = request.form['origin_author']
                content = '回复@' + origin_author + '#  ' + content
                message = Message(content=content, author=author,
                                  email=email, date=datetime.now(), admin_flag=admin_flag, replied_id=message_id)
            db.session.add(message)
            db.session.commit()
            result = {'status': 0}
        else:
            result = {'status': 1}
    else:
        result = {'status': 2}
    return jsonify(result)