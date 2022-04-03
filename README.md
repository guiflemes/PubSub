### PubSub


* This allows the registration of multiple subscribers per event.
* Any event that implements the Subscriber interface can be registered at the publisher
* Two events dispatchers

# Installation

`pip install pub-sub-events`

# How to use?

Let's create two events that implemets Subscriber interface, the first is a simple python class and the second a celery task.


```python

@dataclasses.dataclass
class MyClass:
    name: str


class NormalSubscriber:
    def execute(self, message: str) -> None:
        print(message)


class SubscriberCeleryTask(Task):
    def __init__(self) -> None:
        current_app.tasks.register(self)

    def run(self, message: str) -> None:
        print(message)

    def to_json(self, message: MyClass) -> json:
        return json.dumps(dataclasses.asdict(message))

    def execute(self, message: MyClass) -> None:
        serializer = self.to_json(message)
        self.delay(serializer)
 ```

Now lets register it.

```python
publisher_app = Publisher()
publisher_app.register("event_print_name",  NormalSubscriber())
publisher_app.register("event_print_my_class",  SubscriberCeleryTask())
```

With the subscribers implemented and registered we can decorate our methods or functions to trigger the events.

* **dispatch_events_output** will always get the function's output, so in the exemple bellow the printed is "MyClass as dict"
* **dispatch_events_input** will always get the first function's input, so in the exemple bellow the printed is "name"

```python

@dispatch_events_output({"event_print_my_class"})
@dispatch_events_input({"event_print_name"})
def create_my_class(name:str) -> MyClass:
    return MyClass(name)

```



