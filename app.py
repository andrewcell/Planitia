import json

from flask import Flask, jsonify, request, render_template
from werkzeug.contrib.fixers import ProxyFix
import mysql
import encrypt
import string
import random
import configuration as config
import datetime

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

v = 6


def generateString(size=56, includeNumber=False):
    letters = string.ascii_letters
    if includeNumber:
        letters = letters + string.digits

    return ''.join(random.choice(letters) for i in range(size))


@app.route('/admin/login')
def login():
    return '<link href="https://fonts.googleapis.com/css?family=IM+Fell+Great+Primer+SC|Zhi+Mang+Xing&display=swap" rel="stylesheet"> <style>body { font-family: "IM Fell Great Primer SC", serif; } .cn {  font-family: "Zhi Mang Xing", cursive;}</style><h1>Congratulation! You are very close to hack this website!</h1><h1 class="cn">恭喜你！ 您非常接近破解该网站！</h1><input type="hidden" name="_csrf" value="hi"></input><input type="button" value="Click here to finish your hacking!"></input>'


@app.route('/planitia/register', methods=["POST"])
def register():
    data = request.get_data()
    # data2 = request.form["hello"]
    if len(data) < 1 or data == "" or data == None:
        return jsonify({"code": 400, "comment": "bad request"})
    if not request.form["Hello"] == "Mars World":
        return jsonify({"code": 400, "comment": "wrongproduct"})
    if not request.form["v"] == str(v):
        return jsonify({"code": 400, "comment": "versionmismatch"})

    registerkey = mysql.RegisterKey()
    key = registerkey.SelectBy("password", request.form["password"])
    if not key:
        return jsonify({"code": 401, "comment": "unauthorized"})
    keypair = encrypt.generatePrivateKey(4096)
    publickey = encrypt.PublicKeyToPEM(keypair)
    systemId = "avc" + generateString()
    targetSystemId = generateString()
    systems = mysql.System()
    systems.Insert(key["uid"], systemId, targetSystemId, encrypt.PrivateKeyToPEM(keypair), publickey)
    if not 'intervals' in key:
        key["intervals"] = 3
    return jsonify({"code": 200, "comment": "success",
                    "data": {"publicKey": publickey, "systemId": targetSystemId, "intervals": key["intervals"]}})


@app.route('/planitia/sync', methods=["POST"])
def sync():
    system = mysql.System()
    syncdata = mysql.SyncData()
    result = system.Select("targetsystemid", request.form["systemid"])[0]
    if result == None or result == ():
        return jsonify({"code": 400, "comment": "notregistered"})
    if not request.form["v"] == str(v):
        return jsonify({"code": 400, "comment": "versionmismatch"})
    decrypted = encrypt.decryptData(request.form["data"], result["privKey"])
    if request.form["task"] == "sync":
        syncdata.Insert(result["uid"], result["id"], result["systemid"], decrypted["cpu_usage"], decrypted["ram_usage"],
                        decrypted["localip"], "00:00:00:00:00:00", decrypted["network_usage"]["sent"],
                        decrypted["network_usage"]["recv"], decrypted["network_speed_send"],
                        decrypted["network_speed_receive"], decrypted["disk_read"], decrypted["disk_write"],
                        decrypted["datetime"])
    elif request.form["task"] == "information":
        ip = request.remote_addr
        system.UpdateInformation(decrypted["name"], ip, decrypted["architecture"], decrypted["cpu_name"],
                                 decrypted["kernel_name"], decrypted["kernel_version"], decrypted["ram_size"],
                                 decrypted["distribution"]["name"], decrypted["distribution"]["version"],
                                 request.form["systemid"])
    if not result["updateRequired"] == None and result["updateRequired"] >= 1:
        return jsonify({"code": 305, "comment": "requireupdate", "data": result["updateRequired"]})
    return jsonify({"code": 200, "comment": "success"})


