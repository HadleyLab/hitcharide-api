from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class GetOrCreateMixin(serializers.ModelSerializer):
    default_error_messages = {
        'not_existing_item': _('Item does not exists'),
    }

    def get_fields(self):
        fields = super(GetOrCreateMixin, self).get_fields()

        pk_field = fields[
            'pk' if 'pk' in fields else self.Meta.model._meta.pk.attname]

        pk_field.allow_null = True
        pk_field.required = False

        return fields

    def to_internal_value(self, data):
        if isinstance(data, dict):
            pk = data.get('pk', None)

            if pk:
                # Don`t prepare and validate other fields for existing region
                return OrderedDict([('pk', pk), ])

        return super(GetOrCreateMixin, self).to_internal_value(data)

    def validate(self, attrs):
        attrs = super(GetOrCreateMixin, self).validate(attrs)

        pk = attrs.get('pk', None)
        if pk:
            if not self.Meta.model.objects.filter(pk=pk).exists():
                self.fail('not_existing_item')

        return attrs

    def create(self, validated_data):
        pk = validated_data.get('pk', None)

        if pk:
            # Select existing item
            return self.Meta.model.objects.get(pk=pk)

        return super(GetOrCreateMixin, self).create(validated_data)
