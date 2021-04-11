# -*— coding:utf-8 -*—
from flask import render_template,request,session,redirect,url_for,abort,flash,json,jsonify,Markup,current_app
from flask_login import login_required,current_user,login_user,logout_user
from . import auth
from .forms import LoginForm, PostForm, SettingForm
from app import db
# 导入models时，models中定义的load_user生效
from app.models import User, Post, Note, Category, Tag, Comment, Message, Attachment
from datetime import datetime
from sqlalchemy import and_, or_
import os, random
from markdown import markdown


# tag颜色源
colortable = ['Crimson','Pink','DeepPink','Magenta','Purple','BlueViolet','MediumSlateBlue',
          'Blue','RoyalBlue','DoderBlue','SteelBlue','DeepSkyBlue','DarkTurquoise','DarkCyan',
          'Auqamarin','MediumSpringGreen','LimeGreen','Green','GreenYellow','ForestGreen','PaleGodenrod',
          'Orange','OrangeRed','Red','DimGray','#ffd400','#33a3dc','#008792','#007947','#f26522',
          '#733a31','#6c4c49','#1b315e','#2468a2','#ef4136','#ed1941','#7fb80e','#1a2933','#2a5caa','#fcaf17']


# markdown转html
def md2html(content_md):
    extensions = ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables',
            'markdown.extensions.toc', 'markdown.extensions.fenced_code']
    content_html = Markup(markdown(content_md, output_format='html5', extensions=extensions))
    return content_html

# 后台登录页
@auth.route('/login',methods=['GET','POST'])
def login():
    form= LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, True)
            return redirect(url_for('auth.index'))
        flash('用户名或密码错误')
    return render_template('admin/login.html',form=form)

# 后台退出
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出')
    return redirect(url_for('auth.login'))

# 后台首页
@auth.route('/')
@login_required
def index():
    posts = Post.query.order_by(Post.date.desc()).limit(10)
    post_num = len(Post.query.all())
    note_num = len(Note.query.all())
    category_num = len(Category.query.all())
    tag_num = len(Tag.query.filter(Tag.posts).all())
    comment_num = len(Comment.query.all())
    message_num = len(Message.query.all())
    info = {"post_num": post_num, "note_num":note_num, "category_num":category_num,"tag_num":tag_num,
            "comment_num":comment_num,"message_num":message_num}
    return render_template('admin/index.html',posts=posts,info=info)

# 后台设置页
@auth.route('/setting',methods=['GET','POST'])
@login_required
def setting():
    form = SettingForm()
    user = User.query.first()
    if form.validate_on_submit():
        user.title = form.title.data
        user.subtitle = form.subtitle.data
        user.nickname = form.nickname.data
        user.about = form.about.data
        db.session.commit()
        flash('修改成功')
        return redirect(url_for('auth.setting'))
    form.title.data = user.title
    form.subtitle.data = user.subtitle
    form.nickname.data = user.nickname
    form.about.data = user.about
    return render_template('admin/setting.html',form=form,user=user,rnd=datetime.now().strftime("%Y%m%d%H%M%S"))

# 后台写文章页
@auth.route('/writepost',methods=['GET','POST'])
@login_required
def writepost():
    form = PostForm()
    if len(Post.query.all()) == 0:
        newpost_id = 1
    else:
        newpost_id = Post.query.order_by(Post.id.desc()).first().id + 1
    tags = Tag.query.all()
    if form.validate_on_submit():
        tags_id = form.tags.data.split(',')
        content_md = form.content_md.data
        content_html = md2html(content_md)
        post = Post.query.filter_by(id=newpost_id).first()
        if post:
            post.title = form.title.data
            post.category_id = form.category.data
            post.content_md = content_md
            post.content_html = content_html
            post.date = datetime.now()
            post.draft_flag = False
            if tags_id != ['']:
                for tag_id in tags_id:
                    tag = Tag.query.filter_by(id=tag_id).first()
                    post.tags.append(tag)
            db.session.commit()
        else:
            post = Post(id=newpost_id,title=form.title.data,content_html=content_html,content_md=content_md,
                    category_id=form.category.data,date=datetime.now(),draft_flag=False)
            if tags_id != ['']:
                for tag_id in tags_id:
                    tag = Tag.query.filter_by(id=tag_id).first()
                    post.tags.append(tag)
            db.session.add(post)
            db.session.commit()
        flash('发布成功')
        return redirect(url_for('auth.index'))
    return render_template('admin/writepost.html',form=form,tags=tags,newpost_id=newpost_id)

