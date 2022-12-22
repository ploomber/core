import pytest

from ploomber_core.dependencies import requires


@pytest.mark.parametrize(
    "params, expected",
    [
        [
            dict(pkgs=["p1"]),
            "'p1' is required to use 'fn'. Install with: pip install 'p1'",
        ],
        [
            dict(pkgs=["p1"], name="name"),
            ("'p1' is required to use 'name'. Install with: " "pip install 'p1'"),
        ],
        [
            dict(pkgs=["p1"], extra_msg="Some extra message"),
            (
                "'p1' is required to use 'fn'. Install with: "
                "pip install 'p1'\nSome extra message"
            ),
        ],
        [
            dict(pkgs=["p1", "p2"]),
            (
                "'p1' 'p2' are required to use 'fn'. Install with: "
                "pip install 'p1' 'p2'"
            ),
        ],
        [
            dict(pkgs=["p1"], pip_names=["n1"]),
            "'n1' is required to use 'fn'. Install with: pip install 'n1'",
        ],
        [
            # pinning some specific version (this may happen if user is
            # running and old python version)
            dict(pkgs=["p1"], pip_names=["n1<2"]),
            "'n1<2' is required to use 'fn'. Install with: pip install 'n1<2'",
        ],
        [
            # the first package is installed, it shouldn't appear in the error
            dict(pkgs=["ploomber_core", "p1"]),
            "'p1' is required to use 'fn'. Install with: pip install 'p1'",
        ],
        [
            # same as before, but it should replace "-", with "_"
            dict(pkgs=["ploomber-core", "p1"]),
            "'p1' is required to use 'fn'. Install with: pip install 'p1'",
        ],
    ],
)
def test_requires(params, expected):
    @requires(**params)
    def fn():
        pass

    with pytest.raises(ImportError) as excinfo:
        fn()

    assert str(excinfo.value) == expected
