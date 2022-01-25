# A fun web API practice: Python/Flask

This is a Python web API 

## Requirements

* Python 3 (initially written in 3.9.5)

## Running locally

Install requirements:

```sh
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Run the server:

```sh
flask run
```

Note that you will need to restart the server on code change.

## Usage

Hello world

```sh
curl http://127.0.0.1:5000/
```

Create sensor

```sh
curl -X POST http://127.0.0.1:5000/create-sensor \
  -H 'Content-Type: application/json' \
  --data '{"frequency": 2 }'
```

Poll to update all sensors

```sh
curl -X GET  http://127.0.0.1:5000/poll
```

Display all sensors

```sh
curl -X GET  http://127.0.0.1:5000/all-sensors
```
