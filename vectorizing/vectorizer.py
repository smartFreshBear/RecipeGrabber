from abc import ABC
import numpy as np
from transformers import AutoTokenizer


class Vectorizer(ABC):
    BETA_VECTOR_SIZE = 2042

    FROM_NAME_TO_LABELS = {}


    def __init__(self):
        model_name = "xlm-roberta-base"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def example_to_vector_beta(self, txt) -> np.ndarray:

        token_ids = self.tokenizer(txt)['input_ids']
        vector = np.zeros(self.BETA_VECTOR_SIZE)
        for token_id in token_ids:
            index = token_id % self.BETA_VECTOR_SIZE
            vector[index] += 0.02

        return vector


    def vectorize(self, table):

        training_set_size = len(table)
        training_examples_matrix = np.zeros((training_set_size,self.BETA_VECTOR_SIZE))

        for i in range(1, training_set_size):
            row = table[i]
            if len(row) == 3:
                txt = row[0]
                vectorized_txt = self.example_to_vector_beta(txt)
                training_examples_matrix[i] = vectorized_txt


        return training_examples_matrix


    def get_labels_for(self, table, index_of_mark):

        training_set_size = len(table)
        labels = np.zeros((training_set_size, 1))

        for i in range(1, training_set_size):
            row = table[i]
            if len(row) == 3:
                labels[i] = table[i][index_of_mark]

        return labels
