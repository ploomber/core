import pathlib
import sys
from unittest.mock import Mock, call, ANY
from pathlib import Path
import datetime
import logging
import os
import stat
import shutil

import pytest
import yaml
import posthog

from ploomber_core.telemetry import telemetry
from ploomber_core.telemetry import system_info
from ploomber_core.telemetry.validate_inputs import str_param, opt_str_param

from ploomber_core.exceptions import BaseException

MOCK_API_KEY = "phc_P1dsjk20bijsabdaib2eu"


@pytest.fixture()
def inside_conda_env(monkeypatch):
    monkeypatch.setenv("CONDA_PREFIX", True)


@pytest.fixture()
def inside_pip_env(monkeypatch):
    monkeypatch.setattr(telemetry.sys, "prefix", "sys.prefix")
    monkeypatch.setattr(telemetry.sys, "base_prefix", "base_prefix")


@pytest.fixture
def ignore_ploomber_stats_enabled_env_var(monkeypatch):
    """
    GitHub Actions configuration scripts set the PLOOMBER_STATS_ENABLED
    environment variable to prevent CI events from going to posthog, this
    inferes with some tests. This fixture removes its value temporarily.

    GitHub actions also sets CI
    """
    if "PLOOMBER_STATS_ENABLED" in os.environ:
        monkeypatch.delenv("PLOOMBER_STATS_ENABLED", raising=True)

    if "CI" in os.environ:
        monkeypatch.delenv("CI", raising=True)


def test_creates_config_directory(
    monkeypatch, tmp_directory, ignore_ploomber_stats_enabled_env_var
):
    monkeypatch.setattr(telemetry, "DEFAULT_HOME_DIR", str(Path().absolute()))

    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "0.14.0")

    @_telemetry.log_call()
    def my_function():
        pass

    my_function()

    assert Path("stats").is_dir()
    assert Path("stats", "uid.yaml").is_file()
    assert Path("stats", "config.yaml").is_file()


@pytest.fixture
def ignore_env_var_and_set_tmp_default_home_dir(
    tmp_directory, ignore_ploomber_stats_enabled_env_var, monkeypatch
):
    """
    ignore_ploomber_stats_enabled_env_var + overrides DEFAULT_HOME_DIR
    to prevent the local configuration to interfere with tests
    """
    monkeypatch.setattr(telemetry, "DEFAULT_HOME_DIR", str(Path().absolute()))


def test_user_settings_create_file(tmp_directory, monkeypatch):
    monkeypatch.setattr(telemetry, "DEFAULT_HOME_DIR", str(Path().absolute()))

    settings = telemetry.UserSettings()
    content = yaml.safe_load(Path("stats", "config.yaml").read_text())

    assert content == {
        "cloud_key": None,
        "user_email": None,
        "stats_enabled": True,
        "version_check_enabled": True,
    }
    assert settings.cloud_key is None
    assert settings.stats_enabled


def test_user_settings_get_cloud_key_from_file(tmp_directory, monkeypatch):
    monkeypatch.setattr(telemetry, "DEFAULT_HOME_DIR", str(Path().absolute()))
    parent = Path("stats")
    parent.mkdir()
    (parent / "config.yaml").write_text(
        """
cloud_key: some-cloud-key
"""
    )
    settings = telemetry.UserSettings()

    assert settings.get_cloud_key() == "some-cloud-key"


def test_user_settings_get_cloud_key_from_env_var(tmp_directory, monkeypatch):
    monkeypatch.setattr(telemetry, "DEFAULT_HOME_DIR", str(Path().absolute()))
    monkeypatch.setenv("PLOOMBER_CLOUD_KEY", "another-cloud-key")

    parent = Path("stats")
    parent.mkdir()
    (parent / "config.yaml").write_text(
        """
cloud_key: some-cloud-key
"""
    )
    settings = telemetry.UserSettings()

    assert settings.get_cloud_key() == "another-cloud-key"


