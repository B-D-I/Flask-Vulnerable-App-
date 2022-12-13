from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, Form, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_wtf.recaptcha import RecaptchaField
from creds import site_key2, secret_key2
import safe


class CaptchaForm(Form):
    captcha = RecaptchaField(public_key=site_key2, private_key=secret_key2, secure=True)


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=25, message='name too long')])
    email = StringField("Email", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired(), Length(max=25, message='username too long')])
    role = StringField("Role", validators=[Length(max=25, message='role type too long')])
    password_hash = PasswordField("Password", validators=[DataRequired(),
                                                          Length(min=9, max=35, message='password must be greater than'
                                                                 '9 characters'),
                                                          EqualTo('password_hash2', message='passwords must match')
                                                          ])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate_password_hash(self, password_hash):
        if not bool(safe.check(password_hash.data)):
            print('password insecure')
            raise ValidationError('password not strong enough: include upper and lowercase, '
                                  'special characters and numbers!!')



class NamerForm(FlaskForm):
    name = StringField("Enter Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Submit")