from pathlib import Path

from tensorflow import keras
import data_loader
from training import training_test_cv_divider
from utils.logger import create_logger_instance
from vectorizing.vectorizer import Vectorizer

main_flow_logger = create_logger_instance('Main_Flow')
vectorizer = Vectorizer()


# Cache file names:
INSTRUCTIONS_MODEL = 'inst_params'
INGREDIENTS_MODEL = 'ing_params'




def loadCache():
    global model_instruction
    global model_ingredients

    file_instru = f'{INSTRUCTIONS_MODEL}'
    file_ingri = f'{INGREDIENTS_MODEL}'

    if not (Path(file_instru).is_dir() and Path(file_ingri).is_dir()):
        return None

    main_flow_logger.info('loading cache')
    model_instruction = keras.models.load_model(file_instru)
    model_ingredients = keras.models.load_model(file_ingri)

    return model_instruction and model_ingredients


FROM_NAME_TO_LABELS = {}


def load_data():
    table = data_loader.training_storer.get_values(False)

    vectorized_exam = vectorizer.vectorize(table)

    labels_ingredients = vectorizer.get_labels_for(table, 1)
    labels_instruction = vectorizer.get_labels_for(table, 2)


    FROM_NAME_TO_LABELS[INSTRUCTIONS_MODEL] = [vectorized_exam, labels_instruction]
    FROM_NAME_TO_LABELS[INGREDIENTS_MODEL] = [vectorized_exam, labels_ingredients]


def train(name_group, test_error_tolerance):
    test_error = 10

    model = create_model()

    while test_error_tolerance < test_error:
        training_ex, training_labels, validation_ex, validation_labels, test_ex, test_labels = \
            training_test_cv_divider.divided_training_test(FROM_NAME_TO_LABELS[name_group][0],
                                                           FROM_NAME_TO_LABELS[name_group][1], 0.8)

        model.fit(training_ex, training_labels, epochs=42,
                  validation_data=(validation_ex, validation_labels))

        test_error, _ = model.evaluate(test_ex, test_labels)

    model.save(f'{name_group}')

    return model


def create_model():
    model = keras.models.Sequential()
    model.add(keras.layers.Dense(Vectorizer.BETA_VECTOR_SIZE, activation="relu"))
    model.add(keras.layers.Dense(12, activation="relu"))
    model.add(keras.layers.Dense(6, activation="relu"))
    model.add(keras.layers.Dense(4, activation="relu"))
    model.add(keras.layers.Dense(1, activation="sigmoid"))
    model.compile(
        loss='binary_crossentropy',
        optimizer="sgd",
        metrics=["accuracy"])
    return model


def predict_ingred_probes(text: str):
    vectorized_ingred = vectorizer.example_to_vector_beta(text)
    return predict_vector_with_model(model_ingredients, vectorized_ingred)


def predict_instruc_probes(text: str):
    vectorized_instr = vectorizer.example_to_vector_beta(text)
    return predict_vector_with_model(model_instruction, vectorized_instr)


def predict_vector_with_model(model, vector):
    try:
        transpose_vector = vector.reshape(1, len(vector))
        ans = model(transpose_vector)
        ans = ans[0][0]
    except Exception as e:
        main_flow_logger.error(f'error has occurred during prediction, {e}')
        raise e

    return ans


def main():
    global FROM_NAME_TO_LABELS
    global model_instruction
    global model_ingredients

    if not loadCache():
        load_data()
        model_instruction = train(name_group=INSTRUCTIONS_MODEL,
                                  test_error_tolerance=0.02)
        model_ingredients = train(name_group=INGREDIENTS_MODEL,
                                  test_error_tolerance=0.02)

if __name__ == '__main__':
    main()