def test_internal_create_file(tmp_directory, monkeypatch):
    monkeypatch.setattr(telemetry, "DEFAULT_HOME_DIR", str(Path().absolute()))
    monkeypatch.setattr(telemetry, "uuid4", lambda: "some-unique-uuid")

    internal = telemetry.Internal()
    content = yaml.safe_load(Path("stats", "uid.yaml").read_text())

    assert content == {
        "uid": "some-unique-uuid",
        "last_version_check": None,
        "last_cloud_check": None,
        "first_time": True,
    }
    assert internal.uid == "some-unique-uuid"
    assert internal.last_version_check is None


def test_does_not_overwrite_existing_uid(tmp_directory, monkeypatch):
    monkeypatch.setattr(telemetry, "DEFAULT_HOME_DIR", str(Path().absolute()))

    Path("stats").mkdir()
    Path("stats", "uid.yaml").write_text(yaml.dump({"uid": "existing-uid"}))

    internal = telemetry.Internal()

    assert internal.uid == "existing-uid"


# Validations tests
def test_str_validation():
    res = str_param("Test", "")
    assert isinstance(res, str)
    res = str_param("TEST", "test_param")
    assert "TEST" == res
    with pytest.raises(TypeError) as exc_info:
        str_param(3, "Test_number")

    exception_raised = exc_info.value
    assert isinstance(exception_raised, TypeError)


def test_opt_str_validation():
    res = opt_str_param("Test", "")
    assert isinstance(res, str)
    res = opt_str_param("Test", "TEST")
    assert "TEST" == res
    res = opt_str_param("Test", None)
    assert not res

    with pytest.raises(TypeError) as exc_info:
        opt_str_param("Test", 3)

    exception_raised = exc_info.value
    assert isinstance(exception_raised, TypeError)


def test_check_stats_enabled(ignore_env_var_and_set_tmp_default_home_dir):
    stats_enabled = telemetry.check_telemetry_enabled()
    assert stats_enabled is True


@pytest.mark.parametrize(
    "name",
    [
        "CI",
        "READTHEDOCS",
    ],
)
def test_disable_stats_if_ci_env(
    name, ignore_env_var_and_set_tmp_default_home_dir, monkeypatch
):
    monkeypatch.setenv(name, "true")
    stats_enabled = telemetry.check_telemetry_enabled()
    assert stats_enabled is False


@pytest.mark.parametrize(
    "yaml_value, expected_first, env_value, expected_second",
    [
        ["true", True, "false", False],
        ["TRUE", True, "FALSE", False],
        ["false", False, "true", True],
        ["FALSE", False, "TRUE", True],
    ],
)
def test_env_var_takes_precedence(
    monkeypatch,
    ignore_env_var_and_set_tmp_default_home_dir,
    yaml_value,
    expected_first,
    env_value,
    expected_second,
):
    stats = Path("stats")
    stats.mkdir()

    (stats / "config.yaml").write_text(
        f"""
                                        stats_enabled: {yaml_value}
                                        """
    )

    assert telemetry.check_telemetry_enabled() is expected_first

    monkeypatch.setenv("PLOOMBER_STATS_ENABLED", env_value, prepend=False)

    assert telemetry.check_telemetry_enabled() is expected_second


def test_first_usage(monkeypatch, tmp_directory):
    monkeypatch.setattr(telemetry, "DEFAULT_HOME_DIR", str(Path().absolute()))

    assert telemetry.check_first_time_usage()
    assert not telemetry.check_first_time_usage()


# The below fixtures are to mock the different virtual environments
# Ref: https://stackoverflow.com/questions/51266880/detect-if-
# python-is-running-in-a-conda-environment
def test_conda_env(monkeypatch, inside_conda_env, tmp_directory):
    # Set a conda parameterized env
    env = system_info.is_conda()
    assert bool(env) is True
    env = system_info.get_env()
    assert env == "conda"


