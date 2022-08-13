import pathlib
import sys
from unittest.mock import Mock, call
from pathlib import Path
import datetime
import logging
import os

import pytest
import yaml
import posthog

from ploomber_core.telemetry import telemetry
from ploomber_core.telemetry.validate_inputs import str_param, opt_str_param

from ploomber_core.exceptions import BaseException

MOCK_API_KEY = 'phc_P1dsjk20bijsabdaib2eu'


@pytest.fixture()
def inside_conda_env(monkeypatch):
    monkeypatch.setenv('CONDA_PREFIX', True)


@pytest.fixture()
def inside_pip_env(monkeypatch):
    monkeypatch.setattr(telemetry.sys, 'prefix', 'sys.prefix')
    monkeypatch.setattr(telemetry.sys, 'base_prefix', 'base_prefix')


@pytest.fixture
def ignore_ploomber_stats_enabled_env_var(monkeypatch):
    """
    GitHub Actions configuration scripts set the PLOOMBER_STATS_ENABLED
    environment variable to prevent CI events from going to posthog, this
    inferes with some tests. This fixture removes its value temporarily.

    GitHub actions also sets CI
    """
    if 'PLOOMBER_STATS_ENABLED' in os.environ:
        monkeypatch.delenv('PLOOMBER_STATS_ENABLED', raising=True)

    if 'CI' in os.environ:
        monkeypatch.delenv('CI', raising=True)


@pytest.fixture
def ignore_env_var_and_set_tmp_default_home_dir(
        tmp_directory, ignore_ploomber_stats_enabled_env_var, monkeypatch):
    """
    ignore_ploomber_stats_enabled_env_var + overrides DEFAULT_HOME_DIR
    to prevent the local configuration to interfere with tests
    """
    monkeypatch.setattr(telemetry, 'DEFAULT_HOME_DIR', '.')


def test_user_settings_create_file(tmp_directory, monkeypatch):
    monkeypatch.setattr(telemetry, 'DEFAULT_HOME_DIR', '.')

    settings = telemetry.UserSettings()
    content = yaml.safe_load(Path('stats', 'config.yaml').read_text())

    assert content == {
        'cloud_key': None,
        'user_email': None,
        'stats_enabled': True,
        'version_check_enabled': True,
    }
    assert settings.cloud_key is None
    assert settings.stats_enabled


def test_internal_create_file(tmp_directory, monkeypatch):
    monkeypatch.setattr(telemetry, 'DEFAULT_HOME_DIR', '.')
    monkeypatch.setattr(telemetry, 'uuid4', lambda: 'some-unique-uuid')

    internal = telemetry.Internal()
    content = yaml.safe_load(Path('stats', 'uid.yaml').read_text())

    assert content == {
        'uid': 'some-unique-uuid',
        'last_version_check': None,
        'first_time': True
    }
    assert internal.uid == 'some-unique-uuid'
    assert internal.last_version_check is None


def test_does_not_overwrite_existing_uid(tmp_directory, monkeypatch):
    monkeypatch.setattr(telemetry, 'DEFAULT_HOME_DIR', '.')

    Path('stats').mkdir()
    Path('stats', 'uid.yaml').write_text(yaml.dump({'uid': 'existing-uid'}))

    internal = telemetry.Internal()

    assert internal.uid == 'existing-uid'


# Validations tests
def test_str_validation():
    res = str_param("Test", "")
    assert isinstance(res, str)
    res = str_param("TEST", "test_param")
    assert 'TEST' == res
    with pytest.raises(TypeError) as exc_info:
        str_param(3, "Test_number")

    exception_raised = exc_info.value
    assert type(exception_raised) == TypeError


def test_opt_str_validation():
    res = opt_str_param("Test", "")
    assert isinstance(res, str)
    res = opt_str_param("Test", "TEST")
    assert 'TEST' == res
    res = opt_str_param("Test", None)
    assert not res

    with pytest.raises(TypeError) as exc_info:
        opt_str_param("Test", 3)

    exception_raised = exc_info.value
    assert type(exception_raised) == TypeError


def test_check_stats_enabled(ignore_env_var_and_set_tmp_default_home_dir):
    stats_enabled = telemetry.check_telemetry_enabled()
    assert stats_enabled is True


def test_disable_stats_if_ci_env(ignore_env_var_and_set_tmp_default_home_dir,
                                 monkeypatch):
    monkeypatch.setenv('CI', 'true')
    stats_enabled = telemetry.check_telemetry_enabled()
    assert stats_enabled is False


@pytest.mark.parametrize(
    'yaml_value, expected_first, env_value, expected_second', [
        ['true', True, 'false', False],
        ['TRUE', True, 'FALSE', False],
        ['false', False, 'true', True],
        ['FALSE', False, 'TRUE', True],
    ])
