"""Python module implementing a wrapper over the requests.Session class.

Copyrights (c) Nutanix Inc. 2015

Author: bgangadharan@nutanix.com
"""
#pylint: disable=invalid-name,unused-variable,broad-except,import-error,no-name-in-module
#pylint: disable=too-many-branches

import json
import time
import requests

from requests import Session
from requests.exceptions import ConnectionError, ReadTimeout
try:
  from requests.packages.urllib3 import disable_warnings
  disable_warnings()
except Exception: # pragma: no cover
  pass



class HTTP(object):
  """This class implements a simple wrapper over the requests session.
  This class adds functionalities like retries and timeouts for the operations.
  """

  NO_RETRY_HTTP_CODES = [400, 404, 500, 502]

  def __init__(self, **kwargs):
    """Default constructor.
    Args:
      kwargs(dict): Accepts following arguments:
        timeout(optional, int): Max seconds to wait before HTTP connection
        times-out. Default 30 seconds.
        retries (optional, int): Maximum number of retires. Default: 5.
        retry_interval (optional, int): Time to sleep between retry intervals.
         Default: 5 seconds.

    Returns:
      None.
    """
    self._session = Session()
    self._timeout = kwargs.get('timeout', 30)
    self._retries = kwargs.get('retries', 5)
    self._retry_interval = kwargs.get('retry_interval', 30)

  def delete(self, url, **kwargs):
    """This is a wrapper method over the delete method.

    Args:
      url (str): The URL to for the Request
      kwargs (dict): Keyword args to be passed to the requests call.

    Returns:
      (response): The response object
    """
    return self._send('delete', url, **kwargs)

  def get(self, url, **kwargs):
    """This is a wrapper method over the get method.

    Args:
      url (str): The URL to for the Request
      kwargs (dict): Keyword args to be passed to the requests call.

    Returns:
      (response): The response object
    """
    return self._send('get', url, **kwargs)

  def head(self, url, **kwargs):
    """This is a wrapper method over the head method.

    Args:
      url (str): The URL to for the Request
      kwargs (dict): Keyword args to be passed to the requests call.

    Returns:
      (response): The response object
    """
    return self._send('head', url, **kwargs)

  def post(self, url, **kwargs):
    """This is a wrapper method over the post method.

    Args:
      url (str): The URL to for the Request
      kwargs (dict): Keyword args to be passed to the requests call.

    Returns:
      (response): The response object
    """
    return self._send('post', url, **kwargs)

  def put(self, url, **kwargs):
    """This is a wrapper method over the put method.

    Args:
      url (str): The URL to for the Request
      kwargs (dict): Keyword args to be passed to the requests call.

    Returns:
      (response): The response object
    """
    return self._send('put', url, **kwargs)

  def _send(self, method, url, **kwargs):
    """This private method acting as proxy for all http methods.

    Args:
      method (str): The http method type.
      url (str): The URL to for the Request
      kwargs (dict): Keyword args to be passed to the requests call.
        retries (int): The retry count in case of HTTP errors.
                       Except the codes in the list NO_RETRY_HTTP_CODES.

    Returns:
      (response): The response object

    Raises:
      NuTestHTTPError, NuTestInterfaceTransportError
    """
    debug = kwargs.get('debug', True)
    kwargs['verify'] = kwargs.get('verify', False)
    if 'debug' in kwargs:
      del kwargs['debug']
    if 'timeout' not in kwargs:
      kwargs['timeout'] = self._timeout
    if 'json' in kwargs:
      kwargs['data'] = json.dumps(kwargs['json'])
      content_dict = {'content-type': 'application/json'}
      kwargs.setdefault('headers', {})
      kwargs['headers'].update(content_dict)
      del kwargs['json']
    func = getattr(self._session, method)
    response = None

    retries = kwargs.pop("retries", None)
    retry_interval = kwargs.pop("retry_interval", self._retry_interval)
    retry_count = retries if retries else self._retries
    for ii in range(retry_count):
      if debug:
        print(">>%s %s : %s" % (method.upper(), url, kwargs))
      try:
        response = func(url, **kwargs)
        if kwargs.get('params'):
          print("The request url sent: %s" %response.request.url)

      except (ConnectionError, ReadTimeout) as e:
        print("Request failed with error: %s" % e)
        if ii != retry_count - 1:
          time.sleep(retry_interval)
        continue
      finally:
        # This is not a complete session close. It actually clears all cached
        # connections, that are currently not in use. It will NOT affect
        # connections that are in use. It takes care of threaded execution too.
        self._session.close()
      if debug:
        print("<<%s:%s" % (response.status_code, response.text))
      if response.ok:
        return response
      if response.status_code in [401, 403]:
        raise Exception('HTTP Auth Failed %s %s' % (method, url),
                              response=response)
      elif response.status_code == 409:
        raise Exception('HTTP conflict with the current state of the '
                              'target resource %s %s' % (method, url),
                              response=response)
      elif response.status_code in self.NO_RETRY_HTTP_CODES:
        break
      if ii != retry_count - 1:
        time.sleep(retry_interval)

    if response is not None:
      msg = 'HTTP %s %s failed. Response: %s' % (method, url, response)
      if hasattr(response, "text") and response.text:
        msg = "\n".join([msg, response.text]).encode('utf-8')
      raise Exception("exception")
    else:
      raise Exception("Failed to make the HTTP request %s "
                                          "%s" % (method, url))
