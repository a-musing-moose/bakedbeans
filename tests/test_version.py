from bakedbeans import __version__


def test_version_tuple_matches_version():
    segements = __version__.__version__.split('.')
    for i, value in enumerate(segements):
        assert str(__version__.VERSION[i]) == value