def test_env_var_takes_precedence(monkeypatch,
                                  ignore_env_var_and_set_tmp_default_home_dir,
                                  yaml_value, expected_first, env_value,
                                  expected_second):

    stats = Path('stats')
    stats.mkdir()

    (stats / 'config.yaml').write_text(f"""
                                        stats_enabled: {yaml_value}
                                        """)

    assert telemetry.check_telemetry_enabled() is expected_first

    monkeypatch.setenv('PLOOMBER_STATS_ENABLED', env_value, prepend=False)

    assert telemetry.check_telemetry_enabled() is expected_second


def test_first_usage(monkeypatch, tmp_directory):
    monkeypatch.setattr(telemetry, 'DEFAULT_HOME_DIR', '.')

    assert telemetry.check_first_time_usage()
    assert not telemetry.check_first_time_usage()


# The below fixtures are to mock the different virtual environments
# Ref: https://stackoverflow.com/questions/51266880/detect-if-
# python-is-running-in-a-conda-environment
def test_conda_env(monkeypatch, inside_conda_env, tmp_directory):
    # Set a conda parameterized env
    env = telemetry.is_conda()
    assert bool(env) is True
    env = telemetry.get_env()
    assert env == 'conda'


# Ref: https://stackoverflow.com/questions/1871549/
# determine-if-python-is-running-inside-virtualenv
def test_pip_env(monkeypatch, inside_pip_env):
    # Set a pip parameterized env
    env = telemetry.in_virtualenv()
    assert env is True
    env = telemetry.get_env()
    assert env == 'pip'


# Ref: https://stackoverflow.com/questions/43878953/how-does-one-detect-if-
# one-is-running-within-a-docker-container-within-python
def test_docker_env(monkeypatch):

    def mock(input_path):
        return 'dockerenv' in str(input_path)

    monkeypatch.setattr(pathlib.Path, 'exists', mock)
    docker = telemetry.is_docker()
    assert docker is True


# Ref https://stackoverflow.com/questions/53581278/test-if-
# notebook-is-running-on-google-colab
def test_colab_env(monkeypatch):
    monkeypatch.setenv('COLAB_GPU', True)
    colab = telemetry.is_colab()
    assert colab is True


# Ref https://learn.paperspace.com/video/creating-a-jupyter-notebook
@pytest.mark.parametrize(
    'env_variable',
    ['PS_API_KEY', 'PAPERSPACE_API_KEY', 'PAPERSPACE_NOTEBOOK_REPO_ID'])
def test_paperspace_env(monkeypatch, env_variable):
    monkeypatch.setenv(env_variable, True)
    pspace = telemetry.is_paperspace()
    assert pspace is True


# Ref https://stackoverflow.com/questions/63298054/how-to-check-if-my-code
# -runs-inside-a-slurm-environment
def test_slurm_env(monkeypatch):
    monkeypatch.setenv('SLURM_JOB_ID', True)
    slurm = telemetry.is_slurm()
    assert slurm is True


# Ref https://airflow.apache.org/docs/apache-airflow/stable/
# cli-and-env-variables-ref.html?highlight=airflow_home#envvar-AIRFLOW_HOME
@pytest.mark.parametrize('env_variable', ['AIRFLOW_CONFIG', 'AIRFLOW_HOME'])
def test_airflow_env(monkeypatch, env_variable):
    monkeypatch.setenv(env_variable, True)
    airflow = telemetry.is_airflow()
    assert airflow is True


# Ref https://stackoverflow.com/questions/110362/how-can-i-find-
# the-current-os-in-python
@pytest.mark.parametrize('os_param', ['Windows', 'Linux', 'MacOS', 'Ubuntu'])
def test_os_type(monkeypatch, os_param):
    mock = Mock()
    mock.return_value = os_param
    monkeypatch.setattr(telemetry.platform, 'system', mock)
    os_type = telemetry.get_os()
    assert os_type == os_param


def test_full_telemetry_info(ignore_env_var_and_set_tmp_default_home_dir):
    (stat_enabled, uid, is_install) = \
        telemetry._get_telemetry_info('ploomber', '0.14.0')
    assert stat_enabled is True
    assert isinstance(uid, str)
    assert is_install is True


def test_basedir_creation():
    base_dir = telemetry.check_dir_exist()
    assert base_dir.exists()


def test_python_version():
    version = telemetry.python_version()
    assert isinstance(version, str)


def test_is_online():
    assert telemetry.is_online()