# Ref: https://stackoverflow.com/questions/1871549/
# determine-if-python-is-running-inside-virtualenv
def test_pip_env(monkeypatch, inside_pip_env):
    # Set a pip parameterized env
    env = system_info.in_virtualenv()
    assert env is True
    env = system_info.get_env()
    assert env == "pip"


# Ref: https://stackoverflow.com/questions/43878953/how-does-one-detect-if-
# one-is-running-within-a-docker-container-within-python
def test_docker_env(monkeypatch):
    def mock(input_path):
        return "dockerenv" in str(input_path)

    monkeypatch.setattr(pathlib.Path, "exists", mock)
    docker = system_info.is_docker()
    assert docker is True


# Ref https://stackoverflow.com/questions/53581278/test-if-
# notebook-is-running-on-google-colab
def test_colab_env(monkeypatch):
    colab = system_info.is_colab()
    assert colab is False

    m = Mock()

    monkeypatch.setitem(sys.modules, "google", m)
    monkeypatch.setitem(sys.modules, "google.colab", m)
    colab = system_info.is_colab()
    assert colab is True


# Ref https://learn.paperspace.com/video/creating-a-jupyter-notebook
@pytest.mark.parametrize(
    "env_variable", ["PS_API_KEY", "PAPERSPACE_API_KEY", "PAPERSPACE_NOTEBOOK_REPO_ID"]
)
def test_paperspace_env(monkeypatch, env_variable):
    monkeypatch.setenv(env_variable, True)
    pspace = system_info.is_paperspace()
    assert pspace is True


# Ref https://stackoverflow.com/questions/63298054/how-to-check-if-my-code
# -runs-inside-a-slurm-environment
def test_slurm_env(monkeypatch):
    monkeypatch.setenv("SLURM_JOB_ID", True)
    slurm = system_info.is_slurm()
    assert slurm is True


# Ref https://airflow.apache.org/docs/apache-airflow/stable/
# cli-and-env-variables-ref.html?highlight=airflow_home#envvar-AIRFLOW_HOME
@pytest.mark.parametrize("env_variable", ["AIRFLOW_CONFIG", "AIRFLOW_HOME"])
def test_airflow_env(monkeypatch, env_variable):
    monkeypatch.setenv(env_variable, True)
    airflow = system_info.is_airflow()
    assert airflow is True


# Ref https://stackoverflow.com/questions/110362/how-can-i-find-
# the-current-os-in-python
@pytest.mark.parametrize("os_param", ["Windows", "Linux", "MacOS", "Ubuntu"])
def test_os_type(monkeypatch, os_param):
    mock = Mock()
    mock.return_value = os_param
    monkeypatch.setattr(system_info.platform, "system", mock)
    os_type = system_info.get_os()
    assert os_type == os_param


def test_full_telemetry_info(monkeypatch, ignore_env_var_and_set_tmp_default_home_dir):
    monkeypatch.setattr(telemetry, "DEFAULT_HOME_DIR", str(Path().absolute()))
    monkeypatch.setattr(telemetry, "internal", telemetry.Internal())

    (stat_enabled, uid, is_install) = telemetry._get_telemetry_info(
        "ploomber", "0.14.0"
    )
    assert stat_enabled is True
    assert isinstance(uid, str)
    assert is_install is True


def test_python_version():
    version = system_info.python_version()
    assert isinstance(version, str)


def test_validate_entries(monkeypatch):
    event_id = "event_id"
    uid = "uid"
    action = "action"
    client_time = "client_time"
    elapsed_time = "elapsed_time"
    res = telemetry.validate_entries(event_id, uid, action, client_time, elapsed_time)
    assert res == (event_id, uid, action, client_time, elapsed_time)


