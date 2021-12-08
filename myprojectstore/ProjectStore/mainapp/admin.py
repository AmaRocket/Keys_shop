from django.forms import ModelChoiceField
from django.contrib import admin

from .models import *

""" For right descriptions of category, without conflicts with fields
    Чтобы мы не вписали поля описания одной модели в другую
    VPN в Design etc
"""


class BackUpStorageAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='backupstorage'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class DesignAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='design'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(BackUpStorage, BackUpStorageAdmin)
admin.site.register(Design, DesignAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
