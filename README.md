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

## Install on an LXC

## Create a debian container
```
$ lxc-create --name dashydeebee --template download -- --dist debian --release jessie --arch amd64
```

## Start the container
```
$ lxc-start --name dashydeebee
```

## Install python 3 and pip
```
$ lxc-attach --name dashydeebe -- apt-key update
$ lxc-attach --name dashydeebe -- apt-get install --force-yes -y python3-pip
```

## Install dashydeebee and its dependencies
```
$ lxc-attach --name dashydeebe -- pip3 install https://github.com/charlesfleche/dashydeebee/zipball/master
```

## Run the server
```
$ lxc-attach --name dashydeebee -- python3 -m dashydeebee
```

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
(env) $ pip install -r requirements.txt
```

### Run the tests
```
(env) $ python -m unittest discover
```

### Run the application
```
(env) $ python -m dashydeebee
```

Point your browser to [http://localhost:5000](http://localhost:5000) and reload the page to test your changes.