def test_conf_file_after_version_check(tmp_directory, monkeypatch):
    version_path = Path("stats") / "uid.yaml"
    write_to_conf_file(
        tmp_directory=tmp_directory,
        monkeypatch=monkeypatch,
        last_check="2022-01-20 10:51:41.082376",
    )
    uid_content = version_path.read_text()
    uid_content += "uid: some_user_id\n"
    version_path.write_text(uid_content)

    # Test that conf file has all required fields
    telemetry.check_version("ploomber", "0.14.0")
    with version_path.open("r") as file:
        conf = yaml.safe_load(file)

    assert set(conf.keys()) == {
        "first_time",
        "last_cloud_check",
        "last_version_check",
        "uid",
    }


def test_get_version_timeout():
    # Check the total run time is less than 1.5 secs
    start_time = datetime.datetime.now()
    telemetry.get_latest_version("ploomber", "0.14.0")
    end_time = datetime.datetime.now()
    total_runtime = end_time - start_time
    assert total_runtime < datetime.timedelta(milliseconds=1500)


def write_to_conf_file(tmp_directory, monkeypatch, last_check, last_cloud_check=None):
    stats = Path("stats")
    stats.mkdir()
    conf_path = stats / "config.yaml"
    version_path = stats / "uid.yaml"
    monkeypatch.setattr(telemetry, "DEFAULT_HOME_DIR", str(Path().absolute()))
    conf_path.write_text("version_check_enabled: True\n")
    version_path.write_text(f"last_version_check: {last_check}\n")

    if last_cloud_check:
        version_path.write_text(f"last_cloud_check: {last_cloud_check}\n")

    # force to reset data so we load from the data we just wrote
    monkeypatch.setattr(telemetry, "internal", telemetry.Internal())


def test_version_skips_when_updated(tmp_directory, capsys, monkeypatch):
    # Path conf file
    mock_version = Mock()
    mock_version.return_value = "0.14.8"
    monkeypatch.setattr(telemetry, "get_latest_version", mock_version)

    write_to_conf_file(
        tmp_directory=tmp_directory,
        monkeypatch=monkeypatch,
        last_check="2022-01-20 10:51:41.082376",
    )  # version='0.14.8',

    # Test no warning when same version encountered
    telemetry.check_version("ploomber", "0.14.8")
    captured = capsys.readouterr()
    print(captured.out)
    assert "ploomber version" not in captured.out


def test_user_output_on_different_versions(tmp_directory, capsys, monkeypatch):
    mock_version = Mock()
    monkeypatch.setattr(telemetry, "get_latest_version", mock_version)
    write_to_conf_file(
        tmp_directory=tmp_directory,
        monkeypatch=monkeypatch,
        last_check="2022-01-20 10:51:41.082376",
    )
    mock_version.return_value = "0.14.0"

    # Check now that the date is different there is an upgrade warning
    telemetry.check_version("ploomber", "0.14.1")
    captured = capsys.readouterr()
    assert "ploomber version" in captured.out


def test_no_output_latest_version(tmp_directory, capsys, monkeypatch):
    # The file's date is today now, no output should be displayed
    write_to_conf_file(
        tmp_directory=tmp_directory,
        monkeypatch=monkeypatch,
        last_check=datetime.datetime.now(),
    )

    telemetry.check_version("ploomber", "0.14.0")
    captured = capsys.readouterr()
    assert "ploomber version" not in captured.out


def test_output_on_date_diff(tmp_directory, capsys, monkeypatch):
    # Warning should be caught since the date and version are off
    mock_version = Mock()
    monkeypatch.setattr(telemetry, "get_latest_version", mock_version)
    write_to_conf_file(
        tmp_directory=tmp_directory,
        monkeypatch=monkeypatch,
        last_check="2022-01-20 10:51:41.082376",
    )

    version_path = Path("stats") / "uid.yaml"
    telemetry.check_version("ploomber", "0.14.0")
    captured = capsys.readouterr()
    assert "ploomber version" in captured.out

    # Check the conf file was updated
    with version_path.open("r") as file:
        version = yaml.safe_load(file)
    diff = (datetime.datetime.now() - version["last_version_check"]).days
    assert diff == 0


def test_python_major_version():
    version = system_info.python_version()
    major = version.split(".")[0]
    assert int(major) == 3


