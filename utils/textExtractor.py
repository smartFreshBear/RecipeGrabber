import time
import urllib.request
import urllib.parse
from w3lib.url import safe_url_string


import html2text

MAX_SIZE_FOR_TRAINING_SET = 40

SEPERATOR_TOLORANCE = 1

MAX_WORDS_FOR_LINE = 100

MAX_WORDS_FOR_PARA = 120

I = 4

def calibrate(result_paragraph):
    fixed_paragrapes = []
    for i in range(len(result_paragraph)):
        para = result_paragraph[i]
        lines_in_para = para.split('\n')
        main_para = ''
        for line in lines_in_para:
            if len(line.split(' ')) > MAX_WORDS_FOR_LINE:
                fixed_paragrapes.append(line)
            elif line != '':
                main_para += line+'\n'
        fixed_paragrapes.append(main_para)

    return fixed_paragrapes


def get_all_text_from_url(url, retries = 5):
    if retries == 0:
        raise Exception("could not handle request")
    try:
        url_utf_8 = safe_url_string(url)
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        headers = {'User-Agent': user_agent}
        request = urllib.request.Request(url_utf_8, None, headers)

        html = urllib.request.urlopen(request).read().decode('utf-8')

        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True

        allText = h.handle(html)

        return allText
    except Exception as exc:
        if retries > 0:
            print("an exception occurred while trying to access url {} trying again \n more details: {}"
                  .format(url, exc))
            time.sleep(1)
            retries = retries - 1
            return get_all_text_from_url(url, retries)
        else:
            raise



def insert_text(next_para_to_add, result_paragraph):
    if next_para_to_add != '':
        if len(next_para_to_add.split(' ')) > MAX_SIZE_FOR_TRAINING_SET:
            index_with_newline = next_para_to_add.find('\n')
            insert_text(next_para_to_add[0:index_with_newline], result_paragraph)
            insert_text(next_para_to_add[index_with_newline + 1], result_paragraph)


        result_paragraph.append(next_para_to_add)