# -*— coding:utf-8 -*—
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, TextAreaField
from wtforms.validators import DataRequired,Length
from app.models import Category


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')


class SettingForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(),Length(max=64)])
    subtitle = StringField('副标题', validators=[Length(max=64)])
    nickname = StringField('昵称', validators=[DataRequired(), Length(max=64)])
    about = TextAreaField('关于',validators=[DataRequired()])
    old_password = PasswordField('原密码')
    new_password = PasswordField('新密码')
    submit = SubmitField('修改')


class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(max=256)])
    content_md = TextAreaField('正文', validators=[DataRequired()])
    category = SelectField('分类', coerce=int)
    tags = StringField('标签')
    submit = SubmitField('发布内容')

    def __init__(self):
        super(PostForm, self).__init__()
        self.category.choices = [(c.id, c.name) for c in Category.query.order_by('id')]



