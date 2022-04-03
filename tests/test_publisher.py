import dataclasses
from pub_sub import Publisher
from unittest import TestCase, mock
from typing import Any
from threading import Thread

from pub_sub.errors import EventNotRegisteredError


class SubscriptionOne:
    def __init__(self, name) -> None:
        self.name = name

    def execute(self, message: Any) -> None:
        print(f"update: {self.name} got message {message}")


class SubscriptionTwo:
    def __init__(self, name) -> None:
        self.name = name

    def execute(self, message: Any) -> None:
        print(f"update: {self.name} got message {message}")

    def receive(self, message: Any) -> None:
        print(f"receive: {self.name} got message {message}")


class PublisherTestCase(TestCase):

    def setUp(self) -> None:
        self.publisher = Publisher()
        self.publisher._events = {}

    def test_get_subscribers(self) -> None:
        subscriber = SubscriptionOne("sub_one")
        self.publisher.register("email", subscriber)
        result = self.publisher.get_subscribers("email")
        result_sub = list(result.keys())[0]
        self.assertEqual(subscriber, result_sub)

    def test_get_subscribers_raises_KeyError(self) -> None:
        @dataclasses.dataclass
        class testCase:
            desc: str
            event: str

        test_cases = [
            testCase("event error 1", "error 1"),
            testCase("event error 2", "error 2"),
            testCase("event error 3", "error 3"),
        ]

        for t in test_cases:
            with self.subTest(msg=t.desc, event=t.event) as ctx:
                with self.assertRaises(EventNotRegisteredError):
                    self.publisher.get_subscribers(test_cases[0].event)
                    self.assertIn(f"No event called '{t.event}' registered.", str(ctx))

    def test_register(self) -> None:
        sub_one = SubscriptionOne("sub_one")
        sub_two = SubscriptionTwo("sub_two")
        self.publisher.register("email", sub_one)
        self.publisher.register("email", sub_two, callback=sub_two.receive)

        self.publisher.register("slack", sub_one)

        self.assertEqual(len(self.publisher.get_subscribers("email")), 2)
        self.assertEqual(len(self.publisher.get_subscribers("slack")), 1)

    def test_unregister(self) -> None:
        sub_one = SubscriptionOne("sub_one")
        self.publisher.register("email", sub_one)

        self.publisher.unregister("email", sub_one)
        self.assertEqual(len(self.publisher.get_subscribers("email")), 0)

    def test_dispatch(self) -> None:
        mock_execute = mock.MagicMock()
        mock_sub = mock.MagicMock()
        mock_sub.execute = mock_execute

        self.publisher.register("email", mock_sub)

        self.publisher.dispatch("email", "message")
        mock_execute.assert_called_once_with("message")

    def test_singleton(self) -> None:
        publisher1 = Publisher()
        publisher2 = Publisher()
        self.assertEqual(publisher1, publisher2)

    def test_singleton_threads_safe(self) -> None:
        results = []

        def test_singleton() -> None:
            publisher = Publisher()
            results.append(publisher)

        process1 = Thread(target=test_singleton)
        process2 = Thread(target=test_singleton)
        process1.start()
        process2.start()

        self.assertEqual(results[0], results[1], self.publisher)

    def tearDown(self) -> None:
        Publisher()
