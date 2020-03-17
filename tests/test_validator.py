import pytest as pt
import updatemyip.validator as validator


@pt.mark.parametrize(
    "value, result",
    [
        ["127.0.0.1", True],
        ["test", False]
    ]
)
def test_ip_address(value, result):
    assert validator.ip_address(value) == result


@pt.mark.parametrize(
    "value, result",
    [
        ["127.0.0.1", True],
        ["1.1.1.1", False]
    ]
)
def test_ip_address_private(value, result):
    assert validator.ip_address_private(value) == result


@pt.mark.parametrize(
    "value, result",
    [
        ["1.1.1.1", True],
        ["127.0.0.1", False]
    ]
)
def test_ip_address_global(value, result):
    assert validator.ip_address_global(value) == result


@pt.mark.parametrize(
    "value, result",
    [
        ["foo.bar", True],
        ["fail!", False]
    ]
)
def test_hostname(value, result):
    assert validator.hostname(value) == result


@pt.mark.parametrize(
    "value, result",
    [
        ["localhost", True],
        ["conigliaro.org", False]
    ]
)
def test_hostname_private(value, result):
    assert validator.hostname_private(value) == result


@pt.mark.parametrize(
    "value, result",
    [
        ["localhost", False],
        ["conigliaro.org", True]
    ]
)
def test_hostname_global(value, result):
    assert validator.hostname_global(value) == result