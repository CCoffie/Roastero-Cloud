from flask import Blueprint

recipe = Blueprint('recipes', __name__)

from . import views
from . import forms
from ..models import Permission
