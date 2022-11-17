import pickle


def presist_parameters_to_disk(paramaters, name_of_params):
    with open(name_of_params, 'wb') as handle:
        pickle.dump(paramaters, handle)


def load_parameter_cache_from_disk(name_of_params):
    try:
        with open(name_of_params, 'rb') as handle:
            return pickle.load(handle)
    except EOFError:
        return {}
    except FileNotFoundError:
        return {}