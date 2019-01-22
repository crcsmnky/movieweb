# Notes

## mysqlclient on macOS

First
```bash
brew install mysql-connector-c
```

(See here for installation issues: [https://pypi.org/project/mysqlclient/](https://pypi.org/project/mysqlclient/))

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
