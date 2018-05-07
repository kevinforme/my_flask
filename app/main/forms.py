from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectField
from wtforms.validators import Length, DataRequired, Email

from app.models import Role, User


# 用户编辑资料的表单
class EditProfileForm(FlaskForm):
    username = StringField('你的名字', validators=[Length(0, 32)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')


# 管理员编辑用户资料的表单
class EditProfileAdminForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(0, 32), ])
    confirmed = BooleanField('激活状态')
    role = SelectField('用户权限', coerce=int)
    about_me = StringField('关于我')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValueError('邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValueError('用户名已被使用')


class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 64)])
    outline = StringField('概要', validators=[DataRequired(), Length(50, 180)])
    body = PageDownField('写下你想说的话', validators=[DataRequired()])
    submit = SubmitField('提交')


class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired(), Length(1, 128)])
    submit = SubmitField('提交')
