import warnings
import abc
from collections.abc import Mapping
from pathlib import Path
import yaml
import random
import string
from contextlib import contextmanager


@contextmanager
def set_write_attr_changes(obj, value):
    """Context manager to ensure that _write_attr_changes is set to True after the
    operation
    """
    obj._write_attr_changes = value
    yield
    obj._write_attr_changes = True


class Config(abc.ABC):
    """An abstract class to create configuration files (stored as YAML)

    Notes
    -----
    For examples, see test_config.py or the concrete classes
    (UserSettings, Internal)
    """

    def __init__(self):
        self._write_attr_changes = True
        self._writable_filesystem = self._filesystem_writable()
        self._init_values()

        # resolve home directory
        path = self.path()

        if self._writable_filesystem and not path.exists():
            defaults = self._get_annotation_values()
            path.write_text(yaml.dump(defaults))
        else:
            try:
                content = self._load_from_file()
                loaded_from_file = True
            except Exception as e:
                warnings.warn(
                    f"Error loading {str(path)!r}: {e}\n\n"
                    "reverting to default values"
                )
                loaded_from_file = False
                content = self._get_annotation_values()

            if loaded_from_file and not isinstance(content, Mapping):
                warnings.warn(
                    f"Error loading {str(path)!r}. Expected a dictionary "
                    f"but got {type(content).__name__}, "
                    "reverting to default values"
                )
                content = self._get_annotation_values()

            # if we loaded from file, we don't need to write the changes, since
            # we'd be overwriting the file with the same content
            with set_write_attr_changes(self, not loaded_from_file):
                self._set_data(content)

    def _load_from_file(self):
        path = self.path()
        config = self.load_config()

        if config:
            content = config
        else:
            # this might happen if using multiprocessing: the first process
            # won't see the file so it'll proceed writing it, but upcoming
            # processes might see an empty file (file has been created but
            # writing hasn't finished). In such case, text will be None. If
            # so, we simply load the default values
            content = self._get_annotation_values()

        for key, type_ in self.__annotations__.items():
            value = content.get(key, None)

            if value is not None and not isinstance(value, type_):
                default = getattr(self, key)
                warnings.warn(
                    f"Corrupted config file {str(path)!r}: "
                    f"expected {key!r} to contain an object "
                    f"with type {type_.__name__}, but got "
                    f"{type(value).__name__}. Reverting to "
                    f"default value {default}"
                )
                content[key] = default

        return content

    def _get_annotation_values(self):
        """Extract values from the annotations and return a dictionary"""
        return {key: getattr(self, key) for key in self.__annotations__}

    def _set_data(self, data):
        """Take a dictionary and store it in the annotations"""
        for key in self.__annotations__:
            if key in data:
                setattr(self, key, data[key])

    def _init_values(self):
        """
        Iterate over annotations to initialize values. This is only relevant
        when any of the annotations has a factory method to initialize the
        values. If they value is a literal, no changes happen.
        """
        for key in self.__annotations__:
            name = f"{key}_default"

            # if there is a method with such name, call it and store the output
            if hasattr(self, name):
                value = getattr(self, name)()
                # call __setattr__ on the superclass so we skip the part
                # where we overwrite the YAML file, here we only want to
                # set the default values
                super().__setattr__(key, value)

    def _write(self):
        """Writes data to the YAML file"""
        data = self._get_annotation_values()
        self.path().parent.mkdir(parents=True, exist_ok=True)
        self.path().write_text(yaml.dump(data))

    def __setattr__(self, name, value):
        is_private_attribute = name.startswith("_")

        if not is_private_attribute and name not in self.__annotations__:
            raise ValueError(f"{name} not a valid field")
        else:
            super().__setattr__(name, value)

            if is_private_attribute:
                return

            # Check if the filesystem is writable
            if self._write_attr_changes and self._writable_filesystem:
                self._write()

    def load_config(self):
        config = None

        if self._writable_filesystem:
            path = self.path()
            is_config_exist = Path.is_file(path)
            if is_config_exist:
                text = path.read_text()
                if text:
                    config = yaml.safe_load(text)

        return config

    def _filesystem_writable(self):
        """Check if the filesystem is writable"""

        seq = f"{string.ascii_uppercase}{string.digits}"
        # random string is used for race conditions when using multiprocessing
        random_str = "".join(random.choices(seq, k=10))

        tmp = self.path().parent / f"tmp_{random_str}.txt"

        # Checking whether we can create a dir
        try:
            tmp.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            return False

        # Checking whether we can create a file (most probably redundant)
        try:
            tmp.touch()
        except PermissionError:
            return False
        else:
            tmp.unlink()

        return True

    @abc.abstractclassmethod
    def path(cls):
        """Returns the path to the YAML file"""
        pass
