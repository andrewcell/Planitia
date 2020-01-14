from flask import Flask, jsonify, request, render_template

import mysql
import encrypt
import string
import random
import configuration as config


app = Flask(__name__)

v = 6

def generateString(size=56):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(size))

@app.route('/')
def hello_world():
    return "Hello.."

@app.route('/admin/login')
def login():
    return '<link href="https://fonts.googleapis.com/css?family=IM+Fell+Great+Primer+SC|Zhi+Mang+Xing&display=swap" rel="stylesheet"> <style>body { font-family: "IM Fell Great Primer SC", serif; } .cn {  font-family: "Zhi Mang Xing", cursive;}</style><h1>Congratulation! You are very close to hack this website!</h1><h1 class="cn">恭喜你！ 您非常接近破解该网站！</h1><input type="hidden" name="_csrf" value="hi"></input><input type="button" value="Click here to finish your hacking!"></input>'

@app.route('/planitia/register', methods=["POST"])
def register():
    data = request.get_data()
    #data2 = request.form["hello"]
    if len(data) < 1 or data == "" or data == None:
        return jsonify({"code": 400, "comment": "bad request"})
    if not request.form["Hello"] == "Mars World":
        return jsonify({"code": 400, "comment": "wrongproduct"})
    if not request.form["v"] == str(v):
        return jsonify({"code": 400, "comment": "versionmismatch"})

    registerkey = mysql.RegisterKey()
    key = registerkey.Select(request.form["password"])
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
    return jsonify({"code": 200, "comment": "success", "data": {"publicKey": publickey, "systemId": targetSystemId, "intervals": key["intervals"]}})


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
        syncdata.Insert(result["uid"], result["id"], result["systemid"], decrypted["cpu_usage"], decrypted["ram_usage"], decrypted["localip"], "00:00:00:00:00:00", decrypted["network_usage"]["sent"], decrypted["network_usage"]["recv"], decrypted["network_speed_send"], decrypted["network_speed_receive"], decrypted["disk_read"], decrypted["disk_write"], decrypted["datetime"])
    elif request.form["task"] == "information":
        ip = request.remote_addr
        system.UpdateInformation(decrypted["name"], ip, decrypted["architecture"], decrypted["cpu_name"], decrypted["kernel_name"], decrypted["kernel_version"], decrypted["ram_size"], decrypted["distribution"]["name"], decrypted["distribution"]["version"], request.form["systemid"])
    if not result["updateRequired"] == None and result["updateRequired"] >= 1:
        return jsonify({"code": 305, "comment": "requireupdate", "data": result["updateRequired"]})
    return jsonify({"code": 200, "comment": "success"})

if config.config["jupiter"]:
    import mongodb
    import hashlib
    def generateEncrypted(plainText, Salt, hash="SHA512"):
        if hash == "SHA512":
            return hashlib.sha512((plainText + Salt).encode()).hexdigest()

    mongo = mongodb.MongoDB()
    if config.config["test"]:
        @app.route('/jupiter/login', methods=["GET", "POST"])
        def jupiter_login():
            if request.method == 'POST':
                encrypted = generateEncrypted(request.form["password"], config.config["jupiter_salt"])
                user = mongo.findAccount(request.form["username"], encrypted)
                return render_template("logintest.html", title="Login", user=user)
            else:
                    return render_template('logintest.html', title='Login')

        @app.route('/jupiter/register', methods=["GET", "POST"])
        def jupiter_register():
            if request.method == "POST":
                encrypted = generateEncrypted(request.form["password"], config.config["jupiter_salt"])
                newAccountId = mongo.newAccount(username=request.form["username"],
                                                password=encrypted,
                                                firstname=request.form["first"],
                                                lastname=request.form["last"],
                                                email=request.form["email"],
                                                ip=request.remote_addr,
                                                useragent=request.headers.get('User-Agent'))
                try:
                    return render_template("register.html", title="Register", new=newAccountId)
                except Exception as e:
                    return render_template("register.html", title="Register", error=e)
            else:
                return render_template("register.html", title="Register")

if __name__ == '__main__':
    app.run()