def test_is_online_timeout():
    # Check the total run time is less than 1.5 secs
    start_time = datetime.datetime.now()
    telemetry.is_online()
    end_time = datetime.datetime.now()
    total_runtime = end_time - start_time
    assert total_runtime < datetime.timedelta(milliseconds=1500)


def test_stats_off(monkeypatch):
    mock = Mock()
    posthog_mock = Mock()
    mock.patch(telemetry, '_get_telemetry_info', (False, 'TestUID'))

    _telemetry = telemetry.Telemetry('ploomber', '0.14.0', MOCK_API_KEY)
    _telemetry.log_api("test_action")

    assert posthog_mock.call_count == 0


def test_offline_stats(monkeypatch):
    mock = Mock()
    posthog_mock = Mock()
    mock.patch(telemetry, 'is_online', False)

    _telemetry = telemetry.Telemetry('ploomber', '0.14.0', MOCK_API_KEY)
    _telemetry.log_api("test_action")

    assert posthog_mock.call_count == 0


def test_is_not_online(monkeypatch):
    mock_httplib = Mock()
    mock_httplib.HTTPSConnection().request.side_effect = Exception
    monkeypatch.setattr(telemetry, 'httplib', mock_httplib)

    assert not telemetry.is_online()


def test_validate_entries(monkeypatch):
    event_id = 'event_id'
    uid = 'uid'
    action = 'action'
    client_time = 'client_time'
    elapsed_time = 'elapsed_time'
    res = telemetry.validate_entries(event_id, uid, action, client_time,
                                     elapsed_time)
    assert res == (event_id, uid, action, client_time, elapsed_time)


def test_conf_file_after_version_check(tmp_directory, monkeypatch):
    version_path = Path('stats') / 'uid.yaml'
    write_to_conf_file(tmp_directory=tmp_directory,
                       monkeypatch=monkeypatch,
                       last_check='2022-01-20 10:51:41.082376')
    uid_content = version_path.read_text()
    uid_content += 'uid: some_user_id\n'
    version_path.write_text(uid_content)

    # Test that conf file has all required fields
    telemetry.check_version('ploomber', '0.14.0')
    with version_path.open("r") as file:
        conf = yaml.safe_load(file)
    assert 'uid' in conf.keys()
    assert len(conf.keys()) == 3


def test_get_version_timeout():
    # Check the total run time is less than 1.5 secs
    start_time = datetime.datetime.now()
    telemetry.get_latest_version('ploomber', "0.14.0")
    end_time = datetime.datetime.now()
    total_runtime = end_time - start_time
    assert total_runtime < datetime.timedelta(milliseconds=1500)


def write_to_conf_file(tmp_directory, monkeypatch, last_check):
    stats = Path('stats')
    stats.mkdir()
    conf_path = stats / 'config.yaml'
    version_path = stats / 'uid.yaml'
    monkeypatch.setattr(telemetry, 'DEFAULT_HOME_DIR', '.')
    conf_path.write_text("version_check_enabled: True\n")
    version_path.write_text(f"last_version_check: {last_check}\n")


def test_version_skips_when_updated(tmp_directory, capsys, monkeypatch):
    # Path conf file
    mock_version = Mock()
    mock_version.return_value = '0.14.8'
    monkeypatch.setattr(telemetry, 'get_latest_version', mock_version)

    write_to_conf_file(
        tmp_directory=tmp_directory,
        monkeypatch=monkeypatch,
        last_check='2022-01-20 10:51:41.082376')  # version='0.14.8',

    # Test no warning when same version encountered
    telemetry.check_version('ploomber', "0.14.8")
    captured = capsys.readouterr()
    print(captured.out)
    assert "ploomber version" not in captured.out


def test_user_output_on_different_versions(tmp_directory, capsys, monkeypatch):
    mock_version = Mock()
    monkeypatch.setattr(telemetry, 'get_latest_version', mock_version)
    write_to_conf_file(tmp_directory=tmp_directory,
                       monkeypatch=monkeypatch,
                       last_check='2022-01-20 10:51:41.082376')
    mock_version.return_value = '0.14.0'

    # Check now that the date is different there is an upgrade warning
    telemetry.check_version('ploomber', "0.14.1")
    captured = capsys.readouterr()
    assert "ploomber version" in captured.out


def test_no_output_latest_version(tmp_directory, capsys, monkeypatch):
    # The file's date is today now, no output should be displayed
    write_to_conf_file(tmp_directory=tmp_directory,
                       monkeypatch=monkeypatch,
                       last_check=datetime.datetime.now())

    telemetry.check_version('ploomber', "0.14.0")
    captured = capsys.readouterr()
    assert "ploomber version" not in captured.out


