from django.contrib import admin
from . import models


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)


@admin.register(models.File)
class FileAdmin(admin.ModelAdmin):
    pass




#list_filter = ('visible', 'country')
#list_editable = ('visible',)
#search_fields = ['city']