# 后台修改文章页
@auth.route('/editpost/<int:post_id>',methods=['GET','POST'])
@login_required
def editpost(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    attachments = Attachment.query.filter_by(post_id=post_id).all()
    tags = Tag.query.all()
    if form.validate_on_submit():
        tags_id = form.tags.data.split(',')
        post.title = form.title.data
        post.content_md = form.content_md.data
        post.content_html = md2html(form.content_md.data)
        post.category_id = form.category.data
        post.draft_flag = False
        if tags_id != ['']:
            for tag_id in tags_id:
                tag = Tag.query.filter_by(id=int(tag_id)).first()
                if not tag in post.tags:
                    post.tags.append(tag)
            for tag in post.tags:
                if not str(tag.id) in tags_id:
                    post.tags.remove(tag)
        if 'update_date' in request.form:
            post.date = datetime.now()
        db.session.commit()
        flash('发布成功')
        return redirect(url_for('auth.index'))
    # 放在表单验证后面，否则旧数据将覆盖表单新数据
    form.title.data = post.title
    form.content_md.data = post.content_md
    form.category.data = post.category_id
    return render_template('admin/editpost.html',form=form,tags=tags,attachments=attachments,post=post)

# 后台写笔记页
@auth.route('/writenote',methods=['GET','POST'])
@login_required
def writenote():
    form = PostForm()
    if len(Note.query.all()) == 0:
        newnote_id = 1
    else:
        newnote_id = Note.query.order_by(Note.id.desc()).first().id + 1
    tags = Tag.query.all()
    if form.validate_on_submit():
        tags_id = form.tags.data.split(',')
        content_md = form.content_md.data
        content_html = md2html(content_md)
        note = Note(id=newnote_id,title=form.title.data,content_html=content_html,content_md=content_md,
                    category_id=form.category.data,date=datetime.now())
        if tags_id != ['']:
            for tag_id in tags_id:
                tag = Tag.query.filter_by(id=tag_id).first()
                note.tags.append(tag)
        db.session.add(note)
        db.session.commit()
        flash('发布成功')
        return redirect(url_for('auth.index'))
    return render_template('admin/writenote.html',form=form,tags=tags,newnote_id=newnote_id)

# 后台修改笔记页
@auth.route('/editnote/<int:note_id>',methods=['GET','POST'])
@login_required
def editnote(note_id):
    form = PostForm()
    note = Note.query.get_or_404(note_id)
    attachments = Attachment.query.filter_by(note_id=note_id).all()
    tags = Tag.query.all()
    if form.validate_on_submit():
        tags_id = form.tags.data.split(',')

        note.title = form.title.data
        note.content_md = form.content_md.data
        note.content_html = md2html(form.content_md.data)
        note.category_id = form.category.data

        if tags_id != ['']:
            for tag_id in tags_id:
                tag = Tag.query.filter_by(id=int(tag_id)).first()
                if not tag in note.tags:
                    note.tags.append(tag)
            for tag in note.tags:
                if not str(tag.id) in tags_id:
                    note.tags.remove(tag)
        db.session.commit()
        flash('发布成功')
        return redirect(url_for('auth.index'))
    # 放在表单验证后面，否则旧数据将覆盖表单新数据
    form.title.data = note.title
    form.content_md.data = note.content_md
    form.category.data = note.category_id
    return render_template('admin/editnote.html',form=form,tags=tags,attachments=attachments,note=note)

# 后台管理文章页
@auth.route('/posts')
@login_required
def posts():
    return render_template('admin/posts.html')

# 后台管理笔记页
@auth.route('/notes')
@login_required
def notes():
    return render_template('admin/notes.html')

# 后台管理分类页
@auth.route('/categorys')
@login_required
def categorys():
    return render_template('admin/categorys.html')

# 后台管理标签页
@auth.route('/tags')
@login_required
def tags():
    return render_template('admin/tags.html')

# 后台管理评论页
@auth.route('/comments')
@login_required
def comments():
    return render_template('admin/comments.html')

# 后台管理留言页
@auth.route('/messages')
@login_required
def messages():
    return render_template('admin/messages.html')


#---------------------------------------------- api ------------------------------------------------#
# 处理附件上传
@auth.route('/api/upload_avata',methods=['GET','POST'])
@login_required
def upload_avata():
    filename = 'avata.jpg'
    basepath = os.path.join(os.path.abspath(os.path.dirname(__file__))[0:-4], 'static/img')
    avatapath = os.path.join(basepath, filename)
    request.files['file'].save(avatapath)
    result = {'status': 0}
    return jsonify(result)

# 处理附件上传
@auth.route('/api/upload',methods=['GET','POST'])
@login_required
def upload():
    # 附件所属文章或笔记的id
    id = int(request.form['id'])
    code = int(request.form['code'])
    # 处理文件大小
    filesize = int(request.headers['content-length']) / 1024
    if filesize < 1024:
        filesize = format(filesize,'.2f') + 'Kb'
    elif filesize > 1024 and filesize < 1024 * 1024:
        filesize = format(filesize,'.2f') + 'Mb'
    # 处理文件名
    origin = str(request.files['file']).split(' ')[1].split("'")[1]
    filename = str(request.files['file']).split(' ')[1].split("'")[1].split('.')[0]
    fileext = str(request.files['file']).split(' ')[1].split("'")[1].split('.')[1]
    # 文件更名并存储
    file = filename + datetime.now().strftime("%Y%m%d%H%M%S") + '.' + fileext
    basepath = os.path.join(os.path.abspath(os.path.dirname(__file__))[0:-4], 'static/uploads')
    current_year = datetime.now().strftime('%Y')
    current_year_path = os.path.join(basepath, current_year)
    print(current_year_path)
    current_month = datetime.now().strftime('%m')
    current_month_path = os.path.join(current_year_path, current_month)
    print(current_month_path)
    if os.path.exists(current_year_path):
        if os.path.exists(current_month_path):
            print('存在' + current_month + '文件夹')
        else:
            os.mkdir(current_month_path)
            print('创建' + current_month + '文件夹')
    else:
        os.makedirs(current_month_path)
        print('创建' + current_month_path + '文件夹')
    # 一经部署，图片存储后的本地路径就固定了，迁移博客时需要确保博客根目录新存放路径与原路径一致，否则旧图片将无法正常删除，虽然新图片不受影响
    local = os.path.join(current_month_path, file)
    request.files['file'].save(local)
    # 文件url
    # url = current_app.config['FLASKY_HOST'] + url_for('static',filename='uploads/' + current_year + '/' + current_month + '/' + file)
    # 采用相对路径
    url = '/' + current_year + '/' + current_month + '/' + file
    # 数据库操作
    if code == 0:
        attachment = Attachment(filename=origin,securename=file,filesize=filesize,
                                date=datetime.now(),local=local,url=url,post_id=id)
    else:
        attachment = Attachment(filename=origin, securename=file, filesize=filesize,
                                date=datetime.now(), local=local, url=url, note_id=id)
    db.session.add(attachment)
    db.session.commit()
    # 返回结果
    result = {
        "code": 0,
        "msg": "",
        "data": {
            "filename": origin,
            "securename": file,
            "size": filesize,
            "src": url
        }
    }
    return jsonify(result)

# 处理删除附件
@auth.route('/api/remove_file',methods=['GET','POST'])
@login_required
def remove_file():
    securename = request.form['securename']
    attachment = Attachment.query.filter_by(securename=securename).first()
    if attachment:
        db.session.delete(attachment)
        db.session.commit()
        try:
            os.remove(attachment.local)
        except:
            pass
        result = {'status': 0}
    else:
        result = {'status': 1}
    return jsonify(result)

# 保存文章草稿
@auth.route('/api/save_draft',methods=['GET','POST'])
@login_required
def save_draft_api():
    code = int(request.form['code'])
    post_id = request.form['post_id']
    post_title = request.form['post_title']
    post_category = request.form['post_category']
    post_tag = request.form['post_tag']
    post_content = request.form['post_content']
    tags_id = post_tag.split(',')
    content_md = post_content
    content_html = md2html(content_md)
    if code == 0:
        post = Post(id=post_id,title=post_title,content_html=content_html,content_md=content_md,
                    category_id=post_category,date=datetime.now(),draft_flag=True)
        if tags_id != ['']:
            for tag_id in tags_id:
                tag = Tag.query.filter_by(id=tag_id).first()
                post.tags.append(tag)
        db.session.add(post)
        db.session.commit()
    else:
        post = Post.query.filter_by(id=post_id).first()
        post.title = post_title
        post.category_id = post_category
        post.content_md = content_md
        post.content_html = content_html
        post.draft_flag = True
        if tags_id != ['']:
            for tag_id in tags_id:
                tag = Tag.query.filter_by(id=int(tag_id)).first()
                if not tag in post.tags:
                    post.tags.append(tag)
            for tag in post.tags:
                if not str(tag.id) in tags_id:
                    post.tags.remove(tag)
    result = {"status": 0}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/postlist',methods=['GET','POST'])
@login_required
def postlist_api():
    posts = Post.query.order_by(Post.date.desc()).all()
    data = []
    i = 1
    for post in posts:
        author = User.query.first()
        status = '已发布'
        if post.draft_flag:
            status = '草稿'
        datarow = {"sno": i,"pid": post.id,"title": post.title,"author": author.nickname,
                   "category": post.category.name,"date": post.date.strftime("%Y-%m-%d %H:%M:%S"),"status": status}
        data.append(datarow)
        i = i + 1
    result = {"code": 0,"msg": "","count": len(posts),"data": data}
    return jsonify(result)

# 数据表格内嵌按钮调用api，搜索文章
@auth.route('/api/admin_search_post',methods=['GET','POST'])
@login_required
def admin_search_post_api():
    key = request.form['key']
    posts = Post.query.filter(or_(Post.title.like('%' + key + '%'),Post.content_md.like('%' + key + '%'))) \
            .order_by(Post.date.desc()).all()
    i = 1
    data = []
    for post in posts:
        author = User.query.first()
        status = '已发布'
        if post.draft_flag:
            status = '草稿'
        datarow = {"sno": i,"pid": post.id,"title": post.title,"author": author.nickname,
                   "category": post.category.name,"date": post.date.strftime("%Y-%m-%d %H:%M:%S"),"status": status}
        data.append(datarow)
        i = i + 1
    result = {"code": 0,"msg": "","count": len(posts),"data": data}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/deletepost',methods=['GET','POST'])
@login_required
def deletepost_api():
    post_id = int(request.form['post_id'])
    post = Post.query.filter_by(id=post_id).first()
    if post:
        db.session.delete(post)
        db.session.commit()
        result = {"status": 0}
    else:
        result = {"status": 1}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/notelist',methods=['GET','POST'])
@login_required
def notelist_api():
    notes = Note.query.order_by(Note.date.desc()).all()
    data = []
    i = 1
    for note in notes:
        author = User.query.first()
        datarow = {"sno": i,"nid": note.id,"title": note.title,"author": author.nickname,
                   "category": note.category.name,"date": note.date.strftime("%Y-%m-%d %H:%M:%S")}
        data.append(datarow)
        i = i + 1
    result = {"code": 0,"msg": "","count": len(notes),"data": data}
    return jsonify(result)

# 数据表格内嵌按钮调用api，搜索笔记
@auth.route('/api/admin_search_note',methods=['GET','POST'])
@login_required
def admin_search_note_api():
    key = request.form['key']
    notes = Note.query.filter(or_(Note.title.like('%' + key + '%'),Note.content_md.like('%' + key + '%'))) \
            .order_by(Note.date.desc()).all()
    i = 1
    data = []
    for note in notes:
        author = User.query.first()
        datarow = {"sno": i,"nid": note.id,"title": note.title,"author": author.nickname,
                   "category": note.category.name,"date": note.date.strftime("%Y-%m-%d %H:%M:%S")}
        data.append(datarow)
        i = i + 1
    result = {"code": 0,"msg": "","count": len(notes),"data": data}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/deletenote',methods=['GET','POST'])
@login_required
def deletenote_api():
    note_id = int(request.form['note_id'])
    note = Note.query.filter_by(id=note_id).first()
    if note:
        db.session.delete(note)
        db.session.commit()
        result = {"status": 0}
    else:
        result = {"status": 1}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/categorylist',methods=['GET','POST'])
@login_required
def categorylist_api():
    categorys = Category.query.order_by(Category.date.desc()).all()
    data = []
    i = 1
    for category in categorys:
        datarow = {"sno": i,"cid": category.id,"name": category.name,"date": category.date.strftime("%Y-%m-%d")}
        data.append(datarow)
        i = i + 1
    result = {"code": 0,"msg": "","count": len(categorys),"data": data}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/newcategory',methods=['GET','POST'])
@login_required
def newcategory_api():
    category_name = request.form['category_name']
    if len(Category.query.filter_by(name=category_name).all()):
        result = {"status": 1}
    else:
        category = Category(name=category_name,date=datetime.now())
        db.session.add(category)
        db.session.commit()
        result = {"status": 0}
    return jsonify(result)

# 数据表格内嵌按钮调用api
# 获取当前编辑分类的原始名称
@auth.route('/api/editcategory',methods=['GET','POST'])
@login_required
def editcategory_api():
    category_id = int(request.form['category_id'])
    category = Category.query.filter_by(id=category_id).first()
    if category:
        result = {"name": category.name,"status": 0}
    else:
        result = {"name": "","status": 1}
    return jsonify(result)

# 数据表格内嵌按钮调用api
# 真正完成分类修改
@auth.route('/api/editcategory2',methods=['GET','POST'])
@login_required
def editcategory_api2():
    category_id = int(request.form['category_id'])
    if category_id == 1:
        result = {"status": 2}
        return jsonify(result)
    category_name = request.form['category_name']
    category = Category.query.filter_by(id=category_id).first()
    if category:
        category.name = category_name
        db.session.commit()
        result = {"status": 0}
    else:
        result = {"status": 1}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/deletecategory',methods=['GET','POST'])
@login_required
def deletecategory_api():
    category_id = int(request.form['category_id'])
    # 默认分类不可删除
    if category_id == 1:
        result = {"status": 2}
        return jsonify(result)
    category = Category.query.filter_by(id=category_id).first()
    if category:
        # 该分类下的所有文章归至默认分类
        for post in category.posts:
            post.category_id = 1
        db.session.commit()
        db.session.delete(category)
        db.session.commit()
        result = {"status": 0}
    else:
        result = {"status": 1}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/taglist',methods=['GET','POST'])
@login_required
def taglist_api():
    tags = Tag.query.order_by(Tag.date.desc()).all()
    data = []
    i = 1
    for tag in tags:
        datarow = {"sno": i,"tid": tag.id,"name": tag.name,"date": tag.date.strftime("%Y-%m-%d")}
        data.append(datarow)
        i = i + 1
    result = {"code": 0,"msg": "","count": len(tags),"data": data}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/newtag',methods=['GET','POST'])
@login_required
def newtag_api():
    tag_name = request.form['tag_name']
    if len(Tag.query.filter_by(name=tag_name).all()):
        result = {"status": 1}
    else:
        tag = Tag(name=tag_name,color=colortable[random.randint(0,len(colortable)-1)],date=datetime.now())
        db.session.add(tag)
        db.session.commit()
        result = {"status": 0,"id": tag.id,"name": tag.name,"color": tag.color}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/edittag',methods=['GET','POST'])
@login_required
def edittag_api():
    tag_id = int(request.form['tag_id'])
    tag = Tag.query.filter_by(id=tag_id).first()
    if tag:
        result = {"name": tag.name,"status": 0}
    else:
        result = {"name": "","status": 1}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/edittag2',methods=['GET','POST'])
@login_required
def edittag_api2():
    tag_id = int(request.form['tag_id'])
    tag_name = request.form['tag_name']
    tag = Tag.query.filter_by(id=tag_id).first()
    if tag:
        tag.name = tag_name
        db.session.commit()
        result = {"status": 0}
    else:
        result = {"status": 1}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/deletetag',methods=['GET','POST'])
@login_required
def deletetag_api():
    tag_id = int(request.form['tag_id'])
    tag = Tag.query.filter_by(id=tag_id).first()
    if tag:
        db.session.delete(tag)
        db.session.commit()
        result = {"status": 0}
    else:
        result = {"status": 1}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/commentlist',methods=['GET','POST'])
@login_required
def commentlist_api():
    comments = Comment.query.order_by(Comment.date.desc()).all()
    data = []
    i = 1
    for comment in comments:
        datarow = {"sno": i,"cid": comment.id,"author": comment.author,
                   "content": comment.content,"title": comment.post.title,
                   "email": comment.email,"date": comment.date.strftime(("%Y-%m-%d %H:%M:%S"))}
        data.append(datarow)
        i = i + 1
    result = {"code": 0,"msg": "","count": len(comments),"data": data}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/deletecomment',methods=['GET','POST'])
@login_required
def deletecomment_api():
    comment_id = int(request.form['comment_id'])
    comment = Comment.query.filter_by(id=comment_id).first()
    if comment:
        db.session.delete(comment)
        db.session.commit()
        result = {"status": 0}
    else:
        result = {"status": 1}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/messagelist',methods=['GET','POST'])
@login_required
def messagelist_api():
    messages = Message.query.order_by(Message.date.desc()).all()
    data = []
    i = 1
    for message in messages:
        datarow = {"sno": i,"mid": message.id,"author": message.author,
                   "content": message.content,"email": message.email,
                   "date": message.date.strftime("%Y-%m-%d %H:%M:%S")}
        data.append(datarow)
        i = i + 1
    result = {"code": 0,"msg": "","count": len(messages),"data": data}
    return jsonify(result)

# 数据表格内嵌按钮调用api
@auth.route('/api/deletemessage',methods=['GET','POST'])
@login_required
def deletemessage_api():
    message_id = int(request.form['message_id'])
    message = Message.query.filter_by(id=message_id).first()
    if message:
        db.session.delete(message)
        db.session.commit()
        result = {"status": 0}
    else:
        result = {"status": 1}
    return jsonify(result)
