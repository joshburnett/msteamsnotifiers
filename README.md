msteamsnotifiers: Decorators for automatically notifying an MS Teams channel of events
======================================================================================

`msteamsnotifiers` makes it easy to automatically send notifications to a channel in MS Teams from Python.

With the [retirement of Office 365 Connectors](https://devblogs.microsoft.com/microsoft365dev/retirement-of-office-365-connectors-within-microsoft-teams/), 
this library has been updated to use Workflows. Follow the instructions in [this simple, short video](https://www.youtube.com/watch?v=jHTU_jUnswY) to set up the Workflow for your Teams channel. You can then get the webhook URL from the "When a Teams webhook request is received" step of the workflow (it's the auto-generated HTTP POST URL field, which has a handy 'copy' button next to it).

## Installation

Install with `pip`:

```
pip install msteamsnotifiers
```

## Usage

Create a Notifier instance by passing in the webhook URL for your workflow:

```python
from msteamsnotifiers import Notifier

notifier = Notifier('<your Microsoft webhook URL>')
```

### Posting simple messages to a channel

This is the simplest way of posting very simple messages to a channel in MS Teams.

```python
from msteamsnotifiers import Notifier

notifier = Notifier('<your Microsoft webhook URL>')

notifier.post_simple_teams_message('Hello channel!')
notifier.post_simple_teams_message('[Markdown formatting](https://www.markdownguide.org/) is supported.')
notifier.post_simple_teams_message('This was sent using [msteamsnotifiers](https://pypi.org/project/msteamsnotifiers/)')

```


### Notifying a channel of an exception

`@Notifiy.notify_exceptions` is a decorator that will catch any exceptions in the decorated function and send a specially formatted message with details about the exception to a channel.

```python
from msteamsnotifiers import Notifier

notifier = Notifier('<your Microsoft webhook URL>')

@notifier.notify_exceptions()
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
from msteamsnotifiers import Notifier

notifier = Notifier('<your Microsoft webhook URL>')

import time

@notifier.notify_complete()
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
### 0.3: 2024-12-16

- Update the API, creating a new Notifier class. This allows easy creation of multiple notifiers that have their own webhooks, rather than needing to pass the webhook URL to each decorator.
- Non-API related: Update project to use the pyproject.toml instead of setup.py

### 0.2: 2024-07-18

- Update to support the new data schema required by the Workflows app.
  - [Office 365 Connectors are going away](https://devblogs.microsoft.com/microsoft365dev/retirement-of-office-365-connectors-within-microsoft-teams/)
  - This version isn't compatible with any O365 Connector webhooks you've previously set up. According to the link directly above, creation of new Connector webhooks after August 15th, 2024 is no longer possible. Existing connector webhooks stopped working on October 1st, 2024.
- Removed dependency on `pymsteams` (an excellent library, *RIP*)

### 0.1: 2021-10-02

- Initial release

