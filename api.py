from flask import *
from pymongo import MongoClient
import hashlib
import datetime

cluster=MongoClient('mongodb+srv://Krishna123:1234567890@cluster0.i5fh2ng.mongodb.net/')
db=cluster['blockchain']
users=db['users']
ledgers=db['ledger']
requests=db['requests']
words=db['words']
challenge=db['challenge']

app=Flask(__name__)

app.secret_key='reddy'

@app.route('/')
def confirm():
    return render_template('confirm.html')

@app.route('/user')
def default():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/admin')
def admin():
    return render_template('/adminlogin.html')

@app.route('/adminhome')
def adminhome():
    return render_template('admindashboard.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/userhome')
def userhome():
    return render_template('dashboard.html')

@app.route('/request')
def requ():
    return render_template('gasdetails.html')

@app.route('/addimage')
def addimage():
    return render_template('imagecategory.html')

@app.route('/addwords')
def addwords():
    return render_template('wordscategory.html')

@app.route('/addrequest',methods=['post'])
def addrequest():
    gr=request.form['gasrequired']
    grew=request.form['gasrewarded']
    session['data']=request.form['data']
    category=request.form['category']
    session['category']=category
    if requests.count_documents({ })>0:
        return render_template('gasdetails.html',status="Request already added")
    if category=="words":
        data=words.find()
        data1=list(data)[0]
        challenge.insert_one(data1)
    requests.insert_one({'gasrequired':gr,'gasrewarded':grew})
    return render_template('gasdetails.html',status='Request added successfully')

@app.route('/viewrequests')
def viewreq():
    data=requests.find()
    return render_template('requests.html',data=data)

@app.route('/accepted')
def accept():
    return render_template('challenge.html')
    
@app.route('/adminlogin',methods=['post'])
def adminlogin():
    username=request.form['username']
    password=request.form['password']
    if username=='admin' and password=='1234567890':
        return render_template('admindashboard.html')
    return render_template('adminlogin.html',status='Invalid credentials')

@app.route('/registeruser',methods=['post'])
def registeruser():
    username=request.form['username']
    password=request.form['password']
    rpassword=request.form['rpassword']
    data=users.find_one({'username':username})
    print(username)
    if not data:
        if password!=rpassword:
            return render_template('register.html',status='Passwords do not match')
        users.insert_one({"username":username,"password":password,'flag':0,'coins':1000,'solved':0})
        return render_template('register.html',status="Registration succesful")
    return render_template('register.html',status="Username already exists")

@app.route('/resetpassword',methods=['post'])
def reset():
    old=request.form['currentpassword']
    new=request.form['newpassword']
    rnew=request.form['rpassword']
    user1=users.find_one({'username':session['name']})
    if user1['password']==old:
        if new==rnew:
            users.update_one({'username':session['name']},{"$set":{'password':new}})
            users.update_one({'username':session['name']},{"$set":{'flag':1}})
            return render_template('dashboard.html')
        else:
            return render_template('resetpassword.html',status='Passwords do not match')
    return render_template('resetpassword.html',status='Incorrect current password')

@app.route('/loginuser',methods=['post'])
def loginuser():
    username=request.form['username']
    password=request.form['password']
    data=users.find_one({'username':username})
    if data:
        if data['password']==password and data['flag']==0:
            session['name']=username
            return render_template('resetpassword.html')
        elif data['password']==password:
            session['name']=username
            return render_template('dashboard.html')
        else:
            return render_template('login.html',status='Incorrect password')
    return render_template('login.html',status="User does not exist")

@app.route('/ledgerdata')
def ledgerdata():
    data=ledgers.find()
    data=list(data)
    data.reverse()
    return render_template('ledger.html',data=data)

@app.route('/userledgerdata')
def ledgerdata1():
    data=ledgers.find()
    data=list(data)
    data.reverse()
    return render_template('userledger.html',data=data)

@app.route('/logout')
def logout():
    try:
        session['name']
        session['name']=''
        return render_template('confirm.html')
    except:
        return render_template('confirm.html')

@app.route('/addblock')
def ledgerda():
    c=ledgers.count_documents({ })
    data=datetime.datetime.now()
    hasher = hashlib.sha256()
    hasher.update(str(data).encode()) 
    thash=hasher.hexdigest()
    print(thash)
    dataValue="hello"+str(data)
    hasher.update(dataValue.encode())
    dhash=hasher.hexdigest()
    print(dhash)
    res=ledgers.find_one({'blockid':c-1})
    
    phash=res['dhash']
    ledgers.insert_one({
        'thash':thash,
        'dhash':dhash,
        'phash':phash,
        'blockid':c,
        'addedby':'krishna'
    })
    data=users.find_one({'username':session['name']})
    # ledgers.update_one({''},{'$inc',{'solved':1}})
    return 'Block added successfully'

@app.route('/deny')
def deny():
    return redirect('/viewrequests')

@app.route('/wordscategory',methods=['post'])
def wordscategory():
    desc=request.form['description']
    letters=request.form['letters']
    answer=request.form['answer']
    print(desc,letters,answer)
    a=answer.split(',')
    if challenge.count_documents({ })>0:
        return render_template('wordscategory.html',status="Challenge already added")
    words.insert_one({"desc":desc,"letters":letters,"answer":a,"category":"words"})
    return render_template('wordscategory.html',status="Challenge added successfully",count=len(a))

@app.route('/acceptrequest')
def acceptrequest():
    data=challenge.find()
    data1=challenge.find()
    data=list(data)[0]
    session['data1']=list(data1)[0]['answer']
    if data['category']=="words":
        return render_template('wordschallenge.html',data=data,count=len(session['data']))
    return "hii"

@app.route('/verifywords',methods=['post'])
def verifywords():
    data=challenge.find()
    data=list(data)[0]
    z=session['data1']
    print(z)
    a=request.form['answer']
    if a in z:
        z.remove(a)
        print(z)
        return render_template('wordschallenge.html',count=len(z),data=data)
    return render_template('wordschallenge.html',status="Try another word",count=len(a),data=data)

if __name__=='__main__':
    app.run(debug=True)