def test_output_on_date_diff(tmp_directory, capsys, monkeypatch):
    # Warning should be caught since the date and version are off
    mock_version = Mock()
    monkeypatch.setattr(telemetry, 'get_latest_version', mock_version)
    write_to_conf_file(tmp_directory=tmp_directory,
                       monkeypatch=monkeypatch,
                       last_check='2022-01-20 10:51:41.082376')
    version_path = Path('stats') / 'uid.yaml'
    telemetry.check_version('ploomber', "0.14.0")
    captured = capsys.readouterr()
    assert "ploomber version" in captured.out

    # Check the conf file was updated
    with version_path.open("r") as file:
        version = yaml.safe_load(file)
    diff = (datetime.datetime.now() - version['last_version_check']).days
    assert diff == 0


def test_python_major_version():
    version = telemetry.python_version()
    major = version.split(".")[0]
    assert int(major) == 3


@pytest.fixture
def mock_telemetry(monkeypatch):
    mock = Mock()
    mock_dt = Mock()
    mock_dt.now.side_effect = [1, 2]
    monkeypatch.setattr(telemetry.Telemetry, 'log_api', mock)
    monkeypatch.setattr(telemetry.datetime, 'datetime', mock_dt)
    yield mock


def test_log_call_success(mock_telemetry):
    _telemetry = telemetry.Telemetry('ploomber', '0.14.0', MOCK_API_KEY)

    @_telemetry.log_call('some-action')
    def my_function():
        pass

    my_function()

    mock_telemetry.assert_has_calls([
        call(action='some-action-started', metadata=dict(argv=sys.argv)),
        call(action='some-action-success',
             total_runtime='1',
             metadata=dict(argv=sys.argv)),
    ])


def test_log_call_exception(mock_telemetry):
    _telemetry = telemetry.Telemetry('ploomber', '0.14.0', MOCK_API_KEY)

    @_telemetry.log_call('some-action')
    def my_function():
        raise ValueError('some error')

    with pytest.raises(ValueError):
        my_function()

    mock_telemetry.assert_has_calls([
        call(action='some-action-started', metadata=dict(argv=sys.argv)),
        call(action='some-action-error',
             total_runtime='1',
             metadata={
                 'type': None,
                 'exception': 'some error',
                 'argv': sys.argv,
             })
    ])


def test_log_call_logs_type(mock_telemetry):
    _telemetry = telemetry.Telemetry('ploomber', '0.14.0', MOCK_API_KEY)

    @_telemetry.log_call('some-action')
    def my_function():
        raise BaseException('some error', type_='some-type')

    with pytest.raises(BaseException):
        my_function()

    mock_telemetry.assert_has_calls([
        call(action='some-action-started', metadata=dict(argv=sys.argv)),
        call(action='some-action-error',
             total_runtime='1',
             metadata={
                 'type': 'some-type',
                 'exception': 'some error',
                 'argv': sys.argv,
             })
    ])


def test_log_call_add_payload_error(mock_telemetry):
    _telemetry = telemetry.Telemetry('ploomber', '0.14.0', MOCK_API_KEY)

    @_telemetry.log_call('some-action', payload=True)
    def my_function(payload):
        payload['dag'] = 'value'
        raise BaseException('some error', type_='some-type')

    with pytest.raises(BaseException):
        my_function()

    mock_telemetry.assert_has_calls([
        call(action='some-action-started', metadata=dict(argv=sys.argv)),
        call(action='some-action-error',
             total_runtime='1',
             metadata={
                 'type': 'some-type',
                 'exception': 'some error',
                 'argv': sys.argv,
                 'dag': 'value',
             })
    ])


def test_log_call_add_payload_success(mock_telemetry):
    _telemetry = telemetry.Telemetry('ploomber', '0.14.0', MOCK_API_KEY)

    @_telemetry.log_call('some-action', payload=True)
    def my_function(payload):
        payload['dag'] = 'value'

    my_function()

    mock_telemetry.assert_has_calls([
        call(action='some-action-started', metadata=dict(argv=sys.argv)),
        call(action='some-action-success',
             total_runtime='1',
             metadata={
                 'argv': sys.argv,
                 'dag': 'value',
             })
    ])


@pytest.mark.allow_posthog
def test_hides_posthog_log(caplog, monkeypatch):

    def fake_capture(*args, **kwargs):
        log = logging.getLogger("posthog")
        log.error('some error happened')

    monkeypatch.setattr(posthog, 'capture', fake_capture)
    _telemetry = telemetry.Telemetry('ploomber', '0.14.0', MOCK_API_KEY)

    with caplog.at_level(logging.ERROR, logger="posthog"):
        _telemetry.log_api("test_action")

    assert len(caplog.records) == 0
