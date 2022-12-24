import shutil
import os
import pytest
import tempfile
import posthog
from unittest.mock import MagicMock


@pytest.fixture()
def tmp_directory():
    old = os.getcwd()
    tmp = tempfile.mkdtemp()
    os.chdir(str(tmp))

    yield tmp

    os.chdir(old)

    # ignore unexpected permission error during test suite cleanup
    shutil.rmtree(str(tmp), ignore_errors=True)


@pytest.fixture(scope="class")
def monkeypatch_session():
    from _pytest.monkeypatch import MonkeyPatch

    m = MonkeyPatch()
    yield m
    m.undo()


@pytest.fixture(scope="class", autouse=True)
def external_access(request, monkeypatch_session):
    # https://miguendes.me/pytest-disable-autouse
    if "allow_posthog" in request.keywords:
        yield
    else:
        # https://github.com/pytest-dev/pytest/issues/7061#issuecomment-611892868
        external_access = MagicMock()
        external_access.get_something = MagicMock(return_value="Mock was used.")
        monkeypatch_session.setattr(posthog, "capture", external_access.get_something)
        yield
