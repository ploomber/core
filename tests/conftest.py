import shutil
import os
import pytest
import tempfile
import posthog
from unittest.mock import MagicMock
from stat import S_IREAD, S_IRGRP, S_IROTH
import platform

if platform.system() == "Windows":
    import win32security
    import ntsecuritycon as con


@pytest.fixture()
def tmp_directory():
    old = os.getcwd()
    tmp = tempfile.mkdtemp()
    os.chdir(str(tmp))

    yield tmp

    os.chdir(old)

    # ignore unexpected permission error during test suite cleanup
    shutil.rmtree(str(tmp), ignore_errors=True)


@pytest.fixture()
def tmp_readonly_directory():
    old = os.getcwd()
    tmp = tempfile.mkdtemp()
    os.chdir(str(tmp))

    # Read permissions

    # TODO: Fix this for Windows
    # Filesystem should not be writable, after running the below code
    # But it is currently. Fix this
    if platform.system() == "Windows":
        # https://learn.microsoft.com/en-us/windows/win32/secauthz/well-known-sids
        everyone = win32security.ConvertStringSidToSid("S-1-1-0")

        # https://stackoverflow.com/questions/12168110
        sd = win32security.GetFileSecurity(tmp, win32security.DACL_SECURITY_INFORMATION)
        dacl = sd.GetSecurityDescriptorDacl()
        dacl.AddAccessAllowedAce(
            win32security.ACL_REVISION_DS,
            con.FILE_GENERIC_READ,
            everyone,
        )
        sd.SetSecurityDescriptorDacl(1, dacl, 0)
        win32security.SetFileSecurity(tmp, win32security.DACL_SECURITY_INFORMATION, sd)
    else:
        # Although Windows supports chmod(), you can only set the file’s read-only flag
        # with it(via the stat.S_IWRITE and stat.S_IREAD constants or
        # a corresponding integer value). All other bits are ignored.
        os.chmod(tmp, S_IREAD | S_IRGRP | S_IROTH)

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

        mock_posthog_instance = MagicMock()
        mock_posthog_instance.capture = external_access.get_something
        mock_posthog_class = MagicMock(return_value=mock_posthog_instance)

        monkeypatch_session.setattr(posthog, "Posthog", mock_posthog_class)
        yield
