import shutil
import os
import pytest
import tempfile


@pytest.fixture()
def tmp_directory():
    old = os.getcwd()
    tmp = tempfile.mkdtemp()
    os.chdir(str(tmp))

    yield tmp

    os.chdir(old)

    # ignore unexpected permission error during test suite cleanup
    shutil.rmtree(str(tmp), ignore_errors=True)
