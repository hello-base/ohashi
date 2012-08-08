import psycopg2.extras
import uuid

from django import forms
from django.core import exceptions
from django.db import models, router
from django.db.models import DateTimeField, Field, ForeignKey
from django.utils import timezone

from south.modelsinspector import add_introspection_rules


class CharField(Field):
    def formfield(self, **kwargs):
        defaults = {'widget': forms.TextInput}
        defaults.update(kwargs)
        return super(CharField, self).formfield(**defaults)

    def db_type(self, connection):
        if self.max_length:
            return 'varchar(%s)' % self.max_length
        return 'text'


class EmailField(CharField):
    def formfield(self, **kwargs):
        defaults = {'form_class': forms.EmailField}
        defaults.update(kwargs)
        return super(EmailField, self).formfield(**defaults)


class SlugField(CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('db_index', True)
        super(SlugField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.SlugField}
        defaults.update(kwargs)
        return super(SlugField, self).formfield(**defaults)


class URLField(CharField):
    def __init__(self, verbose_name=None, name=None, verify_exists=True, **kwargs):
        self.verify_exists = verify_exists
        super(URLField, self).__init__(verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.URLField, 'verify_exists': self.verify_exists}
        defaults.update(kwargs)
        return super(URLField, self).formfield(**defaults)


class CustomManagerForeignKey(ForeignKey):
    """
    Inspired by:
    <http://www.hoboes.com/Mimsy/hacks/custom-managers-django-foreignkeys/>

    """
    def __init__(self, *args, **kwargs):
        if 'manager' in kwargs:
            self.custom_manager = kwargs['manager']()
            del kwargs['manager']
        else:
            self.custom_manager = None
        super(CustomManagerForeignKey, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        field = super(CustomManagerForeignKey, self).formfield(**kwargs)
        if self.custom_manager:
            field.queryset = self.custom_manager
        return field

    def validate(self, value, model_instance):
        if self.rel.parent_link:
            return
        super(models.ForeignKey, self).validate(value, model_instance)
        if value is None:
            return
        if self.custom_manager:
            manager = self.custom_manager
        else:
            using = router.db_for_read(model_instance.__class__, instance=model_instance)
            manager = self.rel.to._default_manager.using(using)
        qs = manager.filter(**{self.rel.field_name: value})
        qs = qs.complex_filter(self.rel.limit_choices_to)
        if not qs.exists():
            raise exceptions.ValidationError(
                self.error_messages['invalid'] % {
                    'model': self.rel.to._meta.verbose_name,
                    'pk': value
                }
            )


# Register this adapter so we can use UUID objects.
psycopg2.extras.register_uuid()


class UUIDField(CharField):
    """
    A field which stores a UUID value in hex format. This may also have the
    Boolean attribute 'auto' which will set the value on initial save to a new
    UUID value (calculated using the UUID4 method).

    """
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', uuid.uuid4)
        kwargs.setdefault('editable', not kwargs.get('primary_key', False))
        super(UUIDField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'uuid'

    def get_db_prep_value(self, value, connection, prepared=False):
        return self.to_python(value)

    def to_python(self, value):
        if not value:
            return None
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value


# South custom field introspection rules.
add_introspection_rules([], [r'^ohashi\.db\.fields\.CustomManagerForeignKey'])
add_introspection_rules([([UUIDField], [], {'auto': ['auto', {'default': 'False'}]},)], [r'^ohashi\.db\.fields\.UUIDField'])
