# app/serializers.py
import json
from django.core.serializers.json import Serializer as JSONSerializer
from django.core.serializers.python import Deserializer as PythonDeserializer
from django.contrib.contenttypes.fields import GenericForeignKey

class Serializer(JSONSerializer):
    def get_dump_object(self, obj):
        dumped_object = super().get_dump_object(obj)
        
        # Inspect model fields to identify any GenericForeignKey relations
        for field in obj._meta.get_fields(include_hidden=True):
            if isinstance(field, GenericForeignKey):
                content_object = getattr(obj, field.name)
                
                # If the linked object exists and implements natural keys, export it
                if content_object and hasattr(content_object, 'natural_key'):
                    # Remove the database-specific numeric ID from the output
                    dumped_object['fields'].pop(field.fk_field, None)
                    # Inject our custom virtual field containing the two-string natural key tuple
                    dumped_object['fields'][f"{field.name}_natural_key"] = content_object.natural_key()
                    
        return dumped_object


def Deserializer(stream_or_string, **options):
    """
    Custom Deserializer assigned strictly to the .json_gfk extension.
    It intercepts and scrubs the virtual fields from the parsed python list 
    before feeding them into Django's native schema mapping engine.
    """
    # 1. Convert the file stream into raw Python dictionaries
    if not isinstance(stream_or_string, (bytes, str)):
        stream_or_string = stream_or_string.read()
    if isinstance(stream_or_string, bytes):
        stream_or_string = stream_or_string.decode()
        
    try:
        raw_data = json.loads(stream_or_string)
    except Exception as exc:
        from django.core.serializers.base import DeserializationError
        raise DeserializationError() from exc

    # Dictionary to keep track of the scrubbed keys
    saved_natural_keys = {}

    # 2. Preprocess: completely drop the virtual key to evade strict validation
    for index, item in enumerate(raw_data):
        fields = item.get('fields', {})
        nat_keys = {k: v for k, v in fields.items() if k.endswith('_natural_key')}
        
        if nat_keys:
            saved_natural_keys[index] = nat_keys
            # Evade FieldDoesNotExist by cleaning the input dictionary
            for k in nat_keys.keys():
                fields.pop(k, None)

    # 3. Hand over the completely clean dictionary list to Django's standard builder
    python_objects = PythonDeserializer(raw_data, **options)
    
    # 4. Loop through valid instances and bind keys using target natural keys
    for index, obj in enumerate(python_objects):
        if index in saved_natural_keys:
            model_fields = obj.object._meta
            
            for field in model_fields.get_fields(include_hidden=True):
                if isinstance(field, GenericForeignKey):
                    fk_nat_key_name = f"{field.name}_natural_key"
                    natural_key_value = saved_natural_keys[index].get(fk_nat_key_name)
                    
                    if natural_key_value:
                        # Extract the dynamic ContentType from the record
                        ct = obj.object.content_type
                        if ct:
                            target_model = ct.model_class()
                            # Fetch the primary key on the target environment using the natural key
                            target_obj = target_model.objects.get_by_natural_key(*natural_key_value)
                            
                            # Bind the dynamic target primary key into the model's integer field
                            setattr(obj.object, field.fk_field, target_obj.pk)
                        
        yield obj

