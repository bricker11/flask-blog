# -*— coding:utf-8 -*—
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    keyword = StringField('关键词', validators=[DataRequired()])
    submit  = SubmitField('搜索')



