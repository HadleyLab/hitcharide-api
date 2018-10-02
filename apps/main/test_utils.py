# TODO: Write the readable assertions
def assert_mock_called_with(m, *args, **kwargs):
    margs, mkwargs = m.call_args
    assert len(args) == len(margs)
    assert set(kwargs.keys()) == set(mkwargs.keys())
    for index, arg in enumerate(args):
        if callable(arg):
            arg(margs[index])
        else:
            assert arg == margs[index]
    for key, value in kwargs.items():
        if callable(value):
            value(mkwargs[key])
        else:
            assert value == mkwargs[key]
