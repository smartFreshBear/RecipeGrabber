import django
from django.conf import settings
from django.template import Template, Context


simplified_recipe_response_template_html = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <link rel='shortcut icon' type='image/x-icon' href='/favicon.ico' />
    </head>


   <h1 style="color: #5e9ca0; text-align: right;">:המתכון</h1>
   <h2 style="color: #2e6c80; text-align: right;">:מצרכים</h2>
   <ol style="list-style-type: hebrew; direction: rtl;">
      <p style="text-align: right;">{{ingredients}}</p>
   </ol>
   <h2 style="color: #2e6c80; text-align: right;">:הוראות הכנה</h2>
   <p style="text-align: right;">{{instructions}}</p>
   <p><strong>&nbsp;</strong></p>
</html>
"""

home_page_html = """"
<head>
    <link rel='shortcut icon' type='image/x-icon' href='/favicon.ico' />
</head>
    <iframe src="https://docs.google.com/presentation/d/e/2PACX-1vQT2Ql5NWy5w69U3sSQcSrY9VgOEc32M_neFRSd94mSiqJheBuMjfVNXm_K-7SbK3NQUf_AJYlgXrWw/embed?start=false&loop=true&delayms=3000" frameborder="0" width="1440" height="839" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>
    """

TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates'}]
settings.configure(TEMPLATES=TEMPLATES)
django.setup()

simplified_recipe_template = Template(simplified_recipe_response_template_html)

home_page_recipe_template = Template(home_page_html)


def render_given_json(json_response):
    c = Context(
        {
            "ingredients": '\n '.join(json_response['ingredients']),
            "instructions": '\n '.join(json_response['instructions'])
        }
    )
    return simplified_recipe_template.render(c)


def render_home_page():
    return home_page_recipe_template.render(Context({}))

