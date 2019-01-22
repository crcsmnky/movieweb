# Notes

The Python module [Records](https://github.com/kennethreitz/records) requires `mysqlclient` but it has issues on macOS.

## mysqlclient on macOS

See here for installation issues: [https://pypi.org/project/mysqlclient/](https://pypi.org/project/mysqlclient/)

First
```bash
brew install mysql-connector-c
```

Change line 112 of `[HOMEBREW_PATH]/Cellar/mysql-connector-c/6.1.11/bin/mysql_config` from:

```
# Create options
libs="-L$pkglibdir"
libs="$libs -l "
```

To:

```
# Create options
libs="-L$pkglibdir"
libs="$libs -lmysqlclient -lcrypto -L/Users/parikhs/Development/homebrew/opt/openssl/lib "
```

Then:

```bash
export CPPFLAGS="-I[HOMEBREW_PATH]/opt/openssl/include"
export LDFLAGS="-L[HOMEBREW_PATH]/opt/openssl/lib"
```

Finally:

```bash
pip install mysqlclient
```

## mysqlclient on Linux

See [Super Basic MySQL jumpstart with Records for Python](https://medium.com/emoney-engineering/super-basic-mysql-with-records-for-python-83e39c408ba6)

```
sudo apt-get install libmysqlclient-dev
```