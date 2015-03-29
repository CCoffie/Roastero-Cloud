from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, json
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
    if form.validate_on_submit() and form.validate():
        file = request.files['recipe']
        print(type(file))
        if file is not None:
            recipeJSON = json.loads(file.stream.read().decode("utf-8").replace('\n', ''))
        print(request.form.name)
        #newRecipe = Recipe()
        #db.session.add(newRecipe)
        #db.session.commit()
    return render_template('recipe/add.html', form=form)


@recipe.route('/browse', methods=['GET'])
def browse_recipes():
    page = request.args.get('page', 1, type=int)
    pagination = Recipe.query.order_by(Recipe.id).paginate(
        page, per_page=current_app.config['RECIPES_PER_PAGE'],
        error_out=False)
    recipes = pagination.items
    return render_template('recipe/browse.html', recipes=recipes, pagination=pagination)
