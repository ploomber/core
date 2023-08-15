# CHANGELOG

## 0.2.14 (2023-08-15)

* [Fix] Fix error when using `@modify_exceptions` in an exception initialized without arguments
* [Fix] Reduced telemetry latency by removing `is_online` call
* [Fix] Skip file write operations in config files if not needed
* [Fix] `_PLOOMBER_TELEMETRY_DEBUG` environment variable is independent of the `PLOOMBER_STATS_ENABLED` environment variable

## 0.2.13 (2023-06-27)

* [Fix] Fixed support for readonly file systems in telemetry ([#63](https://github.com/ploomber/core/issues/63))
* [Fix] Better validation when checking version updates ([#66](https://github.com/ploomber/core/issues/66))

## 0.2.12 (2023-06-06)

* [Feature] Adds `ploomber_core.warnings.deprecation_warning` ([#65](https://github.com/ploomber/core/issues/65))

## 0.2.11 (2023-05-25)

* [Fix] Fix `check_installed` so it behaves consistently with `@requires` regarding package names

## 0.2.10 (2023-04-24)

* [Feature] `modify_exceptions` decorator modifies exceptions if they have a `modify_exception` attribute equal to `True`

## 0.2.9 (2023-03-29)

* [Fix] Do not check if there's internet connection when stats are disabled ([#55](https://github.com/ploomber/core/issues/55))

## 0.2.8 (2023-03-27)

* [Fix] Adds LICENSE information to `setup.py`

## 0.2.7 (2023-03-22)

* [Feature] Adds `ploomber_core.dependencies.check_installed` to check if packages are installed

## 0.2.6 (2023-02-16)

* [Feature] Adds `ploomber_core.validate` to validate function values

## 0.2.5 (2023-02-14)

* [Feature] Functions decorated with `[@log_call](https://github.com/log_call)` expose an attribute for unit testing

## 0.2.4 (2023-02-14)

* [Fix] Fixes `[@log_call](https://github.com/log_call)` with `payload=True` when decorating methods

## 0.2.3 (2023-02-01)

* [Fix] Improving `modify_exceptions` to include TypeError
* [Fix] Deduplicating community message on nested functions

## 0.2.2 (2023-01-31)

* [Fix] Telemetry: Sets version to `0.5`
* [Fix] Telemetry: Normalizing event names (replacing `_` with `-`)

## 0.2.1

*There was not `0.2.1` due to an error in the deployment script.*

## 0.2.0 (2023-01-13)

* [API Change] Refactors some functions in the `deprecated` module.

## 0.1.2 (2023-01-11)

* Setting the `_PLOOMBER_TELEMETRY_DEBUG` environment variable overrides the PostHog key to log events in the "Debugging" project.

## 0.1.1 (2023-01-05)

* Adds `exceptions.modify_exceptions` decorator

## 0.1 (2022-12-29)

* Makes `PloomberDeprecationWarning` a subclass of `FutureWarning`
* Adds more features to the `deprecated` module
* Adds new exceptions to the `exceptions` module

## 0.0.14 (2022-12-28)

* Bumps up telemetry version to version `0.4` (the schema changed happened in version `0.0.12` but we forgot to update it)

## 0.0.13 (2022-12-23)

* Truncating long lists in the telemetry module

## 0.0.12 (2022-12-23)

* Improves telemetry module to allow logging selected function calling params

## 0.0.11 (2022-12-22)

* Adds `ploomber_core.dependencies.requires`

## 0.0.10 (2022-12-09)

* Changing telemetry exception type

## 0.0.9 (2022-12-09)

* Fixing issue of crashing telemetry when dir is read only

## 0.0.8 (2022-11-25)

* Fixes telemetry duplicated events ([#19](https://github.com/ploomber/core/issues/19))

## 0.0.7 (2022-11-01)

* Fixes race condition when loading and writing config file ([#12](https://github.com/ploomber/core/issues/12))
* Fixes check for Colab

## 0.0.6 (2022-08-23)

* Fixing telemetry logging of `package_name` and `version`
* Sanitizing `sys.argv` in telemetry module

## 0.0.5 (2022-08-21)

* Adds `[@deprecated](https://github.com/deprecated).method`

## 0.0.4 (2022-08-13)

* Disable telemetry call if `READTHEDOCS` environment variable is set

## 0.0.3 (2022-08-13)

* Disable telemetry call if `CI` environment variable is set (to ignore [GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/environment-variables#default-environment-variables))

## 0.0.2 (2022-08-01)

* Support for multiple telemetry keys

## 0.0.1

* First release
