import venusian

# This is a singleton that holds references to all the model loaders
MODELS = {}


def register_model(name):
    def wrapper(wrapped):
        def callback(scanner, ob_name, ob):
            MODELS[name] = ob

        venusian.attach(wrapped, callback)
        return wrapped

    return wrapper
