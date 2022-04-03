from typing import Any
from unittest import TestCase, mock
import dataclasses
from pub_sub import dispatch_events_output
from pub_sub import Publisher
from publisher import Publisher


class MySubscriber:

    def execute(self, message: Any) -> None:
        pass


class OtherSubscriber:
    def execute(self, message: Any) -> None:
        pass


class DispatchEventsTestCase(TestCase):

    def setUp(self) -> None:
        Publisher().register(event="my_event", subscriber=MySubscriber())
        Publisher().register(event="my_event", subscriber=OtherSubscriber())


    @mock.patch("pub_sub.dispatcher.Publisher.dispatch")
    def test_dispatch_events(self, mock_dispatch: mock.MagicMock) -> None:
        @dispatch_events_output({"my_event"})
        def func(value: Any) -> Any:
            return value

        @dataclasses.dataclass
        class ItemTest:
            event: str
            message: Any

        table = [
            ItemTest("my_event", True),
            ItemTest("my_event", False)
        ]

        for item in table:
            with self.subTest(item=item):
                result = func(item.message)
                mock_dispatch.assert_called_with(item.event, item.message)
                self.assertEqual(result, item.message)

    def tearDown(self) -> None:
        Publisher()
