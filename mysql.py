import pymysql.cursors
import pymysql
import configuration
config = configuration.config


def installStructure():
    return ""

def getConnection():
    connection = pymysql.connect(host=config["host"],
                                 user=config["user"],
                                 password=config["password"],
                                 db=config["db"],
                                 charset="utf8mb4")
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    return cursor, connection

def Query(query, data):
    global connection
    try:
        db, connection = getConnection()
        Query = connection.escape_string(query)
        db.execute(Query, data)
        connection.commit()
        return db.fetchall()
    finally:
        connection.close()

class SyncData:
    #def __init__(self):
    def Insert(self, uid, systemid_sql, systemid, cpu_usage, ram_usage, ip, mac, network_usage_sent, network_usage_received, network_send, network_receive, disk_read, disk_write, datetime):
        query = "INSERT INTO syncdata (uid, systemid_sql, systemid, cpu_usage, ram_usage, ip1, mac1, network_usage_sent, network_usage_received, network_send, network_receive, disk_read, disk_write, queryTime_Unix, queryTimeReadable, queryTime_year, queryTime_month, queryTime_day, queryTime_hour, queryTime_minute, queryTime_second, queryTime_microsecond) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        result = Query(query, (uid, systemid_sql, systemid, cpu_usage, ram_usage, ip, mac, network_usage_sent, network_usage_received, network_send, network_receive, disk_read, disk_write, datetime["queryTimeUnix"], datetime["queryTime"], datetime["year"], datetime["month"], datetime["day"], datetime["hour"], datetime["minute"], datetime["second"], datetime["microsecond"]))
        return result

    def SelectBy(self, Identifier, Value):
        if Identifier == "systemid_sql":
            query = "SELECT * FROM SyncData WHERE systemid_sql=%s"
        elif Identifier == "systemid":
            query = "SELECT * FROM SyncData WHERE systemid=%s"
        elif Identifier == "id":
            query = "SELECT * FROM SyncData WHERE id=%s"
        else:
            return False
        result = Query(query, (Value))
        return result

class RegisterKey:
    def Select(self, password):
        query = "SELECT * FROM registerkey WHERE password=%s"
        result = Query(query, (password))
        if result == None or result == ():
            return False
        else:
            return result[0]

class System:
    def Select(self, Identifier, Value):
        if Identifier == "id":
            query = "SELECT * FROM systems WHERE id=%s"
        elif Identifier == "targetsystemid":
            query = "SELECT * FROM systems WHERE targetsystemid=%s"
        elif Identifier == "systemid":
            query = "SELECT * FROM systems WHERE systemid=%s"
        elif Identifier == "uid":
            query = "SELECT * FROM systems WHERE uid=%s"
        else:
            return False
        result = Query(query, (Value))
        return result

    def Insert(self, uid, systemid, targetsystemid, privKey, pubKey):
        if uid == None or systemid == None or targetsystemid == None or privKey == None or pubKey == None:
            return False
        query = "INSERT INTO systems(uid, systemid, targetsystemid, privKey, pubKey) VALUES (%s, %s, %s, %s, %s)"
        result = Query(query, (uid, systemid, targetsystemid, privKey, pubKey))
        return result

    def UpdateInformation(self, name, hostip, architecture, cpu_name, kernel_name, kernel_version, ram_size, distribution_name, distribution_version, targetsystemId):
        query = "UPDATE systems SET name=%s, hostip=%s, architecture=%s, cpu_name=%s, kernel_name=%s, kernel_version=%s, ram_size=%s, distribution_name=%s, distribution_version=%s, updateRequired=0 WHERE targetsystemid=%s"
        result = Query(query, (name, hostip, architecture, cpu_name, kernel_name, kernel_version, ram_size, distribution_name, distribution_version, targetsystemId))
        return result
'''import sqlalchemy
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import NullType
from fla'''