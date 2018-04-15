#################################################
Config and Secret parser for your Python projects
#################################################

.. image:: https://github.com/douglasmiranda/gconfigs/blob/master/.github/gconfigs-logo.png?raw=true
        :alt: gConfigs - Config and Secret parser for your Python projects
        :target: https://github.com/douglasmiranda/gconfigs

|

.. image:: https://img.shields.io/pypi/v/gconfigs.svg
        :alt: Badge Version
        :target: https://pypi.python.org/pypi/gconfigs

.. image:: https://img.shields.io/travis/douglasmiranda/gconfigs.svg
        :alt: Badge Travis Build
        :target: https://travis-ci.org/douglasmiranda/gconfigs

.. image:: https://coveralls.io/repos/github/douglasmiranda/gconfigs/badge.svg
        :alt: Badge Coveralls - Coverage Status
        :target: https://coveralls.io/github/douglasmiranda/gconfigs

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
        :alt: Code style: black
        :target: https://github.com/ambv/black

.. image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
        :alt: Just Say Thanks if you like gConfigs
        :target: https://saythanks.io/to/douglasmiranda

|

Let me show you some code:

.. code-block:: python

    from gconfigs import envs, configs, secrets

    HOME = envs('HOME', default='/')
    DEBUG = configs.as_bool('DEBUG', default=False)
    DATABASE_USER = configs('DATABASE_USER')
    DATABASE_PASS = secrets('DATABASE_PASS')


.. code-block:: pycon

    >>> # envs, configs and secrets are iterables
    >>> from gconfigs import envs
    >>> for env in envs:
    ...     print(env)
    ...     print(env.key)
    ...     print(env.value)
    ...
    EnvironmentVariable(key='ENV_TEST', value='env-test-1')
    ENV_TEST
    env-test-1
    ...

    >>> 'ENV_TEST' in envs
    True

    >>> envs.json()
    '{"ENV_TEST": "env-test-1", "HOME": "/root", ...}'


**This is experimental, so you know, use at your own risk.**

.. contents:: **Table of Contents**
   :local:


Features
********

* Python 3.6
* No dependencies

Read configs from:

* `Environment Variables`_
* `Local Mounted Configs and Secrets`_
* `.env (dotenv) files`_


Installation
************

To install gConfigs, run this command in your terminal:

.. code-block:: console

    $ pip install gconfigs
    $ # or
    $ pipenv install gconfigs

These are the preferred methods to install gConfigs.

If you don't have `pip`_ or `pipenv`_ installed, this `Python installation guide`_ can guide you through the process.

.. _pip: https://pip.pypa.io
.. _pipenv: https://docs.pipenv.org
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


Usage - Basics
**************

I will show you the basics with the built-in backends.

I'm still deciding about other backends. If you need a custom backend, it's easy to create. Check "Advanced" section for more.


Environment Variables
=====================

So, there are good reasons to **not** use environment variables for your configs, but if you want / need to use, please just not use for sensitive data, like: passwords, secret keys, private tokens and stuff like that.

.. code-block:: pycon

    >>> from gconfigs import envs
    # contents from ``envs`` are just data from ``os.environ``
    >>> envs
    <GConfigs backend=LocalEnv>
    >>> envs('HOME')
    '/root'


Local Mounted Configs and Secrets
=================================

Configs and secrets can be mounted as text files, read-only and in a secure location if possible, and we can read its contents. Basically the file name will be like a var / key name and its contents will be the value.


configs
-------

For ``configs``, *gConfigs* will look for mouted files at **/run/configs**, for example::

    File Absolute Path: /run/configs/LANGUAGE_CODE
    File Name: LANGUAGE_CODE
    File Contents: en-us

.. code-block:: python

    from gconfigs import configs
    LANGUAGE_CODE = configs('LANGUAGE_CODE')
    # ...translates into:
    LANGUAGE_CODE = "en-us"

Of course you can change the path that *gConfigs* will look for your configs. Let's suppose your configs are mouted at **/configs**:

.. code-block:: python

    from gconfigs import configs
    configs.root_dir = '/configs'
    # will look for /configs/LANGUAGE_CODE
    LANGUAGE_CODE = configs('LANGUAGE_CODE')

This is the simplest way to do it. Check section "Advanced" for more.


secrets
-------

It follows the same flow as ``configs``, so for more details go to ``configs``.

For ``secrets``, *gConfigs* will look for mouted files at **/run/secrets**.

.. code-block:: python

    from gconfigs import secrets
    POSTGRES_PASSWORD = secrets('POSTGRES_PASSWORD')
    # ...translates into:
    POSTGRES_PASSWORD = "super-strong-password"
    secrets.root_dir = '/secrets'
    # will look for /secrets/POSTGRES_PASSWORD
    POSTGRES_PASSWORD = secrets('POSTGRES_PASSWORD')

**NOTE:** If you don't know what tools follow these workflows for configurations and secrets, you could try with `Docker`_. Check `Docker Configs`_ and / or `Docker Secrets`_ management with Docker.

.. _Docker: https://www.docker.com/


.env (dotenv) files
===================

