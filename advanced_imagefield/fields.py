# -*- coding:utf-8 -*-
from django.db import models
from django import forms
from django.forms.widgets import ClearableFileInput
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
import pytils


DEF_UPLOAD_SIZE_IMAGE = 3*1024*1024

class AdvancedThumbImageWidget(ClearableFileInput):
    template_with_initial = u'%(initial_text)s: %(initial)s %(clear_template)s<br /><p>%(input_text)s: %(input)s</p>'
    template_with_clear = u'<p>%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label></p>'

    def __init__(self, *args, **kwargs):
        super(AdvancedThumbImageWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        ret = super(AdvancedThumbImageWidget, self).render(name,value,attrs)
        if value:
            try:
                ret = u'%s <p><img src="%s" style="height: 60px;"></p>' % (ret, value.url)
            except Exception, e:
                pass
        return mark_safe(ret)

class AdvancedImageFieldForm(forms.FileField):
    def __init__(self, *args, **kwargs):
        self.max_length = kwargs.pop('max_length', None)
        kwargs['widget'] = AdvancedThumbImageWidget
        super(AdvancedImageFieldForm, self).__init__(*args, **kwargs)


class AdvancedImageField(models.ImageField):
    def __init__(self, *args, **kwargs):
        if kwargs.get('max_upload_size'):
            self.max_upload_size = kwargs.pop("max_upload_size")
        else:
            self.max_upload_size = DEF_UPLOAD_SIZE_IMAGE
        super(AdvancedImageField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(AdvancedImageField, self).clean(*args, **kwargs)
        sz = getattr(data.instance, self.name).size
        if sz > self.max_upload_size:
            raise forms.ValidationError(_('Please keep filesize under %(under)s. Current filesize %(current)s') % {"under":filesizeformat(self.max_upload_size), "current":filesizeformat(sz)})
        return data

    def pre_save(self, model_instance, add):
        #нужно перевести в нижний регистр и убрать кириллицу
        if add:
            pass
        file_name = getattr(model_instance, self.attname).name
        if file_name:
            file_name = file_name.lower()
            file_name = pytils.translit.translify(file_name)
            getattr(model_instance, self.attname).name = file_name

        file = super(AdvancedImageField, self).pre_save(model_instance, add)
        return file

    def formfield(self, **kwargs):
        defaults = {'form_class': AdvancedImageFieldForm}
        defaults.update(kwargs)
        return super(AdvancedImageField, self).formfield(**defaults)


'''

END CmsImageField

'''
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^advanced_imagefield\.fields\.AdvancedImageField"])
except:
    pass