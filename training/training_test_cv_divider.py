import random
import numpy as np


def divided_training_test(examples_matrix, lbls, train_prec):
    concatenated_examples_lbs = np.concatenate((examples_matrix, lbls), axis=1)
    np.random.shuffle(concatenated_examples_lbs)

    size_of_vector = np.shape(concatenated_examples_lbs)[1]
    size_of_matrix = len(concatenated_examples_lbs)
    size_of_training = int(size_of_matrix * train_prec)
    size_of_cv = int(size_of_matrix * ((1 - train_prec) / 2))
    size_of_test = size_of_cv
    if (size_of_matrix % 2) == 1:
        size_of_test += 1

    training = concatenated_examples_lbs[0:size_of_training, :]
    validation = concatenated_examples_lbs[size_of_training:size_of_training+size_of_cv, :]
    test = concatenated_examples_lbs[size_of_training+size_of_cv:size_of_matrix, :]

    training_ex, training_lbls = split_to_ex_lbls(size_of_vector, training)
    validation_ex, validation_lbls = split_to_ex_lbls(size_of_vector, validation)
    test_ex, test_lbls = split_to_ex_lbls(size_of_vector, test)

    return training_ex, training_lbls, validation_ex, validation_lbls, test_ex, test_lbls

def split_to_ex_lbls(size_of_vector, concatened_vec):
    return concatened_vec[:, 0:size_of_vector - 1], concatened_vec[:, size_of_vector-1:size_of_vector]
