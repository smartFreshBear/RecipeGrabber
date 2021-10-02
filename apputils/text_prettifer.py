import re
from daos.key_words import key_words

INSTRUCTIONS = 'instructions'
INGREDIENTS = 'ingredients'

get_opposite = {
    INSTRUCTIONS: INGREDIENTS,
    INGREDIENTS: INSTRUCTIONS
}

class TextPrettifier:
    def process(ingred_paragraph, type):
        pass


class UnwantedPatternRemover(TextPrettifier):
    supporting_types = [INGREDIENTS, INSTRUCTIONS]
    def process(text, type):
        url_regex = r'([\w]+(\/.*?\.[\w:]+))|([\w+]+\:\/\/)?([\w\d-]+\.)*[\w-]+[\.\:]\w+([\/\?\=\&\#.]?[-\w\+\,\%\=\'\"\:\/]+)*\/?'
        fixed_doc = []
        for row in text:
            fixed_doc.append(re.sub(url_regex, '', row))
        return fixed_doc


class RemoveHeadlinesTop(TextPrettifier):
    supporting_types = [INGREDIENTS, INSTRUCTIONS]
    def process(text, type):
        if len(text) > 0:
            big_regex = get_regex_for_type(type)
            result = [big_regex.sub("", text[0])]
            result.extend(text[1 :])
            return result

        return text

class RemoveInstructions(TextPrettifier):

    supporting_types = [INGREDIENTS]

    def process(text, type):
        all_suspicious_incites = [i for i, x in enumerate(text) if any(word in x for word in key_words.get_instructions_key_words())]
        if len(all_suspicious_incites) == 0:
            return text
        else:
            last_suspicious_index = all_suspicious_incites.pop()
            return text[0:last_suspicious_index]

class RemoveHeadlinesBottom(TextPrettifier):
    supporting_types = [INGREDIENTS, INSTRUCTIONS]
    def process(text, type):
        if len(text) > 0:
            big_regex = get_regex_for_type(get_opposite[type])
            result = [big_regex.sub("", text.pop())]
            text.extend(result)
            return text

        return text


class RemoveEmptyLines(TextPrettifier):

    supporting_types = [INGREDIENTS, INSTRUCTIONS]

    def process(text, type):
        filtered_empty = [line for line in text if line != '']
        return filtered_empty


def get_regex_for_type(type):
    all_key_words = key_words.get_ingredients_key_words() if type == INGREDIENTS else key_words.get_instructions_key_words()
    big_regex = re.compile('|'.join(map(re.escape, all_key_words)))
    return big_regex


all_prettifies = [UnwantedPatternRemover, RemoveInstructions ,RemoveHeadlinesTop, RemoveHeadlinesBottom, RemoveEmptyLines]

def process(json_response):

    ingredients_text = json_response[INGREDIENTS]
    instructions_text = json_response[INSTRUCTIONS]

    json_response[INGREDIENTS] = prettify(all_prettifies, ingredients_text, INGREDIENTS)
    json_response[INSTRUCTIONS] = prettify(all_prettifies, instructions_text, INSTRUCTIONS)
    return json_response


def prettify(all_prettifies, processed_text, member):
    for prettifer in all_prettifies:
        if member in prettifer.supporting_types:
            processed_text = prettifer.process(processed_text, member)
    return processed_text