def test_no_output_dev_version(capsys):
    telemetry.check_version("ploomber-core", "0.14.0.dev")
    captured = capsys.readouterr()
    assert "" == captured.out


@pytest.fixture
def mock_telemetry(monkeypatch):
    mock = Mock()
    mock_dt = Mock()
    mock_dt.now.side_effect = [1, 2]
    monkeypatch.setattr(telemetry.Telemetry, "log_api", mock)
    monkeypatch.setattr(telemetry.datetime, "datetime", mock_dt)
    monkeypatch.setattr(telemetry.sys, "argv", ["/path/to/bin", "arg"])
    yield mock


def test_log_call_success(mock_telemetry):
    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "0.14.0")

    @_telemetry.log_call("some-action")
    def my_function():
        pass

    my_function()

    mock_telemetry.assert_has_calls(
        [
            call(
                action="some-package-some-action-success",
                total_runtime="1",
                metadata=dict(argv=["bin", "arg"]),
            ),
        ]
    )


def test_log_call_exception(mock_telemetry):
    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "0.14.0")

    @_telemetry.log_call("some-action")
    def my_function():
        raise ValueError("some error")

    with pytest.raises(ValueError):
        my_function()

    mock_telemetry.assert_has_calls(
        [
            call(
                action="some-package-some-action-error",
                total_runtime="1",
                metadata={
                    "type": None,
                    "exception": "some error",
                    "argv": ["bin", "arg"],
                },
            ),
        ]
    )


def test_log_call_logs_type(mock_telemetry):
    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "0.14.0")

    @_telemetry.log_call("some-action")
    def my_function():
        raise BaseException("some error", type_="some-type")

    with pytest.raises(BaseException):
        my_function()

    mock_telemetry.assert_has_calls(
        [
            call(
                action="some-package-some-action-error",
                total_runtime="1",
                metadata={
                    "type": "some-type",
                    "exception": "some error",
                    "argv": ["bin", "arg"],
                },
            ),
        ]
    )


def test_log_call_add_payload_error(mock_telemetry):
    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "0.14.0")

    @_telemetry.log_call("some-action", payload=True)
    def my_function(payload):
        payload["dag"] = "value"
        raise BaseException("some error", type_="some-type")

    with pytest.raises(BaseException):
        my_function()

    mock_telemetry.assert_has_calls(
        [
            call(
                action="some-package-some-action-error",
                total_runtime="1",
                metadata={
                    "type": "some-type",
                    "exception": "some error",
                    "argv": ["bin", "arg"],
                    "dag": "value",
                },
            ),
        ]
    )


def test_log_call_add_payload_success(mock_telemetry):
    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "0.14.0")

    @_telemetry.log_call("some-action", payload=True)
    def my_function(payload):
        payload["dag"] = "value"

    my_function()

    mock_telemetry.assert_has_calls(
        [
            call(
                action="some-package-some-action-success",
                total_runtime="1",
                metadata={
                    "argv": ["bin", "arg"],
                    "dag": "value",
                },
            ),
        ]
    )


def test_log_call_method_with_payload_success(mock_telemetry):
    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "0.14.0")
    telemetry_my_class = _telemetry.create_group("TestClass")

    class TestClass:
        @telemetry_my_class.log_call("some-action", payload=True)
        def my_function(self, payload, x, y):
            payload["sum"] = x + y

    test_class = TestClass()
    test_class.my_function(1, 2)
    mock_telemetry.assert_has_calls(
        [
            call(
                action="some-package-TestClass-some-action-success",
                total_runtime="1",
                metadata={"argv": ["bin", "arg"], "sum": 3},
            ),
        ]
    )


