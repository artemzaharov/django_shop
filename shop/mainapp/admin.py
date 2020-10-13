from django.forms import ModelChoiceField, ModelForm
from django.contrib import admin
from .models import *


class SmartphoneAdminForm(ModelForm):
    # show grey sd_volume_max form if sd is false 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and not instance.sd:
            self.fields['sd_volume_max'].widget.attrs.update({
                'readonly': True, 'style': 'backgroud: lightgray'
            })

    def clean(self):
        if not self.cleaned_data['sd']:
            self.cleaned_data['sd_volume_max'] = None
        return self.cleaned_data

# if we create a notebook there must be no choice to change it to smartphone, so we need forms


class NotebookAdmin(admin.ModelAdmin):

    # we use this to show only one variant in admin panel(if we choose notebook it is notebook)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            # slug in this case is http://127.0.0.1:8000/admin/mainapp/notebook/
            return ModelChoiceField(Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(self, db_field, request, **kwargs)


class SmartphoneAdmin(admin.ModelAdmin):

    # for customization admin panel we use this
    change_form_template = 'admin.html'
    form = SmartphoneAdminForm

    # we use this to show only one variant in admin panel(if we choose smartphone it is smartphone)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            # slug in this case is http://127.0.0.1:8000/admin/mainapp/smartphones/
            return ModelChoiceField(Category.objects.filter(slug='smartphones'))
        return super().formfield_for_foreignkey(self, db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Notebook, NotebookAdmin)
admin.site.register(Smartphone, SmartphoneAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
