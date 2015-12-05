# dashydeebee
A python 3 dashboard for ODK. For the moment nothing else than a quickly (badly…) hacked experimental project.

## Install and run
Make sure [pip](https://en.wikipedia.org/wiki/Pip_(package_manager)) is installed on your machine.

### Create a python virtual environment
```shell
$ pyvenv dashydeebee
$ source dashydeebee/bin/activate
(dashydeebee) $
```

### Install dashydeebee and its dependencies
```shell
(dashydeebee) $ pip install https://github.com/charlesfleche/dashydeebee/zipball/master
```

### Run the server
```shell
(dashydeebee) $ python -m dashydeebee
```
Point your browser to [http://localhost:5000](http://localhost:5000).

## Develop
### Get the code
```shell
$ git clone git@github.com:charlesfleche/dashydeebee.git
$ cd dashydeebee
```

### Create a python virtual environment
```shell
$ pyvenv env
$ source env/bin/activate
(env) $
```

### Install dependencies
```
(env) $ python setup.py develop
```

### Run
```
(env) $ python -m dashydeebee
```

Point your browser to [http://localhost:5000](http://localhost:5000) and reload the page to test your changes.
