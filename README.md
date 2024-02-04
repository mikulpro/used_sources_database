# Database of Used Information Sources

## Basic information

github name: used_sources_database

Application using REST API for storing your book sources at one place so you can later access them when asked by your Bachelor's thesis leader.

Documentation of API is available in SWI_dokumentace.pdf

This project was heavily inspired by the following website build around RESTing:
```
https://flask-restful.readthedocs.io/en/latest/quickstart.html
```

---------------------------------------------------------

## Docker setup

Docker pulls MySQL Database image to run books.db and packs it with our written REST API for POSTing, GETting, PUTting and DELTEing books.

For docker use these two commands:

```shell
docker-compose build
```
...for creating a proper docker image using all libraries and venv with name "swi".

```shell
docker compose up
```
...to run the docker. 

```shell
docker compose down
```
...to stop the docker. 

---------------------------------------------------------

## Testing

We have written unit tests in new_unit_testing.py, that can quickly ensure every CRUD method is working correctly.

To run automatised testing first make sure your docker image is up and running, then you can run unit testing using the following command in separate terminal in used_sources_database directory:

```shell
docker exec used_sources_database-app-1 python new_unit_testing.py
```

---------------------------------------------------------

## HTTP communication

Assuming you have the Docker image running on your local device and therfore can connect to it using your localhost IP address whith the default port which is usually 127.0.0.1:5000, HTTP communication with our API works like this...

To view Swagger documentation of all methods u can connect with your browser to:
```url
http://127.0.0.1:5000/swagger/
```

All non-swagger communication is done via the route /books/.

To POST a new book to the DB, create a .json file containing information for title, author, type and year and POST it using HTTP request to"
```url
http://127.0.0.1:5000/books/books
```

GETting a book from the DB can be done either by specifying the exact ID that shoud be pulled from the DB using:
```url
http://127.0.0.1:5000/books/books/<int:id>
```

...or by specifying one of the book's parameters, preferably the author.