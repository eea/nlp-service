def find_path(node, key, path=[]):
    to_parse = []
    if type(node) == list:
        to_parse = range(len(node))
    elif type(node) == dict:
        to_parse = node.keys()

    for sub_node in to_parse:
        if sub_node == key:
            return (True, path)

        path.append(sub_node)
        (success, path) = find_path(node[sub_node], key, path)
        if success:
            return (success, path)
        path.pop(-1)

    return (False, path)


def get_value_from_path(node, path):
    for step in path:
        if type(step) == int:
            node = node[step]
        else:
            node = node.get(step)

    return node