.env files are present not only in Python projects, for that reason many developers are familiar with, it's just like a .ini file, but without the sections, you could say it's a key-value store in a file.

.env files could be a good solution depending on your stack. It's better than environment variables at least.

You could just put your configurations in a file called **.env**, (or whatever name you want), for example the contents of your file would be:

.. code-block:: INI

    ROOT=/
    PROJECT_NAME=gConfigs - Config and Secret parser
    AUTH_MODULE=users.User

After that I'm going to save my **.env** file in **/app/**, then the full path will be **/app/.env**, now let's see how to load all it's contents in *gConfigs*:

.. code-block:: python

    from gconfigs import dotenvs
    dotenvs.load_file('/app/.env')
    # after that it's like using ``envs``, or ``configs``
    ROOT = dotenvs('ROOT')
    NAME = dotenvs('PROJECT_NAME')
    AUTH = dotenvs('AUTH_MODULE')

NOTES:
  * if it's a .ini syntax it will be parsed, but it will ignore sections
  * duplicated keys will be overridden by the latest value
  * inexistent keys or empty files will raise exception
  * all values load as strings, use casting to convert them
  * didn't like the name ``dotenvs``? Just do: ``from gconfigs import dotenvs as configs``


Usage - Advanced
****************

With the basics, you are already running your projects just fine, but if you want the extra stuff of *gConfigs*, I'll show you.

I'll be using envs in the examples, but it should work for all built-in backends.


Get Your Config Value
=====================


default value
-------------

You can provide a default value, in case the backend couldn't return the config.

.. code-block:: pycon

    >>> from gconfigs import envs
    >>> envs('WHATEVER', default='/')
    '/'


typed value
-----------

Generally backends will return key and value as strings, but you can return other types.

``gconfigs.GConfigs.get`` won't try to cast your typed value.

For example when providing a ``default`` value you could set a ``int``:

.. code-block:: pycon

    >>> from gconfigs import envs
    >>> envs('WORKERS', default=1)
    1

But you **must** know that if your backend, in that case it's just the ``LocalEnv`` backend, return a string value, you could create a bug in your configuration. Unless your software is prepared to deal with the number of ``WORKERS`` being a string and an integer, you could be in trouble.

What you want here is to cast your value, that you could achieve by simply converting what gConfigs return to the desired type or using some of the built-in casting methods.


casting (converting your strings to a specific type)
----------------------------------------------------

Most of the backends will return a string (``str``) as value. But sometimes you want to use a ``bool``, ``int``, ``list`` config.

**NOTE:** I choose to **not** do too much magic, so the cast methods implemented for *gConfigs* just loads the values with ``json.loads`` from the Python's built-in ``json`` module. Therefore, it must be a valid json value, I'll show you how:


BOOLEAN - Converting to bool
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's say you want ``DEBUG`` as a boolean.

.. code-block:: pycon

    >>> from gconfigs import envs
    >>> envs.as_bool('DEBUG')
    True

I'm not doing any magic translation of ``"on"`` => ``True`` | ``"yes"`` => ``True``. I don't want to introduce ambiguity, In my opinion, configurations must be straightforward and with limited variations.


LIST - Converting to list
^^^^^^^^^^^^^^^^^^^^^^^^^

Let's say you have a configuration value like this:

.. code-block:: bash

    [1, 2.1, "string-value", true]

    # if you want to try in your terminal:
    export CONFIG_LIST='[1, 2.1, "string-value", true]'

The value must be just JSON-like, which is very close to a list in Python. And you will be able to get a list object by doing:

.. code-block:: pycon

    >>> from gconfigs import envs
    >>> envs.as_list('CONFIG-LIST')
    [1, 2.1, 'string-value', True]


DICT - Converting to dict
^^^^^^^^^^^^^^^^^^^^^^^^^

If you have a value that is basically a JSON valid object, you may already know you can turn into a ``dict`` using ``json.loads``.

Here is an example, if your config value is:

.. code-block:: bash

    {"endpoint": "/", "workers": 1, "debug": true}

    # if you want to try in your terminal:
    export CONFIG_DICT='{"endpoint": "/", "workers": 1, "debug": true}'


.. code-block:: pycon

    >>> from gconfigs import envs
    >>> envs.as_list('CONFIG-LIST')
    {'endpoint': '/', 'workers': 1, 'debug': True}

Again, nothing new, no surprises, boring, no magic... as intended.


OTHER TYPES - Converting to int, float, tuple, str, set
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Well let's not reinvent the wheel, like I said before, most backends will return string by default, so if we have something like:

.. code-block:: bash

    WORKERS="1"
    WEIGHT="1.1"
    MODULES='["auth", "session"]'

We could then do this:

.. code-block:: pycon

    >>> from gconfigs import envs
    >>> int(envs('WORKERS'))
    1
    >>> float(envs('WEIGHT'))
    1.1

If you want ``tuple`` or ``set``, just get as list and then do whatever you want:

.. code-block:: pycon

    >>> from gconfigs import envs
    >>> tuple(envs.as_list('MODULES'))
    ('auth', 'session')
    >>> set(envs.as_list('MODULES'))
    {'auth', 'session'}

