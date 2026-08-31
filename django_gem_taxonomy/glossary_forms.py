from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from .models import Atom, Content

# Create a generic inline formset for the Note model.
# - extra=1: Displays one empty field to add a new note.
# - max_num=1: (Optional) Set this if you want to limit it to exactly one note per object.
ContentFormSet = generic_inlineformset_factory(Content, fields=('content',), extra=1, max_num=1, validate_max=True)
