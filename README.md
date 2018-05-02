# flask_api
a restful api, with a swagger example, and a sqlalchemy example

* [manage.py](./manage.py)
* [log](./log)
* [runserver.sh](./runserver.sh)  #sh runserver.sh
* [test.db](./test.db)  #database for test
* [config.py](./config.py)  #config
* [lib](./lib)
  * [\_\_init\_\_.py](./lib/__init__.py)
  * [flask_mysql.py](./lib/flask_mysql.py)  #extension for sqlalchemy
* [requirements.txt](./requirements.txt)
* [app](./app)
  * [\_\_init\_\_.py](./app/__init__.py)  #create and initialize flask app
  * [errors.py](./app/errors.py)  #customize error class
  * [utils.py](./app/utils.py)  #util tools for restful api(response reformater, exception handling, db session)
  * [meta.py](./app/meta.py)  #single instance of some extension
  * [models.py](./app/models.py)  #models for function logic
  * [static](./app/static)
    * [favicon.ico](./app/static/favicon.ico)  #favicon for swagger
  * [apis](./app/apis)
    * [\_\_init\_\_.py](./app/apis/__init__.py)
    * [auth.py](./app/apis/auth.py)  #password and token
    * [resources.py](./app/apis/resources.py)  #a simple api example
    * [resources_v2.py](./app/apis/resources_v2.py)  #a simple api example with swagger support
    
Thanks for [Flask-RESTPlus](http://flask-restplus.readthedocs.io/en/stable/) project!
