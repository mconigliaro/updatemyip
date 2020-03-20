import updatemyip.options as opt


def test_parse():
    args = ["foo.example.com", "-a", "test.Address", "-d", "test.DNS"]
    opts = opt.parse(args)

    assert opts.fqdn == args[0]
    assert opts.address_plugins == [args[2]]
    assert opts.dns_plugin == args[4]
