from flask import Flask, render_template
import ibm_db
from flask_bcrypt import Bcrypt
from sqlalchemy import *
from flask_sqlalchemy import  SQLAlchemy
import ibm_db_sa
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '01845a0438c36160cbe978ea'
app.config['SQLALCHEMY_DATABASE_URI'] = 'db2+ibm_db://jbg49873:CWnz9f65Zdaixqgw@b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud:31249/bludb'

try:
    db2 = SQLAlchemy(app)
    conn = ibm_db.connect(
        'DATABASE=bludb;HOSTNAME=b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=31249;PROTOCOL=TCPIP;UID=jbg49873;PWD=CWnz9f65Zdaixqgw;Security=SSL;SSLSecurityCertificate=DigiCertGlobalRootCA.crt',
        '', '')
except:
    print("[+]\tConnecting to DB2 [FAIL] : ", ibm_db.conn_errormsg())
else:
    print("[+]\tConnecting to DB2 [SUCCESS]")
bcrypt = Bcrypt(app)
# login_manager = LoginManager(app)
# login_manager.init_app(app)



from components import routes
