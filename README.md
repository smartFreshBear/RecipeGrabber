# RecipeGrabber
An API that given a url that points to website with a recipe, filtering all the
"blah blah blah"  before and after the recipe (ingredients and instructions) and 
returning the recipe itself.

The purpose of this web service is to:
* Help people and application summarize recipe website.
* Be used as Playground for people want to get hands-on experience working on medium size project.


How to run the project? 
Mind that the instruction are for macOs/Linux. regarding Windows, welcome to add!
* install Python 3.9

    ```
    brew install python@3.9
    ``` 
* Install [tensorflow](https://www.tensorflow.org/install/pip#macos) for your env.
* Now we want to git clone the project to your machine:

    ```
    git clone https://github.com/smartFreshBear/RecipeGrabber.git
    ``` 
* [read a little](https://docs.python.org/3/library/venv.html) about the concept of python virtual env in python official docs

* Create python virtual via IDE, assuming you are using Pycharm you can follow [this link](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html#python_create_virtual_env)
* [Read a little about pip](https://www.w3schools.com/python/python_pip.asp) - package installer for python
* Run the following command line to install all the project dependencies
```
  pip install -r requirements.txt
``` 
* **Chilling Note** most likely things won't go smooth! don't worry, most project on local env don't behave smoothly 
on the  first time, and there is always some work needed to be done depending on your OS and the state of your machine 
BEFORE you actually manage to
run the project locally. so put some nice music, brew yourself a coffee and search the web how to resolve the dependency conflicts.

* Run the app/app.py, the working directory should be ../RecipeGrabber (see Chillign Note again! it is yet another 
point you might need to fix some local env related errors)

* As you understand from the initial description this project is a actually a web service.
In order to communicate with it we need to send HTTP requests, a good way to do so nicely and elegantly is PostMan
[read about it and install it](https://www.postman.com/).
* It's time to send your first request!
* Use postman OR curl(shell tool to send http requtests) to send the following to request to our web service:

```
curl --location --request POST 'http://localhost:5000 /find_recipe_in_url/' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'url=https://www.yehudit-aviv.co.il/%D7%9E%D7%A8%D7%A7%D7%99%D7%9D/%D7%A7%D7%95%D7%A1%D7%A7%D7%95%D7%A1-%D7%9E%D7%94%D7%AA%D7%97%D7%9C%D7%94-%D7%95%D7%A2%D7%93-%D7%94%D7%A1%D7%95%D7%A3%D7%A3%D7%A3%D7%A3/' \
--data-urlencode 'instructions=true' \
--data-urlencode 'ingredients=true'
```
