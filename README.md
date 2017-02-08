# Stackcite Database

A database schema library for Stackcite applications.

## Installation

Clone the latest Stackcite database reposiotry from GitHub:

```bash
localhost ~ $ git clone https://github.com/Kobnar/stackcite.api.git
localhost ~ $ git clone https://github.com/Kobnar/stackcite.data.git
```

Create and activate a new `virtualenv` directory:

```bash
localhost ~ $ virtualenv env --no-site-packages
localhost ~ $ source env/bin/activate
```

Run the included `setuptools` install script:

```bash
localhost ~ (env) $ cd stackcite.data && python setup.py develop
```

## Running Tests

The Stackcite database repository is configured to use `nose2` with branch
coverage reports generated in `htmlcov`. To run these tests, execute the
following command:

```bash
(env) localhost stackcite.data $ nose2
```