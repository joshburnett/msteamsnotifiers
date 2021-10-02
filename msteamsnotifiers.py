from functools import wraps, partial
import sys
import platform
import socket
from pprint import pformat
import datetime
from typing import Optional

import pymsteams
import friendly_traceback
friendly_traceback.exclude_file_from_traceback(__file__)


__version__ = '0.1.0'
__version_info__ = tuple(int(i) if i.isdigit() else i for i in __version__.split('.'))


default_webhook_url = None

default_exception_template = """
*{timestamp}*  
Exception caught in **{funcname}()**, File **"{filename}"**  
**{message}**  
<br>
Node: {machine_name} ({ip_address})
<br>

```{where}```

args: {args}  
kwargs: {kwargs}

Full traceback:  
```{traceback}```
""".strip()

default_completion_template = """
*{timestamp}*  
Function completed: **{funcname}()** in file **"{filename}"**  
Node: {machine_name} ({ip_address})  
args: {args}  
kwargs: {kwargs}
""".strip()


DEBUG = False


#%%
def post_simple_teams_message(message: str, webhook_url: Optional[str] = None):
    """
    Post a simple, text-based message to an MS Teams channel via a webhook.  If webhook_url is unspecified,
    will use teamsnotifiers.default_webhook_url.
    """
    if webhook_url is None:
        if default_webhook_url is None:
            raise ValueError('Must provide a webhook URL, either as an argument or by setting '
                             'teamsnotifiers.default_webhook_url')
        webhook_url = default_webhook_url

    if DEBUG:
        print(f'Webhook URL: {webhook_url}')
        print('Message to be sent:')
        print('=' * 50)
        print(message)
        print('=' * 50)
        print('\n')
    else:
        msg = pymsteams.connectorcard(webhook_url)
        msg.text(message)
        msg.send()


#%%
def notify_exceptions(func: Optional[callable] = None, *, webhook_url: Optional[str] = None,
                      template: Optional[str] = None):
    """
    Decorator that catches exceptions in the decorated function and posts a message with the exception details
    to an MS Teams channel via a webhook.  If webhook_url is unspecified, will use
    teamsnotifiers.default_webhook_url.  If template is unspecified, will use teamsnotifiers.default_exception_template.
    """

    if func is None:
        return partial(notify_exceptions, webhook_url=webhook_url, template=template)

    @wraps(func)
    def wrapper_notify_exceptions(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except KeyboardInterrupt as e:
            print("Caught a KeyboardInterrupt, won't send the notification.")
            raise

        except Exception as e:
            if template is None:
                _template = default_exception_template
            else:
                _template = template

            error_type, value, tb = sys.exc_info()
            # output = {'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p'),
            #           'exception': e,
            #           'traceback': traceback.format_exc()}

            friendly_items = {}
            for item in ['message', 'where', 'friendly_tb']:
                friendly_traceback.set_include(item)
                friendly_traceback.explain_traceback('capture')
                friendly_items[item] = friendly_traceback.get_output()

            notifier_text = _template.format(funcname=func.__name__, filename=tb.tb_frame.f_code.co_filename,
                                             machine_name=platform.node(), message=friendly_items['message'].strip(),
                                             where=friendly_items['where'],
                                             ip_address=socket.gethostbyname(socket.gethostname()),
                                             args=f'{pformat(args, width=35)}',
                                             kwargs=f'{pformat(kwargs, width=35, sort_dicts=False)}',
                                             traceback=friendly_items['friendly_tb'],
                                             timestamp=datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p'))

            post_simple_teams_message(message=notifier_text, webhook_url=webhook_url)
            raise

    return wrapper_notify_exceptions


#%%
def notify_complete(func: Optional[callable] = None, *, webhook_url: Optional[str] = None,
                    template: Optional[str] = None):
    """
    Decorator that posts a message to an MS Teams channel via a webhook upon completion of the decorated function.
    If webhook_url is unspecified, will use teamsnotifiers.default_webhook_url.  If template is unspecified, will use
    teamsnotifiers.default_completion_template.
    """
    if func is None:
        return partial(notify_complete, webhook_url=webhook_url, template=template)

    @wraps(func)
    def wrapper_notify_complete(*args, **kwargs):
        if template is None:
            _template = default_completion_template
        else:
            _template = template

        result = func(*args, **kwargs)
        notifier_text = _template.format(funcname=func.__name__,
                                         filename=func.__globals__.get('__file__', 'Interactive session'),
                                         machine_name=platform.node(),
                                         ip_address=socket.gethostbyname(socket.gethostname()),
                                         args=f'{pformat(args, width=35)}',
                                         kwargs=f'{pformat(kwargs, width=35, sort_dicts=False)}',
                                         timestamp=datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p'))

        post_simple_teams_message(message=notifier_text, webhook_url=webhook_url)
        return result

    return wrapper_notify_complete
