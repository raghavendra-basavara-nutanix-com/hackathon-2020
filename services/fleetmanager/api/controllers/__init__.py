"""
Copyright (c) 2019 Nutanix Inc. All rights reserved.
"""

from api.controllers.tenant import resolver as tenant_controller_resolver


def get_resolvers():
    """
    Returns API controller resolver
    :param config: Configurations for the controllers.
    :type config: object
    """
    resolvers = dict()
    tenant_resolvers = tenant_controller_resolver()
    resolvers.update(tenant_resolvers)

    return resolvers