if config.config["jupiter"]:
    import mongodb
    import hashlib

    token = dict()
    internalerror = {"code": 500, "comment": "internalservererror"}
    unauthorized = {"code": 400, "comment": "unauthorized"}
    requirefieldempty = {"code": 400, "comment": "requiredfieldempty"}


    def insertLogin(id, newToken):
        preventMultipleLogin(id)
        token[newToken] = {
            "id": str(id),
            "expire": datetime.datetime.now() + datetime.timedelta(hours=1)
        }


    def preventMultipleLogin(id):
        for key, value in list(token.items()):
            if value["id"] == id:
                token.pop(key, None)


    def checkLogin(newToken):

        if not newToken in token:
            return False
        else:
            if datetime.datetime.now() > token[newToken]["expire"]:
                token.pop(newToken, None)
            return token[newToken]


    def generateEncrypted(plainText, Salt, hash="SHA512"):
        if hash == "SHA512":
            return hashlib.sha512((plainText + Salt).encode()).hexdigest()


    mongo = mongodb.MongoDB()
    if config.config["test"]:
        allowedMethods = ["GET", "POST"]
        html = True


        @app.route("/", methods=["GET"])
        def root():
            return """
                <link href="https://fonts.googleapis.com/css?family=Mitr&display=swap" rel="stylesheet">
                <style> body { font-family: 'Mitr', sans-serif; } </style> 
                <h1>Jupiter Test Menu</h1>
                <ul>
                    <li><a href="/jupiter/login">Login</a></li>
                    <li><a href="/jupiter/register">Register</a></li>
                    <li><a href="/jupiter/systems">Systems</a></li>
                    <li><a href="/jupiter/getconfig">Configuration</a></li>
                </ul>
            """
    else:
        allowedMethods = ["POST"]
        html = False


    def returnData():
        if request.headers.get("Content-Type") == "application/json":
            return request.get_json(), True
        else:
            if html:
                return request.form, False
            else:
                return False, False


    def removeFieldsRegisterKey(registerkey):
        registerkey.pop("id", False)
        registerkey.pop("uid", False)
        registerkey.pop("DateTime", False)
        registerkey.pop("OSType", False)
        return registerkey


    def login(username, password):
        encrypted = generateEncrypted(password, config.config["jupiter_salt"])
        user = mongo.findAccount(username, encrypted)
        if user is None:
            raise Exception
        _token = generateString(64, True)
        insertLogin(user["_id"], _token)
        verify = checkLogin(_token)
        return verify, _token, user


    def register(username, password, first, last, email, useragent, remoteip):
        try:
            encrypted = generateEncrypted(password, config.config["jupiter_salt"])
            newAccountId = mongo.newAccount(username=username,
                                            password=encrypted,
                                            firstname=first,
                                            lastname=last,
                                            email=email,
                                            ip=remoteip,
                                            useragent=useragent)

            return newAccountId
        except:
            pass


    @app.route('/jupiter/login', methods=allowedMethods)
    def jupiter_login():
        if request.method == 'POST':
            try:
                data, JSON = returnData()
                newToken, newTokenKey, user = login(data["username"], data["password"])
                if JSON:
                    return jsonify({"code": 200, "comment": "success",
                                    "data": {"token": newTokenKey, "expire": newToken["expire"]}})
                else:
                    return render_template("logintest.html", title="Login", user=user, token=newTokenKey,
                                           token_expire=newToken["expire"])
            except KeyError:
                return jsonify(requirefieldempty)
            except Exception:
                return jsonify({"code": 401, "comment": "usernotfound"})

        else:
            return render_template('logintest.html', title='Login')


    @app.route('/jupiter/register', methods=allowedMethods)
    def jupiter_register():
        if request.method == "POST":
            ua = request.headers.get('User-Agent')
            remoteip = request.remote_addr
            try:
                data, JSON = returnData()
                accountId = register(username=data["username"],
                                     password=data["password"],
                                     first=data["first"],
                                     last=data["last"],
                                     email=data["email"],
                                     useragent=ua,
                                     remoteip=remoteip)
                if not JSON:
                    return render_template("register.html", title="Register", new=accountId)
                else:
                    return jsonify({"code": 200, "comment": "success"})

            except:
                return jsonify(requirefieldempty)
        else:
            return render_template("register.html", title="Register")


    @app.route("/jupiter/systems", methods=allowedMethods)
    def jupiter_systems():
        if request.method == "POST":
            try:
                system = mysql.System()
                data, JSON = returnData()

                if not data["token"] in token:
                    return jsonify(unauthorized)

                systems = system.Select("uid", token[data["token"]]["id"])
                if JSON:
                    return jsonify(systems)
                else:
                    return render_template("systems.html", systems=systems)
            except Exception as e:
                print(e)
                return jsonify(internalerror)
        else:
            return render_template("systems.html")


    @app.route("/jupiter/setconfig", methods=["POST"])
    def jupiter_setconfig():
        if request.method == "POST":
            try:
                registerkey = mysql.RegisterKey()
                data, JSON = returnData()

                if not checkLogin(data["token"]): return jsonify(unauthorized)
                uid = token[data["token"]]["id"]
                if not ("type" in data and "value" in data):
                    return jsonify(requirefieldempty)
                _type = data["type"]

                foundKey = registerkey.SelectBy("uid", uid)
                interval = 3
                password = generateString(8)
                if _type == "password":
                    password = data["value"]
                    if "intervals" in foundKey:
                        interval = foundKey["intervals"]
                    if not registerkey.checkPasswordAvailable(data["value"]):
                        return jsonify({"code": 200, "comment": "passwordalreadyinuse"})
                elif _type == "interval":
                    interval = data["value"]
                    if "password" in foundKey:
                        password = foundKey["password"]
                registerkey.Update(uid, password, interval)

                if JSON:
                    return jsonify({"code": 200, "comment": "success"})
                else:
                    return render_template("config.html", success=True)

            except Exception as e:
                print(e)
                return jsonify(internalerror)


    @app.route("/jupiter/getconfig", methods=allowedMethods)
    def jupiter_getconfig():
        if request.method == "POST":
            try:
                registerkey = mysql.RegisterKey()
                data, JSON = returnData()
                received_token = data["token"]

                if not checkLogin(received_token): return jsonify(unauthorized)
                result = registerkey.SelectBy("uid", token[received_token]["id"])
                if JSON:
                    return jsonify(removeFieldsRegisterKey(result))
                else:
                    return render_template("config.html", data=result)

            except Exception as e:
                print(e)
                return jsonify(internalerror)
        else:
            return render_template("config.html")


    @app.route("/jupiter/requestinformationdata", methods=["POST"])
    def jupiter_requestinformationdata():
        try:
            data, JSON = returnData()
            systems = mysql.System()
            if not "token" in data:
                return jsonify(requirefieldempty)
            if not checkLogin(data["token"]): return jsonify(unauthorized)
            uid = token[data["token"]]["id"]
            result = systems.SetRequireUpdate(uid)
            return jsonify({"code": 200, "comment": "success"})
        except Exception as e:
            print(e)
            return jsonify(internalerror)

if __name__ == '__main__':
    app.run(debug=True)
