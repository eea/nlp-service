import venusian

MODELS = {}


def register_model(name):
    def wrapper(wrapped):
        def callback(scanner, ob_name, ob):
            MODELS[name] = ob
            print('hello')
        venusian.attach(callback)
        return wrapped
    return wrapper