What about strings? If you getting from your backend config values that aren't strings, and for some of them you need to convert to ``str``, just use the Python built-in ``str()``:

.. code-block:: pycon

    >>> from gconfigs import envs
    >>> envs('AN-INT-CONFIG')  # if this return an integer
    1
    >>> str(envs('AN-INT-CONFIG'))  # just use str
    '1'


Interators
==========

.. code-block:: pycon

    >>> from gconfigs import envs
    >>> list(envs)  # envs is a iterator
    [EnvironmentVariable(key='LANG', value='C.UTF-8'), ...]

    >>> for env in envs:
    ...     print(env)
    ...     print(env.key)
    ...     print(env.value)
    ...
    EnvironmentVariable(key='ENV_TEST', value='env-test-1')
    ENV_TEST
    env-test-1
    ...

If you use an iterator once, you can't iterate again, but if you want you can call `.iterator()` and get a new one:

.. code-block:: pycon

    >>> iter_envs = envs.iterator()
    >>> for env in iter_envs:
    ...     print(env.key)
    ...
    HOME
    LANG


Extra Goodies
=============

* How many configs with Python built-in ``len``.
* Config key exists with Python built-in ``in``.
* Output your key-value configs as JSON.

.. code-block:: pycon

    >>> from gconfigs import envs
    >>> len(envs)
    28
    >>> 'HOME' in envs
    True
    >>> envs.json()
    '{"HOME": "/root", ...}'


Beyond: from gconfigs import envs
*********************************

Let's see some stuff you can do more than just import the ready for use ``configs`` and ``secrets``.

We have ``GConfigs`` class which takes data from one of the backends ``gconfigs.backends`` and and add fancy stuff like casting and iterator behaviour.

A backend is simply a class implementing the methods:

* ``get(key: str)``: return a value given a key
* ``keys()``: return all available keys

If you know some Python, just look the ``gconfigs.backends.LocalEnv`` and you'll see there's no secret.


Extending a Built-in Backend
============================

Okay let's create a practical example of how to override the behaviour of one of our backends.

If you get your Configs and Secrets with ``gconfigs.configs`` and ``gconfigs.secrets``, you are making use of ``gconfigs.LocalMountFile`` backend. That being said we could extend ``gconfigs.LocalMountFile`` and make it only get the configs if they are a *mount point*.

.. code-block:: python

    from gconfigs import GConfigs, LocalMountFile
    import os

    class MountPointConfigs(LocalMountFile):
        def get(self, key, **kwargs):
            file = self.root_dir / key
            if os.path.ismount(file):
                return super().get(key, **kwargs)

            raise Exception(f"The config {key} file must be a mount point.")

    # :backend: can be a callable class or a instance
    # :object_type_name: it's just the name of the namedtuple you get when you
    # iterate over `configs`.
    configs = GConfigs(
        backend=MountPointConfigs, object_type_name="MountPointConfig"
    )

    MY_CONFIG = configs('MY_CONFIG')

(if you use `Docker Configs`_ or `Docker Secrets`_, you probably know that it does mount your configs / secrets in your container filesystem)


Create Your Own Backend
=======================

If you want to extend the usage of *gConfigs* with other backends, it's not a hard task.

Imagine my configs are stored in Redis (a key-value store), a backend for this would look like:

.. code-block:: python

    class RedisBackend:
        """Redis Backend for gConfigs
        NOTE: this is an example, so you probably would have to install the "redis"
        python package, then connect to Redis, then you would be able to implement
        ``get`` and ``keys`` methods.
        """
        def keys(self):
            # return a iterable of all keys available
            return available_keys

        def get(self, key: str):
            # this method receive a key (identifier of a config)
            # and return its respective value
            return value

*gConfigs* only expects you provide two methods:

``get(key: str)``: return a value given a key
  * connect to your backend
  * based on the ``key`` get it's value
  * return the value OR raise exception if it was not possible to get the config
  * keep in mind that the return type it's up to you, ``str`` makes things kinda agnostic

``keys()``: return all available keys
  * connect to your backend
  * return an iterable (list, tuple, generator..) of all available keys if possible
  * if you don't want or it's not possible to implement this, just raise a ``NotImplementedError`` or a more informative exception if you like

(Optional) ``load_file(filepath: str)``: parse file and just raise exception if fails
  * IMPORTANT: the method name it has to be ``load_file``, that way gConfigs will provide a ``load_file`` that just calls the backend to load the file, check ``gconfigs.GConfigs.__init__`` for more
  * read the file
  * parse and get keys and values
  * store the keys and values inside a ``dict`` if you want
  * then implement ``get`` and ``keys`` as described above

You could also look at the module ``gconfigs.backends``, so you can see how the built-in backends are implemented.


What's Next
***********

* More backends, the really fun ones
* Don't know, you tell me on `Issues`_

.. _Docker Configs: https://docs.docker.com/engine/swarm/configs/
.. _Docker Secrets: https://docs.docker.com/engine/swarm/secrets/

.. _Issues: https://github.com/douglasmiranda/gconfigs/issues
