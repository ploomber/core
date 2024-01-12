from ploomber_core.telemetry.system_info import get_system_info


def test_get_system_info():
    assert set(get_system_info()) == {
        "env",
        "is_airflow",
        "is_argo",
        "is_colab",
        "is_docker",
        "is_paperspace",
        "is_slurm",
        "os",
        "python_version",
    }
