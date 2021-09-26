def traverse_dict(d, name=None, path=""):
    if isinstance(d, dict):
        if path:
            if not name:
                if "." in path:
                    name, rest = path.split('.', 1)
                    path = rest
                else:
                    name = path
                    path = ''
            if name in d:
                branch = d[name]
                if path:
                    if '.' in path:
                        segment, rest = path.split('.', 1)
                    else:
                        segment = path
                        path = ''
                return traverse_dict(branch, segment, path)
            else:
                return None
        if name:
            return d.get(name)
        else:
            return None

    return d


def test_traverse_dict():
    d = {
        "a": {
            "b": "c"
        }
    }
    # import pdb
    # pdb.set_trace()
    res = traverse_dict(d, path="a.b.d")
    print(res)
    assert res == 'c'


if __name__ == "__main__":
    test_traverse_dict()
