msteamsnotifiers: Decorators for automatically notifying an MS Teams channel of events
======================================================================================

`msteamsnotifiers` makes it easy to automatically send notifications to a channel in MS Teams.

Based on the excellent [`pymsteams`](https://pypi.org/project/pymsteams/), this library uses Webhook Connectors for Microsoft Teams. You will need the webhook URL for your channel. Please visit [this Microsoft documentation](https://dev.outlook.com/Connectors/GetStarted#creating-messages-through-office-365-connectors-in-microsoft-teams) for instructions on how to obtain the correct URL.  Sometimes the screenshots in this documentation are not 100% up-to-date, but [this other Microsoft documentation](https://dev.outlook.com/connectors/reference) will have the most up-to-date screenshots of the process.

## Installation

Install with `pip`:

```
pip install msteamsnotifiers
```

## Usage

All the functions provided in `msteamsnotifiers` can take the webhook URL as an argument. If not specified, the value in `msteamsnotifiers.default_webhook_url` will be used. This allows you to set this once and then not have to pass it to the other functions each time they are used:

```python
import msteamsnotifiers

msteamsnotifiers.default_webhook_url = '<your Microsoft webhook URL>'
```

### Posting simple messages to a channel

This is the simplest way of posting very simple messages to a channel in MS Teams.

```python
import msteamsnotifiers

msteamsnotifiers.default_webhook_url = '<your Microsoft webhook URL>'

msteamsnotifiers.post_simple_teams_message('Hello channel!')
msteamsnotifiers.post_simple_teams_message('[Markdown formatting](https://www.markdownguide.org/) is supported.]')
```

If you want to send richer messages with sections, titles, and other features supported by MS Teams, the [`pymsteams`](https://pypi.org/project/pymsteams/) library makes this very easy.


### Notifying a channel of an exception

`@notify_exceptions` is a decorator that will catch any exceptions in the decorated function and send a specially formatted message with details about the exception to a channel.

```python
import msteamsnotifiers
from msteamsnotifiers import notify_exceptions

msteamsnotifiers.default_webhook_url = '<your Microsoft webhook URL>'

@notify_exceptions()
def fn_with_potential_exception(a, b):
    return a + b

# This function call completes successfully, so the channel will not be notified
sum1 = fn_with_potential_exception(1, 2)

# This function call will generate an exception, resulting in the channel being notified
sum2 = fn_with_potential_exception('a', True)
```

The format of the channel notification can be specified using the `template` decorator argument. If no template is specified, the default template is `msteamsnotifiers.default_exception_template`, which includes the full traceback:

```python
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
"""
```

This package variable can be modified similarly to the `default_webhook_url` parameter.

The `friendly_tracebacks` module is used to format the included traceback to make it easier to read. 

### Notifying a channel of a function's completion

`@notify_complete` is a decorator that will send a message to a channel upon successful completion of the decorated function.

```python
import msteamsnotifiers
from msteamsnotifiers import notify_complete

msteamsnotifiers.default_webhook_url = '<your Microsoft webhook URL>'

import time

@notify_complete()
def long_running_function(a, b):
    print('Thinking... thinking... thinking...')
    time.sleep(3600)
    print(f"Aha! The answer is {a+b}!")
    return a + b

# The channel will be notified upon completion of this function call
sum1 = long_running_function(1, 2)
```

The format of this message can be specified using the `template` decorator argument. If no template is specified, the default template is `msteamsnotifiers.default_completion_template`:

```python
default_completion_template = """
*{timestamp}*  
Function completed: **{funcname}()** in file **"{filename}"**  
Node: {machine_name} ({ip_address})  
args: {args}  
kwargs: {kwargs}
"""
```


Releases
--------
### 0.1: 2021-10-02

- Initial release

