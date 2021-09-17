

def load_key_words_ingred():
    global key_words_ingred
    with open('daos/key_words/resource/key_words_ingri.txt', encoding="utf8") as f:
        key_words_ingred = [line.replace('\n', "") for line in f.readlines()]


def load_key_words_instr():
    global key_words_instr
    with open('daos/key_words/resource/key_words_instruc.txt', encoding="utf8") as f:
        key_words_instr = [line.replace('\n', "") for line in f.readlines()]


load_key_words_ingred()
load_key_words_instr()


def get_ingredients_key_words():
    return key_words_ingred


def get_instructions_key_words():
    return key_words_instr
