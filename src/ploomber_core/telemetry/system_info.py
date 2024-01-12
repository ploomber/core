import os
from pathlib import Path
import platform
import sys


try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata


def python_version():
    py_version = sys.version_info
    return f"{py_version.major}.{py_version.minor}.{py_version.micro}"


def is_docker():
    """Will output if the code is within a container"""
    try:
        cgroup = Path("/proc/self/cgroup")
        docker_env = Path("/.dockerenv")
        return (
            docker_env.exists()
            or cgroup.exists()
            and any("docker" in line for line in cgroup.read_text().splitlines())
        )
    except OSError:
        return False


def get_os():
    """
    The function will output the client platform
    """
    os = platform.system()
    if os == "Darwin":
        return "MacOS"
    else:  # Windows/Linux are contained
        return os


def is_conda():
    """
    The function will tell if the code is running in a conda env
    """
    conda_path = Path(sys.prefix, "conda-meta")
    return (
        conda_path.exists()
        or os.environ.get("CONDA_PREFIX", False)
        or os.environ.get("CONDA_DEFAULT_ENV", False)
    )


def get_base_prefix_compat():
    """
    This function will find the pip virtualenv with different python versions.
    Get base/real prefix, or sys.prefix if there is none.
    """
    return (
        getattr(sys, "base_prefix", None)
        or sys.prefix
        or getattr(sys, "real_prefix", None)
    )


def in_virtualenv():
    return get_base_prefix_compat() != sys.prefix


def get_env():
    """Returns: The name of the virtual env if exists as str"""
    if in_virtualenv():
        return "pip"
    elif is_conda():
        return "conda"
    else:
        return "local"


def is_colab():
    """Returns: True for Google Colab env"""
    try:
        import google.colab  # noqa

        in_colab = True
    except ModuleNotFoundError:
        in_colab = False
    finally:
        return in_colab


def is_paperspace():
    """Returns: True for Paperspace env"""
    return (
        "PS_API_KEY" in os.environ
        or "PAPERSPACE_API_KEY" in os.environ
        or "PAPERSPACE_NOTEBOOK_REPO_ID" in os.environ
    )


def is_slurm():
    """Returns: True for Slurm env"""
    return "SLURM_JOB_ID" in os.environ


def is_airflow():
    """Returns: True for Airflow env"""
    return "AIRFLOW_CONFIG" in os.environ or "AIRFLOW_HOME" in os.environ


def is_argo():
    """Returns: True for Argo env"""
    return "ARGO_AGENT_TASK_WORKERS" in os.environ or "ARGO_KUBELET_PORT" in os.environ


def safe_call(function):
    try:
        return function()
    except Exception:
        return None


def get_package_version(package_name):
    try:
        return importlib_metadata.version(package_name)
    except importlib_metadata.PackageNotFoundError:
        return None


def get_system_info():
    return {
        "os": safe_call(get_os),
        "python_version": safe_call(python_version),
        "env": safe_call(get_env),
        "is_docker": safe_call(is_docker),
        "is_colab": safe_call(is_colab),
        "is_paperspace": safe_call(is_paperspace),
        "is_slurm": safe_call(is_slurm),
        "is_airflow": safe_call(is_airflow),
        "is_argo": safe_call(is_argo),
    }
