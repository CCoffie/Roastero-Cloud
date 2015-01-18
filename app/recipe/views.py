from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from ..models import Recipe
from . import recipe
from ..models import Permission
from ..decorators import permission_required
from .forms import AddRecipeForm
from .. import db


@permission_required(Permission.POST_RECIPES)
@recipe.route('/add', methods=['GET', 'POST'])
def add_recipe():
    form = AddRecipeForm()
    if form.validate_on_submit():
        print(type(request.form['recipe']))
        newRecipe = Recipe()
        db.session.add(newRecipe)
        db.session.commit()
    return render_template('recipe/add.html', form=form)