def test_log_call_no_args_method_with_payload_success(mock_telemetry):
    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "0.14.0")
    telemetry_my_class = _telemetry.create_group("TestClass")

    class TestClass:
        @telemetry_my_class.log_call("some-action", payload=True)
        def my_function(self, payload):
            result = "some result"
            payload["log"] = result
            return result

    test_class = TestClass()
    test_class.my_function()

    mock_telemetry.assert_has_calls(
        [
            call(
                action="some-package-TestClass-some-action-success",
                total_runtime="1",
                metadata={"argv": ["bin", "arg"], "log": "some result"},
            ),
        ]
    )


def test_log_call_keyword_args_method_with_payload_success(mock_telemetry):
    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "0.14.0")
    telemetry_my_class = _telemetry.create_group("TestClass")

    class TestClass:
        @telemetry_my_class.log_call("some-action", payload=True)
        def my_function(self, payload, apple=2, banana=4):
            result = "Give me {} apples and {} bananas please".format(apple, banana)
            payload["log"] = result
            return result

    test_class = TestClass()
    result = test_class.my_function(banana=10, apple=5)
    assert result == "Give me 5 apples and 10 bananas please"
    mock_telemetry.assert_has_calls(
        [
            call(
                action="some-package-TestClass-some-action-success",
                total_runtime="1",
                metadata={
                    "argv": ["bin", "arg"],
                    "log": "Give me 5 apples and 10 bananas please",
                },
            ),
        ]
    )


def test_log_call_keyword_only_args_method_with_payload_success(mock_telemetry):
    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "0.14.0")
    telemetry_my_class = _telemetry.create_group("TestClass")

    class TestClass:
        @telemetry_my_class.log_call("some-action", payload=True)
        def my_function(self, payload, users, *, separator):
            users = [user.lower().split() for user in users]
            username = [separator.join(user) for user in users]
            payload["log"] = username
            return username

    test_class = TestClass()
    result = test_class.my_function(["jhonny", "Mr Smith"], separator="_")
    assert result == ["jhonny", "mr_smith"]

    mock_telemetry.assert_has_calls(
        [
            call(
                action="some-package-TestClass-some-action-success",
                total_runtime="1",
                metadata={"argv": ["bin", "arg"], "log": ["jhonny", "mr_smith"]},
            ),
        ]
    )


def test_log_call_keyword_only_positional_args_method_with_payload_success(
    mock_telemetry,
):
    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "0.14.0")
    telemetry_my_class = _telemetry.create_group("TestClass")

    class TestClass:
        @telemetry_my_class.log_call("some-action", payload=True)
        def my_function(self, payload, arg1, *, arg2, arg3):
            result = arg1 + arg2 + arg3
            payload["log"] = result
            return result

    test_class = TestClass()
    result = test_class.my_function("hello", arg2="world", arg3="!")
    assert result == "helloworld!"

    mock_telemetry.assert_has_calls(
        [
            call(
                action="some-package-TestClass-some-action-success",
                total_runtime="1",
                metadata={"argv": ["bin", "arg"], "log": "helloworld!"},
            ),
        ]
    )


def test_log_call_double_asterisk_args_method_with_payload_success(mock_telemetry):
    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "0.14.0")
    telemetry_my_class = _telemetry.create_group("TestClass")

    class TestClass:
        @telemetry_my_class.log_call("some-action", payload=True)
        def my_function(self, payload, **info):
            result = ""
            for key, value in info.items():
                result = result + "{}: {}\n".format(key, value)
            payload["log"] = result
            return result

    test_class = TestClass()
    result = test_class.my_function(name="Eric", age=19)
    assert result == "name: Eric\nage: 19\n"

    mock_telemetry.assert_has_calls(
        [
            call(
                action="some-package-TestClass-some-action-success",
                total_runtime="1",
                metadata={"argv": ["bin", "arg"], "log": "name: Eric\nage: 19\n"},
            ),
        ]
    )


