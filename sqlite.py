import sqlite3
import configuration as config
connection = sqlite3.connect(config.config["sqlite3_file"], check_same_thread=False)
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
connection.row_factory = dict_factory
cursor = connection.cursor()

def Query(query, value):
    try:
        cursor.execute(query, value)
        connection.commit()

        return cursor.fetchall()

    except Exception as e:
        print(e)
    #finally:
        #connection.close()

def QueryReturnOne(query, value):
    try:
        cursor.execute(query, value)
        connection.commit()
        return cursor.fetchone()
    except Exception as e:
        print(e)

def installStructure():
    return ""

class SyncData:
    def __init__(self):
        self.Field = "cpu_usage, disk_read, disk_write, ip1, mac1, network_receive, network_send, network_usage_received, network_usage_sent, queryTimeReadable, queryTime_Unix, ram_usage"
    def Insert(self, uid, systemid_sql, systemid, cpu_usage, ram_usage, ip, mac, network_usage_sent, network_usage_received, network_send, network_receive, disk_read, disk_write, datetime):
        query = "INSERT INTO syncdata (uid, systemid_sql, systemid, cpu_usage, ram_usage, ip1, mac1, network_usage_sent, network_usage_received, network_send, network_receive, disk_read, disk_write, queryTime_Unix, queryTimeReadable, queryTime_year, queryTime_month, queryTime_day, queryTime_hour, queryTime_minute, queryTime_second, queryTime_microsecond) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        result = Query(query, (uid, systemid_sql, systemid, cpu_usage, ram_usage, ip, mac, network_usage_sent, network_usage_received, network_send, network_receive, disk_read, disk_write, datetime["queryTimeUnix"], datetime["queryTime"], datetime["year"], datetime["month"], datetime["day"], datetime["hour"], datetime["minute"], datetime["second"], datetime["microsecond"],))
        return result

    def SelectBy(self, Identifier, Value):
        if Identifier == "systemid_sql":
            query = "SELECT * FROM SyncData WHERE systemid_sql=?"
        elif Identifier == "systemid":
            query = "SELECT * FROM SyncData WHERE systemid=?"
        elif Identifier == "id":
            query = "SELECT * FROM SyncData WHERE id=?"
        else:
            return False
        result = Query(query, (Value,))
        return result

    def SelectByDate(self, year, month, day, systemid):
        if not year or not month or not day:
            return False
        query = "SELECT " + self.Field + " FROM SyncData WHERE queryTime_year=? AND queryTime_month=? AND queryTime_day=? AND systemid=?"
        return Query(query, (year, month, day, systemid,))

    def SelectByDateTimeRange(self, start, end, systemid, uid):
        if not(start and end):
            return False

        query = "SELECT * FROM SyncData WHERE queryTimeReadable BETWEEN ? AND ? AND systemid=? AND uid=?"
        result = Query(query, (start.strftime("%Y-%m-%d %H:%M:%S:%f"), end.strftime("%Y-%m-%d %H:%M:%S:%f"), systemid, uid,))
        return result


class RegisterKey:
    def SelectBy(self, identifier, value):
        if identifier == "password":
            query = "SELECT * FROM registerkey WHERE password=?"
        elif identifier == "uid":
            query = "SELECT * FROM registerkey WHERE uid=?"
        result = QueryReturnOne(query, (value,))
        if result == None or result == ():
            return False
        else:
            return result

    def Update(self, identifierValue, password, interval, identifier="uid"):
        if identifierValue is None or password is None or interval is None:
            return False
            #UPDATE(+ INSERT if UPDATE    fails)
        #uery = "UPDATE() registerkey SET uid=?, password=?, intervals=?, OSType=? WHERE uid=?"
        query = "INSERT INTO registerkey (uid, password, intervals, OSType) VALUES (?, ?, ?, ?) ON CONFLICT(uid) DO UPDATE SET password=?, intervals=?"
        result = Query(query, (identifierValue, password, interval, "universal", password, interval,))
        return result

    def checkPasswordAvailable(self, password):
        result = Query("SELECT 1 FROM registerkey WHERE password = ?", (password,))
        if result is () or result is None:
            return True
        else:
            return False



class System:
    def Select(self, Identifier, Value):
        if Identifier == "id":
            query = "SELECT * FROM systems WHERE id=?"
        elif Identifier == "targetsystemid":
            query = "SELECT * FROM systems WHERE targetsystemid=?"
        elif Identifier == "systemid":
            query = "SELECT * FROM systems WHERE systemid=?"
        elif Identifier == "uid":
            query = "SELECT * FROM systems WHERE uid=?"
        else:
            return False
        result = Query(query, (Value,))
        return result

    def Insert(self, uid, systemid, targetsystemid, privKey, pubKey):
        if uid == None or systemid == None or targetsystemid == None or privKey == None or pubKey == None:
            return False
        query = "INSERT INTO systems(uid, systemid, targetsystemid, privKey, pubKey) VALUES (?, ?, ?, ?, ?)"
        result = Query(query, (uid, systemid, targetsystemid, privKey, pubKey,))
        return result

    def UpdateInformation(self, name, hostip, architecture, cpu_name, kernel_name, kernel_version, ram_size, distribution_name, distribution_version, targetsystemId):
        query = "UPDATE systems SET name=?, hostip=?, architecture=?, cpu_name=?, kernel_name=?, kernel_version=?, ram_size=?, distribution_name=?, distribution_version=?, updateRequired=0 WHERE targetsystemid=?"
        result = Query(query, (name, hostip, architecture, cpu_name, kernel_name, kernel_version, ram_size, distribution_name, distribution_version, targetsystemId,))
        return result

    def SetRequireUpdate(self, uid):
        query = "UPDATE systems SET updateRequired=(SELECT intervals FROM registerkey WHERE uid=?) WHERE uid=?"
        result = Query(query, (uid, uid,))
        return result


