# Jupiter

Standalone version of Planitia from Mars.

# Requirements
## - Database
 - Support MySQL, SQLite3, JSON-based(save on file), MongoDB
 - Indicate database type on configuration.py. 
 - Jupiter will automatically switch to database type.
 - If you change to other type, data will not apply to new server. you will need migrate manually.
## - Python
 - Python 3.5 or higher is recommended. some of functions not supported if Python version is low.
 - Sure it is works even not satisfy version.  
 
# configuration.py
```python
config = { "host": 'mysql.local.mac',
           "port": 3306,
           "user": 'dbuser',
           "password": 'dbpass',
           "db": 'planitia',
           "test": True,
           "jupiter": True,
           "mongodb": "mongodb://127.0.0.1:27017/",
           "mongodb_db": "Mars123",
           "jupiter_salt": "salt",
           "type": "sqlite3",
           "sqlite3_file": "jupiter.db"
   }
```
|type|Description|
|---|---|
|`host`|hostname or IP address of database server. (SQL)
|`port`|Port number of database server. (SQL)|
|`user`|Username of database server. If required. (SQL)
|`password`|Password of database server If required. (SQL)
|`db`|Schema name (SQL)
|`mongodb`| MongoDB Connection URI
|`mongodb_db`| MongoDB Database name
|`jupiter_salt`|Password Salt
|`jupiter`| Enable Jupiter Web API
|`test`| Enable Test web pages
|`type`| Database Type. Support `sqlite3`, `mysql`
|`sqlite3_file`| SQLite 3 File name

