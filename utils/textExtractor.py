import urllib.request
import time

import urllib.request
from bs4 import BeautifulSoup

MAX_SIZE_FOR_TRAINING_SET = 40

SEPERATOR_TOLORANCE = 2

I = 4


def get_text_from_url(url , retries = 20):
    try:
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        request = urllib.request.Request(url, None, headers)

        html = urllib.request.urlopen(request).read()
        # ttt = html2text.html2text(html)
        soup = BeautifulSoup(html)

        # kill all script and style elements
        for script in soup(["script", "style"]):
         script.extract()    # rip it out

        # get text
        paragraphs_raw = soup.get_text('\n\n\n').split('\n\n\n')

        result_paragraph = []
        next_para_to_add = ''
        separator_tolerance = SEPERATOR_TOLORANCE
        for text in paragraphs_raw:

            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text_result = '\n'.join(chunk for chunk in chunks if chunk)
            if text_result != '':
                next_para_to_add += '\n' + text_result
            else:
                separator_tolerance = separator_tolerance - 1

            if text_result == '' and separator_tolerance == 0:
                insert_text(next_para_to_add, result_paragraph)
                next_para_to_add = ''
                separator_tolerance = SEPERATOR_TOLORANCE

        return result_paragraph
    except Exception as exc:
        if retries > 0:
            print("an exception occurred while trying to access url {} trying again \n more details: {}"
                  .format(url, exc))
            time.sleep(1)
            return get_text_from_url(url, --retries)
        else:
            raise


def insert_text(next_para_to_add, result_paragraph):
    if next_para_to_add != '':
        if len(next_para_to_add.split(' ')) > MAX_SIZE_FOR_TRAINING_SET:
            index_with_newline = next_para_to_add.find('\n')
            insert_text(next_para_to_add[0:index_with_newline], result_paragraph)
            insert_text(next_para_to_add[index_with_newline + 1], result_paragraph)


        result_paragraph.append(next_para_to_add)