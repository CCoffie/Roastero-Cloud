from flask import abort
from flask.ext.admin import BaseView, expose
from .. import admin
from wtforms.fields import SelectField, PasswordField
from flask.ext.login import current_user
from ..models import Permission, User, Recipe
from flask.ext.admin.contrib.sqla import ModelView
from .. import db
import inspect
from pprint import pprint

class UserView(ModelView):
    column_list = ('username', 'email', 'member_since', 'last_seen', 'role')
    form_excluded_columns = ('password_hash','avatar_hash')
    column_searchable_list = ('username', 'name', 'email')

    def __init__(self, session):
        # You can pass name and other parameters if you want to
        super(UserView, self).__init__(User, session, name="Users")


    def is_accessible(self):
        if current_user.can(Permission.ADMINISTER):
            return True

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('auth.login'))



class RecipeView(ModelView):

    def __init__(self, session):
        # Just call parent class with predefined model.
        super(RecipeView, self).__init__(Recipe, session, name="Recipes")

    def is_accessible(self):
        if current_user.can(Permission.ADMINISTER):
            return True

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('auth.login'))

#pprint(inspect.getmembers(UserView(db.session, name="Users")))

admin.add_view(UserView(db.session))
admin.add_view(RecipeView(db.session))
