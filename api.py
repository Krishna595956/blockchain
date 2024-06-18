from flask import *
from pymongo import MongoClient
import hashlib
import datetime
import urllib3

cluster=MongoClient('mongodb+srv://Krishna123:1234567890@cluster0.i5fh2ng.mongodb.net/')
db=cluster['blockchain']
users=db['users']
ledgers=db['ledger']
requests=db['requests']
words=db['words']
challenge=db['challenge']
image=db['image']

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
    data=request.form['data']
    category=request.form['category']
    if requests.count_documents({ })>0:
        return render_template('gasdetails.html',status="Request already added")
    if category=="words":
        data1=words.find()
        data1=list(data1)[0]
        challenge.insert_one(data1)
    elif category=="image":
        data=image.find()
        data=list(data)[0]
        challenge.insert_one(data)
    print(list(data))
    requests.insert_one({'gasrequired':gr,'gasrewarded':grew,'data':data})
    return render_template('gasdetails.html',status='Request added successfully')

@app.route('/viewrequests')
def viewreq():
    data=requests.find()
    try:
        if session['status']==0:
            return render_template('denied.html',response="You have denied the current request and please wait for the next request.")
        return render_template('requests.html',data=data)
    except:
        return render_template('requests.html',data=data)

@app.route('/accepted')
def accept():
    return render_template('challenge.html')

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
    if c!=session['ledgercount']:
        data=ledgers.find()
        data=list(data)
        data.reverse()
        return render_template('userledger.html',status="Block added successfully",data=data)
    data=datetime.datetime.now()
    hasher = hashlib.sha256()
    hasher.update(str(data).encode()) 
    thash=hasher.hexdigest()
    dataValue="hello"+str(data)
    hasher.update(dataValue.encode())
    dhash=hasher.hexdigest()
    res=ledgers.find_one({'blockid':c-1})
    
    phash=res['dhash']
    ledgers.insert_one({
        'thash':thash,
        'dhash':dhash,
        'phash':phash,
        'blockid':c,
        'addedby': session['name']
    })
    reward=requests.find()
    reward=list(reward)[0]['gasrewarded']
    users.update_one({"username":session['name']},{"$inc":{"coins":int(reward)}})    
    data=challenge.find()
    data=list(data)[0]['category']
    requests.drop()
    challenge.drop()
    if data=="words":
        data1=words.find()
        words.delete_one(list(data1)[0])
    elif data=="image":
        data1=image.find()
        image.delete_one(list(data1)[0])
    data=ledgers.find()
    data=list(data)
    data.reverse()
    return render_template('userledger.html',status="Block added successfully",data=data)

@app.route('/reject')
def reject():
    session['status']=0
    count=ledgers.count_documents({ })
    session['ledgercount']=count
    return render_template('denied.html',response="You have denied the current request and please wait for the next request.")

@app.route('/wordscategory',methods=['post'])
def wordscategory():
    desc=request.form['description']
    letters=request.form['letters']
    answer=request.form['answer']
    a=answer.split(',')
    words.insert_one({"desc":desc,"letters":letters,"answer":a,"category":"words"})
    return render_template('wordscategory.html',status="Challenge added successfully",count=len(a))

@app.route('/acceptrequest')
def acceptrequest():
    try:
        c=ledgers.count_documents({ })
        session['ledgercount']=c
        data=challenge.find()
        data=list(data)[0]
        charge=requests.find()
        charge=list(charge)[0]['gasrequired']
        users.update_one({"username":session['name']},{"$inc":{"coins":-(int(charge))}})
        if data['category']=="words":
            data1=challenge.find()
            session['data1']=list(data1)[0]['answer']
            return render_template('wordschallenge.html',data=data,count=len(session['data1']))
        elif data['category']=='image':
            a=data['urldata']
            return render_template('imagechallenge.html',urldata=a)
        return "hii"
    except:
        return render_template('requests.html',status="Request already satisfied.")
  
@app.route('/verifywords',methods=['post'])
def verifywords():
    try:
        data=challenge.find()
        data=list(data)[0]
        z=session['data1']
        print(z)
        a=request.form['answer']
        if a in z:
            z.remove(a)
            session['data1']=z
            if len(session['data1'])==0:
                return redirect('/addblock')
            return render_template('wordschallenge.html',count=len(z),data=data)
        return render_template('wordschallenge.html',status="Try another word",count=len(z),data=data)
    except:
        data=ledgers.find()
        data=list(data).reverse()
        return render_template('ledger.html',status="This block is already added",data=data)
    
