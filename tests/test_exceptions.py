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
