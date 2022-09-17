from flask import Flask, render_template, request, redirect, make_response
import hashlib
import pymongo
import time

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["sistema_de_login"]
usersdb = mydb["users"]
sessionsdb = mydb["sessions"]
patientsdb = mydb["patients"]

app = Flask(__name__)

@app.route("/add")
def addpatients():
    patientsdb.insert_many([
        {"name": "joaozinho","age": 12},
        {"name": "pedrinho","age": 18},
        {"name": "marcos","age": 23},
        {"name": "paulo","age": 15},
        {"name": "igor","age": 32},
        ])
    return "adicionado"

def getPatients():
    result = []
    resultdb = patientsdb.find()
    for patient in resultdb:
        result.append(patient)
    return result

def getUsername(token):
    result = sessionsdb.find({"authorization": token})
    return result[0]["username"]

@app.route("/", methods = {"GET"})
def home():
    if "authorization" in request.cookies:
        return render_template("home.html", username=getUsername(request.cookies.get("authorization")),patients=getPatients())
    else:
        return redirect("/login")

@app.route("/patients", methods = {"GET", "POST"})
def patients():
    #authorization = request.cookies.get("authorization")
    #if request.cookies.get("authorization"):
    if request.method == "GET":
        return render_template("newpatient.html")
    elif request.method == "POST":
        patientName = request.form.get("name")
        patientAge = request.form.get("age")
        return {"name": patientName, "age": patientAge}
    else:
        pass

@app.route("/login", methods = {"GET", "POST"})
def login():
    if "authorization" in request.cookies:
        return redirect("/")
    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        result =  usersdb.find_one({"username": username})
        if result:
            if result["password"] == hashlib.sha256(bytes(password, encoding="utf8")).hexdigest():
                res = make_response(redirect("/"))
                authorization = hashlib.sha256(bytes(str(time.time()), encoding="utf8")).hexdigest()
                res.set_cookie("authorization", authorization, 1000)
                sessionsdb.insert_one({"username": username, "authorization": authorization})
                return res
        return render_template("login.html", message="Login ou senha errado.")

@app.route("/logoff", methods = {"GET"})
def logoff():
    if request.cookies.get("authorization"):
        res = make_response(redirect("/"))
        res.set_cookie("authorization", "", 0)
    return res

@app.route("/register", methods = {"GET", "POST"})
def register():
    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":

        username = request.form.get("username")
        if len(username) == 0:
            return render_template("register.html", message="Insira um username.")

        result =  usersdb.find_one({"username": username})

        if result:
            return render_template("register.html", message="Já existe um usuário com esse nome.")
        password = request.form.get("password")
        if len(password) == 0:
            return render_template("register.html", message="Insira uma senha.")
        confirmpassword = request.form.get("confirmpassword")

        if password != confirmpassword:
            return render_template("register.html", message="A senhas não coincidem.")

        hashedpassword = hashlib.sha256(bytes(password, encoding="utf8")).hexdigest()
        x = {"username": username, "password": hashedpassword}

        usersdb.insert_one(x)

        return redirect("/login")

app.run("localhost", 8080)
