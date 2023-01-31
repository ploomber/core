from unittest.mock import Mock, ANY

import pytest
from ploomber_core.telemetry import telemetry as telemetry_module


@pytest.fixture
def mock_posthog(monkeypatch):
    mock_info = Mock(return_value=(True, "UUID", False))
    mock = Mock()
    monkeypatch.setattr(telemetry_module.posthog, "capture", mock)
    monkeypatch.setattr(telemetry_module, "_get_telemetry_info", mock_info)
    yield mock


@pytest.mark.parametrize(
    "y, y_logged",
    [
        [1, 1],
        [1.0, 1.0],
        ["something", "something"],
        [False, False],
        [(1, 2), [1, 2]],
        [{1, 2}, [1, 2]],
        ["a" * 201, "a" * 200 + "...[truncated]"],
        [[0] * 11, [0] * 10 + ["TRUNCATED"]],
        [(0,) * 11, [0] * 10 + ["TRUNCATED"]],
    ],
)
def test_logs_args(mock_posthog, y, y_logged):
    telemetry = telemetry_module.Telemetry(
        api_key="KEY", package_name="somepackage", version="0.1"
    )

    @telemetry.log_call(log_args=True)
    def add(x, y):
        pass

    add(x=1, y=y)

    expected_first = dict(
        distinct_id="UUID",
        event="somepackage-add-started",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-add-started",
            "client_time": ANY,
            "metadata": {
                "args": {"x": 1, "y": y_logged},
                "argv": ANY,
            },
            "total_runtime": None,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    expected_second = dict(
        distinct_id="UUID",
        event="somepackage-add-success",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-add-success",
            "client_time": ANY,
            "metadata": {
                "args": {"x": 1, "y": y_logged},
                "argv": ANY,
            },
            "total_runtime": ANY,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    assert mock_posthog.call_args_list[0][1] == expected_first
    assert mock_posthog.call_args_list[1][1] == expected_second


@pytest.mark.parametrize(
    "y, y_logged",
    [
        [1, 1],
        [1.0, 1.0],
        ["something", "something"],
        [False, False],
        [(1, 2), [1, 2]],
        [{1, 2}, [1, 2]],
        ["a" * 201, "a" * 200 + "...[truncated]"],
    ],
)
def test_logs_args_with_group(mock_posthog, y, y_logged):
    telemetry = telemetry_module.Telemetry(
        api_key="KEY", package_name="somepackage", version="0.1"
    )

    class SomeObject:
        @telemetry.log_call(log_args=True, group="SomeObject")
        def add(self, x, y):
            pass

    obj = SomeObject()
    obj.add(x=1, y=y)

    expected_first = dict(
        distinct_id="UUID",
        event="somepackage-SomeObject-add-started",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-SomeObject-add-started",
            "client_time": ANY,
            "metadata": {
                "args": {"x": 1, "y": y_logged},
                "argv": ANY,
            },
            "total_runtime": None,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    expected_second = dict(
        distinct_id="UUID",
        event="somepackage-SomeObject-add-success",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-SomeObject-add-success",
            "client_time": ANY,
            "metadata": {
                "args": {"x": 1, "y": y_logged},
                "argv": ANY,
            },
            "total_runtime": ANY,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    assert mock_posthog.call_args_list[0][1] == expected_first
    assert mock_posthog.call_args_list[1][1] == expected_second


def test_doesnt_log_args_with_disallowed_types(mock_posthog):
    telemetry = telemetry_module.Telemetry(
        api_key="KEY", package_name="somepackage", version="0.1"
    )

    @telemetry.log_call(log_args=True)
    def add(x, y=1):
        pass

    add(x=dict(a=1))

    expected_first = dict(
        distinct_id="UUID",
        event="somepackage-add-started",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-add-started",
            "client_time": ANY,
            "metadata": {
                "args": {"y": 1},
                "argv": ANY,
            },
            "total_runtime": None,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    expected_second = dict(
        distinct_id="UUID",
        event="somepackage-add-success",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-add-success",
            "client_time": ANY,
            "metadata": {
                "args": {"y": 1},
                "argv": ANY,
            },
            "total_runtime": ANY,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    assert mock_posthog.call_args_list[0][1] == expected_first
    assert mock_posthog.call_args_list[1][1] == expected_second


def test_doesnt_log_ignored_args(mock_posthog):
    telemetry = telemetry_module.Telemetry(
        api_key="KEY", package_name="somepackage", version="0.1"
    )

    @telemetry.log_call(log_args=True, ignore_args={"y"})
    def add(x, y=1):
        pass

    add(x=1)

    expected_first = dict(
        distinct_id="UUID",
        event="somepackage-add-started",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-add-started",
            "client_time": ANY,
            "metadata": {
                "args": {"x": 1},
                "argv": ANY,
            },
            "total_runtime": None,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    expected_second = dict(
        distinct_id="UUID",
        event="somepackage-add-success",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-add-success",
            "client_time": ANY,
            "metadata": {
                "args": {"x": 1},
                "argv": ANY,
            },
            "total_runtime": ANY,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    assert mock_posthog.call_args_list[0][1] == expected_first
    assert mock_posthog.call_args_list[1][1] == expected_second


def test_logs_if_error(mock_posthog):
    telemetry = telemetry_module.Telemetry(
        api_key="KEY", package_name="somepackage", version="0.1"
    )

    @telemetry.log_call(log_args=True)
    def add(x, y=1):
        raise ValueError("some error happened")

    with pytest.raises(ValueError):
        add(x=1)

    expected_first = dict(
        distinct_id="UUID",
        event="somepackage-add-started",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-add-started",
            "client_time": ANY,
            "metadata": {
                "args": {"x": 1, "y": 1},
                "argv": ANY,
            },
            "total_runtime": None,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    expected_second = dict(
        distinct_id="UUID",
        event="somepackage-add-error",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-add-error",
            "client_time": ANY,
            "metadata": {
                "args": {"x": 1, "y": 1},
                "argv": ANY,
                "exception": "some error happened",
                "type": None,
            },
            "total_runtime": ANY,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    assert mock_posthog.call_args_list[0][1] == expected_first
    assert mock_posthog.call_args_list[1][1] == expected_second


@pytest.mark.parametrize(
    "y, y_logged",
    [
        [1, 1],
        [1.0, 1.0],
        ["something", "something"],
        [False, False],
        [(1, 2), [1, 2]],
        [{1, 2}, [1, 2]],
        ["a" * 201, "a" * 200 + "...[truncated]"],
    ],
)
def test_telemetry_group(mock_posthog, y, y_logged):
    telemetry = telemetry_module.Telemetry(
        api_key="KEY", package_name="somepackage", version="0.1"
    )

    group = telemetry.create_group("SomeObject")

    class SomeObject:
        @group.log_call(log_args=True)
        def add(self, x, y):
            pass

        @group.log_call(log_args=True)
        def substract(self, x, y):
            pass

    obj = SomeObject()
    obj.add(x=1, y=y)
    obj.substract(x=1, y=y)

    expected_first = dict(
        distinct_id="UUID",
        event="somepackage-SomeObject-add-started",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-SomeObject-add-started",
            "client_time": ANY,
            "metadata": {
                "args": {"x": 1, "y": y_logged},
                "argv": ANY,
            },
            "total_runtime": None,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    expected_second = dict(
        distinct_id="UUID",
        event="somepackage-SomeObject-add-success",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-SomeObject-add-success",
            "client_time": ANY,
            "metadata": {
                "args": {"x": 1, "y": y_logged},
                "argv": ANY,
            },
            "total_runtime": ANY,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    expected_third = dict(
        distinct_id="UUID",
        event="somepackage-SomeObject-substract-started",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-SomeObject-substract-started",
            "client_time": ANY,
            "metadata": {
                "args": {"x": 1, "y": y_logged},
                "argv": ANY,
            },
            "total_runtime": None,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    expected_fourth = dict(
        distinct_id="UUID",
        event="somepackage-SomeObject-substract-success",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-SomeObject-substract-success",
            "client_time": ANY,
            "metadata": {
                "args": {"x": 1, "y": y_logged},
                "argv": ANY,
            },
            "total_runtime": ANY,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    assert mock_posthog.call_args_list[0][1] == expected_first
    assert mock_posthog.call_args_list[1][1] == expected_second
    assert mock_posthog.call_args_list[2][1] == expected_third
    assert mock_posthog.call_args_list[3][1] == expected_fourth


def test_method_with_no_arguments(mock_posthog):
    telemetry = telemetry_module.Telemetry(
        api_key="KEY", package_name="somepackage", version="0.1"
    )

    class SomeObject:
        @telemetry.log_call(log_args=True, group="SomeObject")
        def do_stuff(self):
            pass

    obj = SomeObject()
    obj.do_stuff()

    expected_first = dict(
        distinct_id="UUID",
        event="somepackage-SomeObject-do-stuff-started",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-SomeObject-do-stuff-started",
            "client_time": ANY,
            "metadata": {
                "argv": ANY,
                "args": {},
            },
            "total_runtime": None,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    expected_second = dict(
        distinct_id="UUID",
        event="somepackage-SomeObject-do-stuff-success",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-SomeObject-do-stuff-success",
            "client_time": ANY,
            "metadata": {
                "argv": ANY,
                "args": {},
            },
            "total_runtime": ANY,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    assert mock_posthog.call_args_list[0][1] == expected_first
    assert mock_posthog.call_args_list[1][1] == expected_second


def test_function_with_no_arguments(mock_posthog):
    telemetry = telemetry_module.Telemetry(
        api_key="KEY", package_name="somepackage", version="0.1"
    )

    @telemetry.log_call(log_args=True)
    def do_stuff():
        pass

    do_stuff()

    expected_first = dict(
        distinct_id="UUID",
        event="somepackage-do-stuff-started",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-do-stuff-started",
            "client_time": ANY,
            "metadata": {
                "argv": ANY,
                "args": {},
            },
            "total_runtime": None,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    expected_second = dict(
        distinct_id="UUID",
        event="somepackage-do-stuff-success",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-do-stuff-success",
            "client_time": ANY,
            "metadata": {
                "argv": ANY,
                "args": {},
            },
            "total_runtime": ANY,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    assert mock_posthog.call_args_list[0][1] == expected_first
    assert mock_posthog.call_args_list[1][1] == expected_second


def test_function_with_args(mock_posthog):
    telemetry = telemetry_module.Telemetry(
        api_key="KEY", package_name="somepackage", version="0.1"
    )

    @telemetry.log_call(log_args=True)
    def do_stuff(a, *args):
        pass

    do_stuff(1, 2, 3)

    expected_first = dict(
        distinct_id="UUID",
        event="somepackage-do-stuff-started",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-do-stuff-started",
            "client_time": ANY,
            "metadata": {
                "argv": ANY,
                "args": {"a": 1, "args": 2},
            },
            "total_runtime": None,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    expected_second = dict(
        distinct_id="UUID",
        event="somepackage-do-stuff-success",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-do-stuff-success",
            "client_time": ANY,
            "metadata": {
                "argv": ANY,
                "args": {"a": 1, "args": 2},
            },
            "total_runtime": ANY,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    assert mock_posthog.call_args_list[0][1] == expected_first
    assert mock_posthog.call_args_list[1][1] == expected_second


def test_function_with_kwargs(mock_posthog):
    telemetry = telemetry_module.Telemetry(
        api_key="KEY", package_name="somepackage", version="0.1"
    )

    @telemetry.log_call(log_args=True)
    def do_stuff(a, **kwargs):
        pass

    do_stuff(1, b=2, c=3)

    expected_first = dict(
        distinct_id="UUID",
        event="somepackage-do-stuff-started",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-do-stuff-started",
            "client_time": ANY,
            "metadata": {
                "argv": ANY,
                "args": {"a": 1, "b": 2, "c": 3},
            },
            "total_runtime": None,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    expected_second = dict(
        distinct_id="UUID",
        event="somepackage-do-stuff-success",
        properties={
            "event_id": ANY,
            "user_id": "UUID",
            "action": "somepackage-do-stuff-success",
            "client_time": ANY,
            "metadata": {
                "argv": ANY,
                "args": {"a": 1, "b": 2, "c": 3},
            },
            "total_runtime": ANY,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )

    assert mock_posthog.call_args_list[0][1] == expected_first
    assert mock_posthog.call_args_list[1][1] == expected_second
