import random
import numpy as np


def divided_training_test(examples_matrix, lbls, train_prec):
    concatenated_examples_lbs = np.concatenate((examples_matrix, lbls), axis=1)
    np.random.shuffle(concatenated_examples_lbs)

    size_of_vector = examples_matrix.shape(2)
    size_of_matrix = len(concatenated_examples_lbs)
    size_of_training = int(size_of_matrix * train_prec)
    size_of_test_and_cv = int(size_of_matrix * ((1 - train_prec) / 2))

    training = concatenated_examples_lbs[0:size_of_training, :]
    training_ex, training_lbls= split_to_ex_lbls(size_of_vector, training)
    test_ex, test_lbls = split_to_ex_lbls(concatenated_examples_lbs[size_of_training + 1: size_of_test_and_cv, :])
    validation_ex, validation_lbls = split_to_ex_lbls(concatenated_examples_lbs[size_of_training + size_of_test_and_cv + 1: size_of_matrix, :])

    return training_ex, training_lbls, test_ex, test_lbls,validation_ex, validation_lbls

def split_to_ex_lbls(size_of_vector, training):
    return training[:, 0:size_of_vector - 1], training[:, size_of_vector]