def test_log_call_single_asterisk_args_method_with_payload_success(mock_telemetry):
    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "0.14.0")
    telemetry_my_class = _telemetry.create_group("TestClass")

    class TestClass:
        @telemetry_my_class.log_call("some-action", payload=True)
        def my_function(self, payload, *todo_list):
            result = "I am going to do: " + ", ".join(todo_list)
            payload["log"] = result
            return result

    test_class = TestClass()
    result = test_class.my_function("studying", "cleaning", "resting")
    assert result == "I am going to do: studying, cleaning, resting"

    mock_telemetry.assert_has_calls(
        [
            call(
                action="some-package-TestClass-some-action-success",
                total_runtime="1",
                metadata={
                    "argv": ["bin", "arg"],
                    "log": "I am going to do: studying, cleaning, resting",
                },
            ),
        ]
    )


def test_permissions_error(monkeypatch):
    monkeypatch.setattr(telemetry, "DEFAULT_HOME_DIR", str(Path().absolute()))
    stats = Path("stats")

    if os.path.exists(stats):
        os.chmod(stats, 777)
        shutil.rmtree(stats)

    os.mkdir(stats)
    os.chmod(stats, stat.S_IRUSR)

    statinfo = os.stat(stats)

    is_read_only = statinfo.st_mode == 16640

    if is_read_only:
        internal = telemetry.Internal()
        user = telemetry.UserSettings()
        assert internal._writable_filesystem is False
        assert user._writable_filesystem is False


@pytest.mark.allow_posthog
def test_hides_posthog_log(caplog, monkeypatch):
    def fake_capture(*args, **kwargs):
        log = logging.getLogger("posthog")
        log.error("some error happened")

    monkeypatch.setattr(posthog, "capture", fake_capture)
    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "ploomber", "0.14.0")

    with caplog.at_level(logging.ERROR, logger="posthog"):
        _telemetry.log_api("test_action")

    assert len(caplog.records) == 0


# TODO: test more of the values (I'm adding ANY to many of them)
def test_log_api_stored_values(monkeypatch):
    mock_info = Mock(return_value=(True, "fake-uuid", False))
    mock = Mock()
    monkeypatch.setattr(telemetry.posthog, "capture", mock)
    monkeypatch.setattr(telemetry, "_get_telemetry_info", mock_info)

    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "1.2.2")

    _telemetry.log_api("some-action")

    py_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}."
        f"{sys.version_info.micro}"
    )

    mock.assert_called_once_with(
        distinct_id="fake-uuid",
        event="some-action",
        properties={
            "event_id": ANY,
            "user_id": "fake-uuid",
            "action": "some-action",
            "client_time": ANY,
            "metadata": {},
            "total_runtime": None,
            "python_version": py_version,
            "version": "1.2.2",
            "package_name": "some-package",
            "docker_container": ANY,
            "cloud": ANY,
            "email": ANY,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )


def test_log_call_stored_values(monkeypatch):
    mock_info = Mock(return_value=(True, "fake-uuid", False))
    mock = Mock()
    monkeypatch.setattr(telemetry.posthog, "capture", mock)
    monkeypatch.setattr(telemetry, "_get_telemetry_info", mock_info)
    monkeypatch.setattr(telemetry.sys, "argv", ["/path/to/bin", "arg2", "arg2"])

    _telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "1.2.2")

    @_telemetry.log_call(action="some-action")
    def my_function():
        pass

    my_function()

    py_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}."
        f"{sys.version_info.micro}"
    )

    assert mock.call_args_list == [
        call(
            distinct_id="fake-uuid",
            event="some-package-some-action-success",
            properties={
                "event_id": ANY,
                "user_id": "fake-uuid",
                "action": "some-package-some-action-success",
                "client_time": ANY,
                "metadata": {"argv": ["bin", "arg2", "arg2"]},
                "total_runtime": ANY,
                "python_version": py_version,
                "version": "1.2.2",
                "package_name": "some-package",
                "docker_container": ANY,
                "cloud": ANY,
                "email": None,
                "os": ANY,
                "environment": ANY,
                "telemetry_version": ANY,
            },
        ),
    ]


