import re
from daos.key_words import key_words

class TextPrettifier:
    def process(ingred_paragraph):
        pass


class UnwantedPatternRemover(TextPrettifier):
    def process(text):
        url_regex = r'([\w]+(\/.*?\.[\w:]+))|([\w+]+\:\/\/)?([\w\d-]+\.)*[\w-]+[\.\:]\w+([\/\?\=\&\#.]?[-\w\+\,\%\=\'\"\:\/]+)*\/?'
        fixed_doc = []
        for row in text:
            fixed_doc.append(re.sub(url_regex, '', row))
        return fixed_doc

class RemoveHeadlinesTop(TextPrettifier):
    def process(text):
        if len(text) > 0:
            big_regex = get_regex_with_all_headlines()
            result = [big_regex.sub("", text[0])]
            result.extend(text[1 :])
            return result

        return text

class RemoveHeadlinesBottom(TextPrettifier):
    def process(text):
        if len(text) > 0:
            big_regex = get_regex_with_all_headlines()
            result = [big_regex.sub("", text.pop())]
            text.extend(result)
            return text

        return text

def get_regex_with_all_headlines():
    all_key_words = key_words.get_ingredients_key_words()
    all_key_words.extend(key_words.get_instructions_key_words())
    big_regex = re.compile('|'.join(map(re.escape, all_key_words)))
    return big_regex


def process(txt):
    all_prettifies = [UnwantedPatternRemover, RemoveHeadlinesTop, RemoveHeadlinesBottom]

    processed_text = txt

    for prettifer in all_prettifies:
        processed_text = prettifer.process(processed_text)
    return processed_text
