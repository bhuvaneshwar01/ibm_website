from flask import Flask, render_template
import ibm_db
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '01845a0438c36160cbe978ea'
user_id = 0
try:
    # conn = ibm_db.connect("bludb","jbg49873","CWnz9f65Zdaixq")
    conn = ibm_db.connect(
        'DATABASE=bludb;HOSTNAME=b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=31249;PROTOCOL=TCPIP;UID=jbg49873;PWD=CWnz9f65Zdaixqgw;Security=SSL;SSLSecurityCertificate=DigiCertGlobalRootCA.crt',
        '', '')
except:
    print("[+]\tConnecting to DB2 [FAIL] : ", ibm_db.conn_errormsg())
else:
    print("[+]\tConnecting to DB2 [SUCCESS]")
bcrypt = Bcrypt(app)
from components import routes
