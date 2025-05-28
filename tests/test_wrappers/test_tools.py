import hades.wrappers.tools as tools


def test_to_wsl():
    paths = ("C:/",)
    refs = ("/mnt/c/",)

    for path, ref in zip(paths, refs):
        assert tools.to_wsl(path) == ref
