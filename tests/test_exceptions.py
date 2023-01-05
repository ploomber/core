import pytest

from ploomber_core import exceptions


def test_show(capsys):
    exceptions.BaseException("something").show()
    captured = capsys.readouterr()
    assert captured.err == "Error: something\n"


@pytest.mark.parametrize("class_", [BaseException, Exception])
def test_show_chained_exceptions(class_, capsys):
    first = class_("first")
    second = exceptions.BaseException("second")

    try:
        raise second from first
    except Exception as e:
        ex = e

    ex.show()

    captured = capsys.readouterr()
    assert captured.err == "Error: second\nfirst\n"


def test_value_error():
    with pytest.raises(ValueError):
        raise exceptions.PloomberValueError("error")


def test_type_error():
    with pytest.raises(TypeError):
        raise exceptions.PloomberTypeError("error")


def test_key_error():
    with pytest.raises(KeyError):
        raise exceptions.PloomberKeyError("error")


def test_modify_exceptions_value_error():
    @exceptions.modify_exceptions
    def crash():
        raise ValueError("some message")

    with pytest.raises(ValueError) as excinfo:
        crash()

    assert "https://ploomber.io/community" in str(excinfo.value)


def test_modify_exceptions_value_error_method():
    class Something:
        @exceptions.modify_exceptions
        def crash(self):
            raise ValueError("some message")

    with pytest.raises(ValueError) as excinfo:
        Something().crash()

    assert "https://ploomber.io/community" in str(excinfo.value)


def test_do_not_catch_other_errors():
    @exceptions.modify_exceptions
    def crash():
        raise TypeError("some message")

    with pytest.raises(TypeError) as excinfo:
        crash()

    assert "https://ploomber.io/community" not in str(excinfo.value)
