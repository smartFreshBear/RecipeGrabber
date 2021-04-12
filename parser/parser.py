import main_flow.main_flow
import utils

ACCEPTANCE_BENCHMARK = 0.3


# proceed_text only roots

def get_key_words():
    with open('/Users/aviad.shalom/PycharmProjects/RecipeGrabber/parser/resource/key_words_ingri.txt') as f:
        return [line.replace('\n', "") for line in f.readlines()]


key_words_ingri = get_key_words()


def is_window_valid(text_window):
    return ACCEPTANCE_BENCHMARK < main_flow.main_flow.predict_ingri_probes(text_window)

def check_from_start_point(line_num, text):
    #will return paragraph size 0 or above
    return ""


def find_line_with_key_word_ingrid(text):
    lines_in_text = text.split('\n')
    all_indices = []
    for i in range(0, len(lines_in_text)):
        line = lines_in_text[i]
        line_contains_key_words = any(key in line for key in key_words_ingri)
        if line_contains_key_words:
            all_indices.append(i)
    return all_indices



print(find_line_with_key_word_ingrid("""" 
חומוס ביתי בקלי קלות
חומרים לקילו חומוס מוכן של איציק דהאן:
1/2 קילו גרגירי חומוס
300 מ"ל טחינה גולמית (או יותר, לפי הטעם)
300 מ"ל מים, או 150 מ"ל מים ו-150 מ"ל (כ-4 קוביות) קרח

כפית מלח
מיץ לימון לפי הטעם (לא חובה)


אופן ההכנה:
1. משרים את החומוס למשך לילה, ומחליפים מדי פעם את המים. בזמן ההשריה הגרגירים תופחים.

2. מסננים את המים, שוטפים את הגרגירים היטב ומכניסים לסיר גדול עם כמה ליטרים של מים. מבשלים על אש גבוהה ומביאים לרתיחה.

3. אחרי הרתיחה מסירים את הקצף, הלכלוך והקליפות הצפות וממשיכים לבשל בסיר פתוח, על אש בינונית. אפשר לבשל על אש 
"""))