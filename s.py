# # # Create a backend api to check username and password
# # # {'username': 'maddy', 'password':'12345'}

# # @api.route('/loginAPI',methods=['POST','GET'])
# # def loginAPI():
# #     json=request.get_json()
# #     username=json['username']
# #     password=json['password']
# #     print(username,password)
# #     for i in collection.find({'username':username,'password':password}):
# #         return jsonify('{"message":"you are authorised"}')
# #     return jsonify('{"message":"you are not authorised"}')

# @api.route('/login',methods=['POST','GET'])
# def login():
#     gname=request.form['gname']
#     gpassword=request.form['gpassword']
#     print(gname,gpassword)
#     encoded_body = json.dumps({
#                      "username":gname,
#                      "password":gpassword
#                  })
#     http=urllib3.PoolManager()
#     response=http.request('post','http://127.0.0.1:9001/loginAPI',headers={'Content-Type':'application/json'},
#                  body=encoded_body)
#     data = json.loads(response.data.decode('utf-8'))
#     data = json.loads(data)
#     print(data)
#     if data['message']=='you are authorised':
#         session['username'] = gname
#         return redirect(url_for('dashboardPage'))
#     return render_template('index.html',status=data['message'])