@app.route('/verifyimage',methods=['post'])
def verifyimage():
    try:
        ans=request.form['answer']
        data=challenge.find()
        answer=list(data)[0]['answer']
        data=challenge.find()
        urldata=list(data)[0]['urldata']
        if ans==answer:
            return redirect('/addblock')
        return render_template('imagechallenge.html',status="Your answer is incorrect",urldata=urldata)
    except:
        data=ledgers.find()
        data=list(data)
        data.reverse()
        return render_template('/userledger.html',status="Block already added",data=data)

@app.route('/addimagechallenge',methods=['post'])
def addimagecha():
    urldata=request.form['imageurl']
    answer=request.form['answer']
    image.insert_one({"urldata":urldata,'answer':answer,"category":"image"})
    return render_template('imagecategory.html',status="challenge added successfully")

@app.route('/nextrequest')
def nextrequest():
    c=ledgers.count_documents({ })
    print(c)
    print(session['ledgercount'])
    if c==session['ledgercount']:
        return render_template('denied.html',response="You have denied the current request and please wait for the next request.")
    session['status']=1
    return redirect('/viewrequests')

@app.route('/status')
def stat():
    session['status']=1
    return redirect('/userhome')

@app.route('/leaderboard')
def leaderboard():
    data=users.find()
    data=list(data)
    for i in range(len(data)-1):
        if data[i]['coins']<data[i+1]['coins']:
            data[i],data[i+1]=data[i+1],data[i]
    return render_template('leaderboard.html',data=data)

@app.route('/loginAPI',methods=['POST','GET'])
def loginAPI():
    json=request.get_json()
    username=json['username']
    password=json['password']
    print(username,password)
    for i in users.find({'username':username,'password':password}):
        return jsonify('{"message":"you are authorised"}')
    return jsonify('{"message":"you are not authorised"}')

@app.route('/loginuser',methods=['POST','GET'])
def loginuser():
    gname=request.form['username']
    gpassword=request.form['password']
    encoded_body = json.dumps({
                     "username":gname,
                     "password":gpassword
                 })
    http=urllib3.PoolManager()
    response=http.request('post','http://127.0.0.1:5000/loginAPI',headers={'Content-Type':'application/json'},
                 body=encoded_body)
    data = json.loads(response.data.decode('utf-8'))
    data = json.loads(data)
    if data['message']=='you are authorised':
        session['name'] = gname
        return redirect(url_for('userhome'))
    return render_template('login.html',status=data['message'])

@app.route('/registerAPI',methods=['post'])
def registerAPI():
    json=request.get_json()
    username=json['username']
    password=json['password']
    rpassword=json['rpassword']
    data=users.find_one({'username':username})
    print(username)
    if not data:
        if password!=rpassword:
            return jsonify('{"message":"0"}')
        users.insert_one({"username":username,"password":password,'flag':0,'coins':1000,'solved':0,"status":0})
        return jsonify('{"message":"1"}')
    return jsonify('{"message":"2"}')

@app.route('/registeruser',methods=['post','get'])
def registeruser():
    username=request.form['username']
    password=request.form['password']
    rpassword=request.form['rpassword']
    encoded_body = json.dumps({
                     "username":username,
                     "password":password,
                     "rpassword":rpassword
                 })
    http=urllib3.PoolManager()
    response=http.request('post','http://127.0.0.1:5000/registerAPI',headers={'Content-Type':'application/json'},
                 body=encoded_body)
    data = json.loads(response.data.decode('utf-8'))
    data = json.loads(data)
    if data['message']=='1':
        return render_template('register.html',status='Registration successful')
    elif data['message']=='0':
        return render_template('register.html',status='Password incorrect')
    else:
        return render_template('register.html',status="Username already exists")
    
@app.route('/adminloginAPI',methods=['post'])
def adminloginAPI():
    json=request.get_json()
    username=json['username']
    password=json['password']
    if username=='admin' and password=='1234567890':
        return jsonify('{"message":"0"}')
    return jsonify('{"message":"1"}')

@app.route('/adminlogin',methods=['post','get'])
def adminlogin():
    username=request.form['username']
    password=request.form['password']
    encoded_body=json.dumps({
        "username":username,
        "password":password
    })
    http=urllib3.PoolManager()
    response=http.request('post','http://127.0.0.1:5000/adminloginAPI',headers={'Content-Type':'application/json'},
                 body=encoded_body)
    data = json.loads(response.data.decode('utf-8'))
    data = json.loads(data)
    if data['message']=="0":
        return redirect(url_for('adminhome'))
    else:
        return render_template('adminlogin.html',status="Invalid credentials")
    
if __name__=='__main__':
    app.run(debug=True)

