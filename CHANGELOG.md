# CHANGELOG

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
* Adds `@deprecated.method`

## 0.0.4 (2022-08-13)
* Disable telemetry call if `READTHEDOCS` environment variable is set

## 0.0.3 (2022-08-13)
* Disable telemetry call if `CI` environment variable is set (to ignore [GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/environment-variables#default-environment-variables))

## 0.0.2 (2022-08-01)
* Support for multiple telemetry keys
## 0.0.1
* First release
