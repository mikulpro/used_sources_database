# Database of Used Information Sources

## Basic information

github name: used_sources_database

Application using REST API for storing your book sources at one place so you can later access them when asked by your Bachelor's thesis leader.

Documentation of API is available in SWI_dokumentace.pdf

---------------------------------------------------------

## Docker setup

For docker use these two commands:

```shell
docker-compose build
```
...for creating a proper docker image using all libraries and venv with name "swi".

```shell
docker compose up
```
...to run the docker. Do not use "docker run", there are some problems with it.

---------------------------------------------------------

## Testing GET using curl

To ensure everything is working correctly, try composing the docker image and then communicating with it using the following command:
```shell
curl http://127.0.0.1:5000/
```
This should return the following content:
```
{ "hello": "world" }
```

---------------------------------------------------------

## Testing PUT using curl

To ensure everything is working correctly, try composing the docker image and then communicating with it using the following command on Linux shell:
```shell
curl http://localhost:5000/todo1 -d "data=Remember the milk" -X PUT
```
Or on Windows Powershell this alternaticve:
```shell
Invoke-WebRequest -Uri http://localhost:5000/todo1 -Method PUT -Body "data=Remember the milk" -ContentType "application/x-www-form-urlencoded"
```

This should return the following content:
```
{ "todo1": "Remember the milk" }
```

The same content should be gotten by then calling the following command:
```shell
curl http://localhost:5000/todo1
```