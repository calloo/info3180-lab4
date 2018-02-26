from flask_wtf import FlaskForm
from app import app
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf.file import FileField, FileAllowed, FileRequired


class UploadForm(FlaskForm):
    photo = FileField('photo', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images Only!')])
