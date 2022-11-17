import pickle5 as pickle
import logging


def presist_parameters_to_disk(paramaters, name_of_params):
    with open(name_of_params, 'wb') as handle:
        pickle.dump(paramaters, handle)


def load_parameter_cache_from_disk(name_of_params):
    try:
        with open(name_of_params, 'rb') as handle:
            logging.debug("load_parameter_cache_from_disk log")
            return pickle.load(handle)
    except EOFError:
        logging.error("load_parameter_cache_from_disk EOFE error")
        return {}
    except FileNotFoundError:
        logging.error("load_parameter_cache_from_disk file not found")
        return {}