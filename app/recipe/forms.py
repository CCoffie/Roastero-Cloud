from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp, DataRequired
from wtforms import ValidationError
from ..models import Role, User, Recipe, Permission
from wtforms.ext.sqlalchemy.orm import model_form
from flask_wtf.file import FileField
from .. import db


AddRecipeFormBase = model_form(model=Recipe,
                        base_class=Form,
                        db_session=db.session,
                        exclude=["recipe", "bean"])
class AddRecipeForm(AddRecipeFormBase):
    recipe = FileField("Upload you recipe", validators=[DataRequired()])
    bean = StringField("Bean Name", [Required()])
    submit = SubmitField("Submit")
