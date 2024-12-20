"""
msteamsnotifiers: Decorators for automatically notifying an MS Teams channel of events
"""

from __future__ import annotations

from functools import wraps, partial
import sys
import platform
import socket
from pprint import pformat
import datetime

import requests
import friendly_traceback
friendly_traceback.exclude_file_from_traceback(__file__)


__version__ = '0.3.0'
__version_info__ = tuple(int(i) if i.isdigit() else i for i in __version__.split('.'))


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


adaptive_card_template = """
{{
  "type": "message",
  "attachments": [
    {{
      "contentType": "application/vnd.microsoft.card.adaptive",
      "contentUrl": null,
      "content": {{
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.2",
        "body": [
          {{
            "type": "TextBlock",
            "text": "{content}"
          }}
        ]
      }}
    }}
  ]
}}
""".strip()


##
class Notifier:
    DEBUG = False

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def post_simple_teams_message(self, message: str):
        """
        Post a simple, text-based message to an MS Teams channel via a webhook.
        """
        if self.DEBUG:
            print(f'Webhook URL: {self.webhook_url}')
            print('Message to be sent:')
            print('=' * 50)
            print(message)
            print('=' * 50)
            print('\n')
        else:
            data = adaptive_card_template.format(content=message)
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.webhook_url, data=data, headers=headers)
            return response

    def notify_exceptions(self, func: callable | None = None, *, template: str | None = None):
        """
        Decorator that catches exceptions in the decorated function and posts a message with the exception details
        to an MS Teams channel via a webhook.  If template is unspecified, will use
        msteamsnotifiers.default_exception_template.
        """

        if func is None:
            return partial(self.notify_exceptions, template=template)

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

                self.post_simple_teams_message(message=notifier_text)
                raise

        return wrapper_notify_exceptions

    def notify_complete(self, func: callable | None = None, *, template: str | None = None):
        """
        Decorator that posts a message to an MS Teams channel via a webhook upon completion of the decorated function.
        If webhook_url is unspecified, will use teamsnotifiers.default_webhook_url.  If template is unspecified, will use
        teamsnotifiers.default_completion_template.
        """
        if func is None:
            return partial(self.notify_complete, template=template)

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

            self.post_simple_teams_message(message=notifier_text)
            return result

        return wrapper_notify_complete
