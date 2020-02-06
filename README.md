# garageautomation

Utilities and a [Flask](https://www.palletsprojects.com/p/flask/) based API for
controlling garage doors with a [Raspberry Pi](https://www.raspberrypi.org/).


## Development

The project uses [Poetry](https://python-poetry.org/) to manage packaging and
dependencies.

### Installing Poetry

To install Poetry:

```bash
pip install poetry
```

### Installing and running the package for development

```bash
poetry install
poetry run garageapp
```

### Build a package for deployment

The following command will build a source distribution tarball and a Python
wheel in the `dist` directory. The wheel can be deployed to production on a
Raspberry Pi

```bash
poetry build
```

## Running the API

```bash
python -m garageautomation.endpoint
```

## Notes
Some ideas I want to build from..

a) like his clean code and object orientated
approach https://github.com/andrewshilliday/garage-door-controller

b) like the
loggging funct in this as well as persistence approach
https://github.com/nathanpjones/GaragePi

c) an early one
https://github.com/ifermon/garagePi

d) potential alexa integration
https://github.com/shrocky2/Alexa_Garage/blob/master/garage.py
