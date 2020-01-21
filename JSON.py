import configuration as config
import os
import sys
import json
import base64
from pathlib import Path

from datetime import datetime

if getattr(sys, 'frozen', False):
    root = os.path.dirname(sys.executable)
else:
    root = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def SaveFile(type, filename, contents, systemid=""):
    try:
        path = os.path.join(root, type, systemid)
        file = open(os.path.join(filename, path), "w")
        file.write(json.dumps(contents, indent=4))
        file.close()
    except Exception as e:
        print(e)


def createDirectory(path, name):
    try:
        if os.path.exists(os.path.join(path, name)):
            return True
        else:
            Path(os.path.join(path, name)).mkdir(parents=True, exist_ok=True)
            return True
    except Exception as e:
        return False


def openFile(filepath):
    file = open(filepath, "r")
    return file


directoryList = ["registerkey", "systems", "systemstaticdata", "registerkey"]
for directoryName in directoryList:
    createDirectory(root, directoryName)


class SyncData:
    def __init__(self):
        self.Field = "cpu_usage, disk_read, disk_write, ip1, mac1, network_receive, network_send, network_usage_received, network_usage_sent, queryTimeReadable, queryTime_Unix, ram_usage"

    def Insert(self, uid, systemid_sql, systemid, cpu_usage, ram_usage, ip, mac, network_usage_sent,
               network_usage_received, network_send, network_receive, disk_read, disk_write, datetime):
        now = datetime.now()
        data = {
            "uid": uid,
            "systemid_sql": systemid_sql,
            "systemid": systemid,
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage,
            "ip1": ip,
            "mac1": mac,
            "network_usage": {
                "sent": network_usage_sent,
                "received": network_usage_received
            },
            "network_bandwidth": {
                "send": network_send,
                "receive": network_receive
            },
            "disk": {
                "read": disk_read,
                "write": disk_write
            }
        }
        SaveFile("syncdata", now.strftime("%Y-%m-%d %H:%M:%S:%f") + "+--+" + uid + "-" + systemid, data, systemid)

    def SelectBy(self, Identifier, Value, uid):
        # if Identifier == "systemid_sql":
        # query = "SELECT * FROM SyncData WHERE systemid_sql=? AND uid=?"
        if Identifier == "systemid":

            path = os.path.join("syncdata", Value)
        # elif Identifier == "id":
        # query = "SELECT * FROM SyncData WHERE id=? AND uid=?"
        else:
            return False
        result = []
        for filename in os.listdir(os.getcwd()):
            file = open(filename, "r")
            arr.append(json.loads(file))

        return result

    def SelectByDate(self, year, month, day, systemid, uid):
        if not year or not month or not day:
            return False
        query = "SELECT " + self.Field + " FROM SyncData WHERE queryTime_year=? AND queryTime_month=? AND queryTime_day=? AND systemid=? AND uid=?"
        return Query(query, (year, month, day, systemid, uid))

    def SelectByDateTimeRange(self, start, end, systemid, uid):
        if not (start and end):
            return False

        query = "SELECT * FROM SyncData WHERE queryTimeReadable BETWEEN ? AND ? AND systemid=? AND uid=?"
        result = Query(query,
                       (start.strftime("%Y-%m-%d %H:%M:%S:%f"), end.strftime("%Y-%m-%d %H:%M:%S:%f"), systemid, uid,))
        return result


class RegisterKey:
    def getKeyExists(self, code, value):
        path = os.path.join(root, "registerkey")
        filelist = os.listdir(path)
        for filename in filelist:
            byte = filename.encode()
            name = base64.b64decode(byte).decode().split("-")
            if str(name[code]) == value:
                return {"uid": name[0], "password": name[1], "interval": name[2]}
            else:
                return False

    def SelectBy(self, identifier, value):
        file = {}
        code = 0
        if identifier == "password":
            code = 1
        elif identifier == "uid":
            code = 0
        result = self.getKeyExists(code, value)
        if not result:
            return False

        else:
            return result

    def Update(self, identifierValue, password, interval, identifier="uid"):
        if identifierValue is None or password is None or interval is None:
            return False
            # UPDATE(+ INSERT if UPDATE    fails)
        # uery = "UPDATE() registerkey SET uid=?, password=?, intervals=?, OSType=? WHERE uid=?"
        query = "INSERT INTO registerkey (uid, password, intervals, OSType) VALUES (?, ?, ?, ?) ON CONFLICT(uid) DO UPDATE SET password=?, intervals=?"
        result = Query(query, (identifierValue, password, interval, "universal", password, interval,))
        return result

    def checkPasswordAvailable(self, password):
        result = QueryReturnOne("SELECT 1 FROM registerkey WHERE password = ?", (password,))
        print(result)
        if result is () or result is None or result is []:
            return True
        else:
            return False


class System:
    def Select(self, Identifier, Value):
        if Identifier == "uid":
            query = "SELECT * FROM systems WHERE uid=?"
        elif Identifier == "id":
            query = "SELECT * FROM systems WHERE id=?"
        elif Identifier == "targetsystemid":
            query = "SELECT * FROM systems WHERE targetsystemid=?"
        elif Identifier == "systemid":
            query = "SELECT * FROM systems WHERE systemid=?"
        else:
            return False

        if Identifier != "uid":
            result = QueryReturnOne(query, (Value,))
        else:
            result = Query(query, (Value,))
        return result

    def Insert(self, uid, systemid, targetsystemid, privKey, pubKey):
        if uid == None or systemid == None or targetsystemid == None or privKey == None or pubKey == None:
            return False
        query = "INSERT INTO systems(uid, systemid, targetsystemid, privKey, pubKey) VALUES (?, ?, ?, ?, ?)"
        result = Query(query, (uid, systemid, targetsystemid, privKey, pubKey,))
        return result

    def UpdateInformation(self, name, hostip, architecture, cpu_name, kernel_name, kernel_version, ram_size,
                          distribution_name, distribution_version, targetsystemId):
        query = "UPDATE systems SET name=?, hostip=?, architecture=?, cpu_name=?, kernel_name=?, kernel_version=?, ram_size=?, distribution_name=?, distribution_version=?, updateRequired=0 WHERE targetsystemid=?"
        result = Query(query, (
        name, hostip, architecture, cpu_name, kernel_name, kernel_version, ram_size, distribution_name,
        distribution_version, targetsystemId,))
        return result

    def SetRequireUpdate(self, uid):
        query = "UPDATE systems SET updateRequired=(SELECT intervals FROM registerkey WHERE uid=?) WHERE uid=?"
        result = Query(query, (uid, uid,))
        return result
