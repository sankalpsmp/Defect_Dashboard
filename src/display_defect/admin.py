from django.contrib import admin

# Register your models here.
from .models import Main_table,Display_score
myModels = [Main_table,Display_score]
admin.site.register(myModels)