@pytest.mark.parametrize(
    "argv, expected",
    [
        [
            ["/path/to/bin", "--arg val", "--something"],
            ["bin", "--arg val", "--something"],
        ],
        [["bin"], ["bin"]],
        [None, None],
        [[], None],
        [1, None],
        [object(), None],
    ],
)
def test_get_sanitized_sys_argv(argv, expected, monkeypatch):
    monkeypatch.setattr(telemetry.sys, "argv", argv)
    assert telemetry.get_sanitized_argv() == expected


def test_exposes_telemetry_data_for_testing():
    my_telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "1.2.2")

    @my_telemetry.log_call()
    def my_function():
        pass

    assert my_function._telemetry == {
        "group": None,
        "ignore_args": set(),
        "log_args": False,
        "payload": False,
        "action": "some-package-my-function",
    }

    assert my_function.__wrapped__._telemetry_success is None
    assert my_function.__wrapped__._telemetry_error is None

    my_function()

    assert my_function.__wrapped__._telemetry_success == {
        "action": "some-package-my-function-success",
        "total_runtime": ANY,
        "metadata": {"argv": ANY},
    }

    assert my_function.__wrapped__._telemetry_error is None


def test_exposes_telemetry_data_for_testing_error():
    my_telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "1.2.2")

    @my_telemetry.log_call()
    def my_function():
        raise ValueError("some error")

    assert my_function._telemetry == {
        "group": None,
        "ignore_args": set(),
        "log_args": False,
        "payload": False,
        "action": "some-package-my-function",
    }

    assert my_function.__wrapped__._telemetry_success is None
    assert my_function.__wrapped__._telemetry_error is None

    try:
        my_function()
    except ValueError:
        pass

    assert my_function.__wrapped__._telemetry_success is None

    assert my_function.__wrapped__._telemetry_error == {
        "action": "some-package-my-function-error",
        "total_runtime": ANY,
        "metadata": {
            "type": None,
            "exception": "some error",
            "argv": ANY,
        },
    }


def test_exposes_telemetry_data_for_testing_params():
    my_telemetry = telemetry.Telemetry(MOCK_API_KEY, "some-package", "1.2.2")

    @my_telemetry.log_call(log_args=("x", "y"), ignore_args=("z",))
    def my_function(x, y, z):
        return x + y + z

    assert my_function._telemetry == {
        "action": "some-package-my-function",
        "payload": False,
        "log_args": ("x", "y"),
        "ignore_args": {"z"},
        "group": None,
    }

    assert my_function.__wrapped__._telemetry_success is None
    assert my_function.__wrapped__._telemetry_error is None

    my_function(1, 2, 3)

    assert my_function.__wrapped__._telemetry_success == {
        "action": "some-package-my-function-success",
        "total_runtime": ANY,
        "metadata": {
            "argv": ANY,
            "args": {"x": 1, "y": 2},
        },
    }

    assert my_function.__wrapped__._telemetry_error is None


@pytest.mark.parametrize(
    "last_cloud_check",
    [
        None,
        "2022-01-20 10:51:41.082376",
    ],
    ids=[
        "first-time",
        "not-first-time",
    ],
)
def test_check_cloud(tmp_directory, monkeypatch, capsys, last_cloud_check):
    write_to_conf_file(
        tmp_directory=tmp_directory,
        monkeypatch=monkeypatch,
        last_check="2022-01-20 10:51:41.082376",
        last_cloud_check=last_cloud_check,
    )

    now = datetime.datetime.now()
    fake_datetime = Mock()
    fake_datetime.now.return_value = now

    with monkeypatch.context() as m:
        m.setattr(telemetry.datetime, "datetime", fake_datetime)
        telemetry.check_cloud()

    config = yaml.safe_load(Path("stats", "uid.yaml").read_text())

    captured = capsys.readouterr()

    expected = (
        "Deploy AI and data apps for free on Ploomber Cloud!"
        " Learn more: https://docs.cloud.ploomber.io/en/latest/quickstart/signup.html"
    )

    assert expected in captured.out
    assert config["last_cloud_check"] == now
