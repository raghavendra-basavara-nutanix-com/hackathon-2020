"""Exceptions related to processors"""


class ResourceNotFoundException(Exception):
    """Exception for resource not found scenario"""

    def __init__(self, resource_type, resource_uuid, *args, **kwargs):
        self.resource_type = resource_type
        self.resource_uuid = resource_uuid
        super(ResourceNotFoundException, self).__init__(*args, **kwargs)

    def __str__(self):
        """Overrides __str__ to allow custom message addition"""
        custom_message = "{0} with UUID: {1} does not exists!".format(
            self.resource_type, self.resource_uuid
        )
        return "{0} {1}".format(
            custom_message,
            super(ResourceNotFoundException, self).__str__()
        )

class ResourceConflictException(Exception):
    """Exception for resource not found scenario"""

    def __init__(self, *args, **kwargs):
        super(ResourceConflictException, self).__init__(*args, **kwargs)

    def __str__(self):
        """Overrides __str__ to allow custom message addition"""
        custom_message = "Conflicting Resource Found"
        return "{0} {1}".format(
            custom_message,
            super(ResourceConflictException, self).__str__()
        )
