#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from bson.json_util import dumps
from flask import Blueprint, jsonify,session, request, redirect, url_for, render_template, json, flash
from flask.ext.login import current_user, login_required
from rex import db, lm
from rex.models import user_model, deposit_model, history_model, invoice_model
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
from time import gmtime, strftime
import time
import json
import os
from validate_email import validate_email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from bson import ObjectId, json_util
import codecs
from random import randint
from hashlib import sha256
import string
import random
import urllib
import urllib2
import base64
import onetimepass
import sys
import collections
import requests
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
sys.setrecursionlimit(10000)
digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


__author__ = 'asdasd'

api_ctrl = Blueprint('api', __name__, static_folder='static', template_folder='templates')
UPLOAD_FOLDER = '/statics/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])



def id_generator(size=6, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def to_bytes(n, length):
    s = '%x' % n
    s = s.rjust(length*2, '0')
    s = codecs.decode(s.encode("UTF-8"), 'hex_codec')
    return s

def decode_base58(bc, length):
    n = 0
    for char in bc:
        n = n * 58 + digits58.index(char)
    return to_bytes(n, length)

def check_bc(bc):
    bcbytes = decode_base58(bc, 25)
    return bcbytes[-4:] == sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]

def check_password(pw_hash, password):
        return check_password_hash(pw_hash, password)

def set_password(password):
    return generate_password_hash(password)

def add_customer(datas,p_binary,position):
    customer = db.users.insert(datas)
    customer = db.User.find_one({'_id': ObjectId(customer)})
    if str(position)== 'left':
        db.users.update({"customer_id": p_binary}, { "$set": { "left":customer.customer_id} })
    else:
        db.users.update({"customer_id": p_binary}, { "$set": { "right":customer.customer_id} })
            
    return customer

@api_ctrl.route('/register', methods=['GET', 'POST'])
def register():
    dataDict = json.loads(request.data)

    fullname_code = dataDict['fullname'].lower()

    fullnamess = fullname_code.split(' ')
    fullname = ''
    for i in range(0,len(fullnamess)):
      fullname += fullnamess[i].capitalize()+" "
  
    email = dataDict['email'].lower()
    address = dataDict['address']
    password = dataDict['password']
    p_node = dataDict['p_node']
    p_binary = dataDict['p_binary']
    telephone = dataDict['telephone']
    cmnd = dataDict['cmnd']
    birthday = dataDict['birthday']
    account_horder = dataDict['account_horder'].upper()
    account_number = dataDict['account_number']
    bankname = dataDict['bankname']
    brandname = dataDict['brandname']
    position = dataDict['position']
    localtime = time.localtime(time.time())
    code_active = id_generator()
    customer_id = '%s%s%s%s%s%s'%(localtime.tm_mon,localtime.tm_year,localtime.tm_mday,localtime.tm_hour,localtime.tm_min,localtime.tm_sec)
    check_email = db.User.find_one({'email': email})
    if check_email is not None:
        return json.dumps({
            'status': 'error', 
            'message': 'Email đã được sử dụng. Vui lòng nhập email khác.' 
        })
    else:
        datas = {
          'customer_id' : customer_id,
          'username': email,
          'password': set_password(password),
          'email': email,
          'fullname' : fullname,
          'telephone' : telephone,
          'p_node': p_node,
          'password_transaction' : '',
          'p_binary': p_binary,
          'left': '',
          'right': '',
          'level': 0,
          'level_dh': 0,
          'creation': datetime.utcnow(),
          'total_pd_left' : 0,
          'total_pd_right' : 0,
          'max_out' : 0,
          'total_earn' : 0,
          'total_invest': 0,
          'total_node' : 0,
          'status' : 0,
          'code_active' : code_active,
          'total_max_out': 0,
          'investment' : 0,
          'active_email' : 0,
          'total_receive' : 0,
          'total_pd_lefts' : 0,
          'total_pd_rights' : 0,
          'th_wallet' : 0,
          'dh_wallet' : 0,
          'n_wallet' : 0,
          'ch_wallet' :0,
          'balance_wallet' : 0,
          'address' : address,
          'cmnd' : cmnd,
          'birthday' : birthday,
          'account_horder' : account_horder,
          'account_number' : account_number,
          'bankname' : bankname,
          'brandname' : brandname
        }
        add_customer(datas,p_binary,position)

        return json.dumps({
          'status': 'complete', 
          'customer_id' : customer_id,
          'message': 'Thêm thành viên thành công.' 
        })


@api_ctrl.route('/get-member', methods=['GET', 'POST'])
def get_memberss():

    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    member = db.users.find({'p_node': customer_id}).sort([("creation", -1)])

    #.sort("date_added", -1)

    array = []
    for item in member:
      
      array.append({
        "customer_id" : item['customer_id'],
        "email" : item['email'],
        "fullname" : item['fullname'],
        "telephone" : item['telephone'],
        "dscn" : item['total_node'],
        "date_added" : (item['creation']).strftime('%d/%m/%Y %H:%M:%S ')
      })
    return json.dumps(array)

@api_ctrl.route('/history-withdraw', methods=['GET', 'POST'])
def history_withdraw():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    
    historys = db.withdrawal.find({'uid': customer_id} ).sort([("date_added", -1)])
    array = []
    for item in historys:
      array.append({
        "amount" : item["amount"],
        "date_added" : (item["date_added"]).strftime('%H:%M %d-%m-%Y'),
        "status" : item["status"],
        'account_horder' : item["account_horder"],
        'account_number' : item["account_number"],
        'bankname' : item["bankname"],
        'brandname' : item["brandname"]
      })
    return json.dumps(array)
@api_ctrl.route('/get-history-commision-truche', methods=['GET', 'POST'])
def get_history_commision_truche():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    
    commision = db.historys.find({'$and' : [{'uid': customer_id},{'type' :'referral'}]} ).sort([("date_added", -1)])
    array = []
    for item in commision:
      array.append({
        "amount" : item["amount"],
        "date_added" : (item["date_added"]).strftime('%H:%M %d-%m-%Y'),
        "type" : item["type"],
        "detail" : item["detail"]
      })
    return json.dumps(array)

@api_ctrl.route('/get-history-commision-nhom', methods=['GET', 'POST'])
def get_history_commision_nhom():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    
    commision = db.historys.find({'$and' : [{'uid': customer_id},{'type' :'hoahongcannhanh'}]} ).sort([("date_added", -1)])
    array = []
    for item in commision:
      array.append({
        "amount" : item["amount"],
        "date_added" : (item["date_added"]).strftime('%H:%M %d-%m-%Y'),
        "type" : item["type"],
        "detail" : item["detail"]
      })
    return json.dumps(array)

@api_ctrl.route('/get-history-commision-conghuong', methods=['GET', 'POST'])
def get_history_commision_conghuong():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    
    commision = db.historys.find({'$and' : [{'uid': customer_id},{'type' :'thunhaptrenthunhap'}]} ).sort([("date_added", -1)])
    array = []
    for item in commision:
      array.append({
        "amount" : item["amount"],
        "date_added" : (item["date_added"]).strftime('%H:%M %d-%m-%Y'),
        "type" : item["type"],
        "detail" : item["detail"]
      })
    return json.dumps(array)

@api_ctrl.route('/get-history-commision-thuong', methods=['GET', 'POST'])
def get_history_commision_thuong():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    
    commision = db.historys.find({'$and' : [{'uid': customer_id},{'type' :'thuong'}]} ).sort([("date_added", -1)])
    array = []
    for item in commision:
      array.append({
        "amount" : item["amount"],
        "date_added" : (item["date_added"]).strftime('%H:%M %d-%m-%Y'),
        "type" : item["type"],
        "detail" : item["detail"]
      })
    return json.dumps(array)

@api_ctrl.route('/get-tree', methods=['GET', 'POST'])
def get_tree():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    #customer_id = '320191892857'

    customer_id0 = '' 
    fullname0 = '' 
    email0 = ''
    empty0 = '' 

    customer_id1 = '' 
    fullname1 = ''
    email1 = '' 
    empty1 = ''

    customer_id2 = '' 
    fullname2 = ''
    email2 = '' 
    empty2 = ''

    customer_id3 = '' 
    fullname3 = '' 
    email3 = '' 
    empty3 = '' 

    customer_id4 = '' 
    fullname4 = '' 
    email4 = '' 
    empty4 = '' 

    customer_id5 = '' 
    fullname5 = '' 
    email5 = ''
    empty5 = '' 

    customer_id6 = '' 
    fullname6 = '' 
    email6 = '' 
    empty6 = '' 

    member0 = db.User.find_one({'customer_id': customer_id})
    member = []
    if member0 is not None:
      customer_id0 = member0.customer_id
      fullname0 = member0.fullname
      email0 = member0.email
      empty0 = False
      
      if member0.left != '':
        member1 = db.User.find_one({'customer_id': member0.left})
        
        customer_id1 = member1.customer_id
        fullname1 = member1.fullname
        email1 = member1.email
        empty1 = False

        if member1.left != '':
          member3 = db.User.find_one({'customer_id': member1.left})
          
          customer_id3 = member3.customer_id
          fullname3 = member3.fullname
          email3 = member3.email
          empty3 = False


        else:
          empty3 = True
      
        if member1.right != '':
          member4 = db.User.find_one({'customer_id': member1.right})

          customer_id4 = member4.customer_id
          fullname4 = member4.fullname
          email4 = member4.email
          empty4 = False

        else:
          empty4 = True

      else:
        empty1 = True

      if member0.right != '':
        member2 = db.User.find_one({'customer_id': member0.right})
        
        customer_id2 = member2.customer_id
        fullname2 = member2.fullname
        email2 = member2.email
        empty2 = False

        if member2.left != '':
          member5 = db.User.find_one({'customer_id': member2.left})
          
          customer_id5 = member5.customer_id
          fullname5 = member5.fullname
          email5 = member5.email
          empty5 = False

        else:
          empty5 = True

        if member2.right != '':
          member6 = db.User.find_one({'customer_id': member2.right})
            
          customer_id6 = member6.customer_id
          fullname6 = member6.fullname
          email6 = member6.email
          empty6 = False

        else:
          empty6 = True


      else:
        empty2 = True
      return json.dumps({
          'status': 'complete', 
          'customer_id0' : customer_id0,
          'fullname0' : fullname0,
          'email0' : email0,
          'empty0' : empty0,

          'customer_id1' : customer_id1,
          'fullname1' : fullname1,
          'email1' : email1,
          'empty1' : empty1,

          'customer_id2' : customer_id2,
          'fullname2' : fullname2,
          'email2' : email2,
          'empty2' : empty2,

          'customer_id3' : customer_id3,
          'fullname3' : fullname3,
          'email3' : email3,
          'empty3' : empty3,

          'customer_id4' : customer_id4,
          'fullname4' : fullname4,
          'email4' : email4,
          'empty4' : empty4,

          'customer_id5' : customer_id5,
          'fullname5' : fullname5,
          'email5' : email5,
          'empty5' : empty5,

          'customer_id6' : customer_id6,
          'fullname6' : fullname6,
          'email6' : email6,
          'empty6' : empty6,
          'count_binary_left' : total_binary_left(customer_id),
          'count_binary_right' : total_binary_right(customer_id)

      })
    else:
      return json.dumps({
          'status': 'error'
      })

@api_ctrl.route('/login', methods=['GET', 'POST'])
def login():
    
    dataDict = json.loads(request.data)
    email = dataDict['email'].lower()
    password = dataDict['password'].lower()
      
    user = db.User.find_one({'email': email})
    
    if user is None or check_password(user['password'], password) == False:
        return json.dumps({
          'status': 'error', 
          'message': 'Thông tin đăng nhập không đúng. Vui lòng thử lại!' 
      })
    else:
        return json.dumps({
          'customer_id' : user['customer_id'],
          'status': 'complete', 
          'message': 'Login successfully' 
        })
def total_binary_left(customer_id):
    customer = db.users.find_one({'customer_id': customer_id})
    count_left = 0
    if customer['left'] == '':
        count_left = 0
    else:
        id_left_all = str(customer['left'])+get_id_tree(customer['left'])
        id_left_all = id_left_all.split(',')
        if (len(id_left_all) > 0):
            for yy in id_left_all:
                count_left = count_left + 1
    return count_left

def total_binary_right(customer_id):
    customer = db.users.find_one({'customer_id': customer_id})
    count_right = 0
    if customer['right'] == '':
        count_right = 0
    else:
        id_right_all = str(customer['right'])+get_id_tree(customer['right'])
        id_right_all = id_right_all.split(',')
        if (len(id_right_all) > 0):
            for yy in id_right_all:
                count_right = count_right + 1
    return count_right
@api_ctrl.route('/get-infomation-user', methods=['GET', 'POST'])
def get_infomation_user():

    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    
    user = db.users.find_one({'customer_id': customer_id})

    count_f1 = db.users.find({'$and' : [{'p_node' : customer_id},{'investment':{'$gt': 0 }} ]}).count()


    percent_nhom = 0
    if float(user['total_node']) >= 100:
      percent_nhom = 8
      max_out_level = 500
    if float(user['total_node']) >= 200:
      percent_nhom = 9
      max_out_level = 1000
    if float(user['total_node']) >= 300:
      percent_nhom = 10
      max_out_level = 2000
    if float(user['total_node']) >= 400:
      percent_nhom = 11
      max_out_level = 4000
    if float(user['total_node']) >= 500:
      percent_nhom = 12
      max_out_level = 5000

    query_history = db.historys.find({'$and' : [ {'type': {'$regex': 'hoahongcannhanh'}},{'uid' : customer_id},
      {"date_added" : {
              '$lte' : datetime.utcnow() ,
              '$gt' : datetime.utcnow() - timedelta(days=30)
            }}
    ]})
    amount_hoahongcannhanh = 0
    for x in query_history:
      amount_hoahongcannhanh += float(x['amount'])
      
    data_ticker = db.tickers.find_one({})

    if int(user['level']) == 0:
      danhhieu = 'Thành viên miễn phí'
    if int(user['level']) == 1:
      danhhieu = 'TƯ VẤN VIÊN'
    if int(user['level']) == 2:
      danhhieu = 'TRƯỞNG NHÓM'
    if int(user['level']) == 3:
      danhhieu = 'TRƯỞNG PHÒNG'
    if int(user['level']) == 4:
      danhhieu = 'GIÁM ĐỐC KINH DOANH'
    if int(user['level']) == 5:
      danhhieu = 'GIÁM ĐỐC CẤP CAO'
    if int(user['level']) == 6:
      danhhieu = 'GIÁM ĐỐC MIỀN'
    if int(user['level']) == 7:
      danhhieu = 'VIP'

    if user is not None:
      
      if str(user['password_transaction']) == '':
        status_password_transaction = False
      else:
        status_password_transaction = True

      return json.dumps({
          'status': 'complete', 
          'id' : str(user['_id']),
          'email': user['email'],
          'date_added' : (user['creation']).strftime('%H:%M %d-%m-%Y'),
          'fullname': user['fullname'],
          'telephone' : user['telephone'],
          'birthday' :  '',
          'total_pd_left' : user['total_pd_left'],
          'total_pd_right' : user['total_pd_right'],
          'total_pd_lefts' : user['total_pd_lefts'],
          'total_pd_rights' : user['total_pd_rights'],
          'total_node' : user['total_node'],
          'count_binary_left' : total_binary_left(customer_id),
          'count_binary_right' : total_binary_right(customer_id),
          'count_f1' : count_f1,
          'percent_nhom' : percent_nhom,
          'max_out_nhom' : max_out_level,
          'dstam' : 0,
          'amount_hoahongcannhanh' : amount_hoahongcannhanh,
          'balance_wallet' : user['balance_wallet'],
          'price_rl' : data_ticker['price'],
          'th_wallet' : user['th_wallet'],
          'dh_wallet' : user['dh_wallet'],
          'n_wallet' : user['n_wallet'],
          'ch_wallet' : user['ch_wallet'],
          'danhhieu' : str(danhhieu),
          'status_password_transaction' : status_password_transaction
      })
    else:
      return json.dumps({
          'status': 'error'
      })

@api_ctrl.route('/withdraw-submit', methods=['GET', 'POST'])
def withdraw_submit():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    amount = dataDict['amount']
    account_bank = dataDict['account_bank']
    account_horder = dataDict['account_horder']
    account_number = dataDict['account_number']
    brandname = dataDict['brandname']
    password_transaction = dataDict['password_transaction']

    user = db.User.find_one({'customer_id': customer_id})
    if user is not None:
      data_ticker = db.tickers.find_one({})
      if check_password(user['password_transaction'], password_transaction) == True:
        if float(user['balance_wallet']) >= float(amount):
          
          new_balance_sub = float(user['balance_wallet']) - float(amount)
          db.users.update({ "customer_id" : customer_id }, { '$set': { 'balance_wallet': float(new_balance_sub)} })
          
          data_withdrawal = {
              'uid' : customer_id,
              'fullname' : user['fullname'],
              'account_horder' : account_horder,
              'account_number' : account_number,
              'bankname' : account_bank,
              'brandname' : brandname,
              'amount': float(amount),
              'date_added' : datetime.utcnow(),
              'status' : 0,
              'telephone' : user['telephone']
          }
          db.withdrawal.insert(data_withdrawal)
          return json.dumps({
              'status': 'complete', 
              'message': 'Withdraw successfully' 
          })
        else:
          return json.dumps({
            'status': 'error',
            'message': 'Số dư RL của bạn không đủ' 
          })
      else:
        return json.dumps({
            'status': 'error',
            'message': 'Mật khẩu cấp 2 không đúng' 
        })

      

@api_ctrl.route('/change-password', methods=['GET', 'POST'])
def change_password():
   
    dataDict = json.loads(request.data)
    
    password_new = dataDict['password_new'].lower()
    customer_id = dataDict['customer_id'].lower()

    user = db.User.find_one({'customer_id': customer_id})

    if user is None:
        return json.dumps({
          'status': 'error', 
      })
    else:
        db.users.update({ "customer_id" : customer_id }, { '$set': { "password": set_password(password_new) }})
        return json.dumps({
          'status': 'complete', 
          'message': 'Change password successfully' 
        })  

@api_ctrl.route('/update-imfomation', methods=['GET', 'POST'])
def update_profile():
   
    dataDict = json.loads(request.data)
    fullname = dataDict['fullname']
    telephone = dataDict['telephone']
    birthday = dataDict['birthday']
    customer_id = dataDict['customer_id'].lower()

    user = db.User.find_one({'customer_id': customer_id})

    if user is None:
        return json.dumps({
          'status': 'error', 
          'message': 'Error' 
      })
    else:
        user['fullname'] = fullname
        user['telephone'] = telephone

        user['birthday'] = datetime.strptime(birthday.split('T')[0], '%Y-%M-%d')
        db.users.save(user)
        return json.dumps({
          'status': 'complete', 
          'message': 'Update account information successfully' 
        })  

@api_ctrl.route('/update-pass-tow', methods=['GET', 'POST'])
def update_pass_tow():
   
    dataDict = json.loads(request.data)
    password = dataDict['password']
    customer_id = dataDict['customer_id'].lower()

    user = db.User.find_one({'customer_id': customer_id})

    if user is None:
        return json.dumps({
          'status': 'error', 
          'message': 'Error' 
      })
    else:
        user['password_transaction'] = set_password(password)
        db.users.save(user)
        return json.dumps({
          'status': 'complete', 
          'message': 'Update account information successfully' 
        })  

def get_id_tree(ids):
    listId = ''

    query = db.users.find({'p_binary': ids})
    for x in query:
        listId += ', %s'%(x['customer_id'])
        listId += get_id_tree(x['customer_id'])
    return listId

def binary_left(customer_id):
    check_f1 = db.users.find({'$and' : [{'p_node' : customer_id},{'investment':{'$gt': 0 }} ]})
    
    if check_f1.count() > 0:
        listId = ''
        for x in check_f1:
            listId += ',%s'%(x['customer_id'])
        arrId = listId[1:]

        count = db.users.find_one({'customer_id': customer_id})
        if count['left'] == '':
            customer_binary = ',0'
        else:
            ids = count['left']

            count = get_id_tree(count['left'])

            if count:
                customer_binary = '%s , %s'%(count, ids)

            else:
                customer_binary = ',%s'%(ids)

        customer_binary = customer_binary[1:]

        array = '%s, %s'%(arrId, customer_binary)
        customers = array.split(',')
        customers = map(int, customers)

        check_in_left = [item for item, count in collections.Counter(customers).items() if count > 1]

        if len(check_in_left) != 0:
            check_in_left = 1
        else:
            check_in_left = -1
    else:
        check_in_left = -1
    return check_in_left
    

def binary_right(customer_id):
    check_f1 = db.users.find({'$and' : [{'p_node' : customer_id},{'investment':{'$gt': 0 }} ]})

    if check_f1.count() > 0:
        listId = ''
        for x in check_f1:
            listId += ', %s'%(x['customer_id'])
        arrId = listId[1:]
        count = db.users.find_one({'customer_id': customer_id})
        if count['right'] == '':
            customer_binary = ',0'
        else:
            ids = count['right']
            count = get_id_tree(count['right'])
            if count:
                customer_binary = '%s , %s'%(count, ids)
            else:
                customer_binary = ',%s'%(ids)
            
        customer_binary = customer_binary[1:]
        array = '%s, %s'%(arrId, customer_binary)
        customers = array.split(',')
        customers = map(int, customers)

        check_in_right = [item for item, count in collections.Counter(customers).items() if count > 1]
        if len(check_in_right) != 0:
            check_in_right = 1
        else:
            check_in_right = -1
    else:
        check_in_right = -1
    return check_in_right


def ThunhapTrenThuNhap(user_id,amount):
    customer = db.users.find_one({"customer_id" : user_id })
    email_receive = customer['fullname']
    if customer['p_node'] != '0' or customer['p_node'] != '':
        #F1
        customer_node_1 = db.users.find_one({"customer_id" : customer['p_node'] })
        if customer_node_1 is not None:
            check_f1_node_1 = db.users.find({'$and' :[{"p_node" : customer_node_1['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
            if int(check_f1_node_1) >= 1 and float(customer_node_1['investment']) > 0:
                ReceiveThuNhapTrenThuNhap(customer_node_1['customer_id'], amount,5,email_receive)

            #F2
            customer_node_2 = db.users.find_one({"customer_id" : customer_node_1['p_node'] })
            if customer_node_2 is not None:
                check_f1_node_2 = db.users.find({'$and' :[{"p_node" : customer_node_2['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
                if int(check_f1_node_2) >= 2 and float(customer_node_2['investment']) > 0:
                    ReceiveThuNhapTrenThuNhap(customer_node_2['customer_id'], amount,5,email_receive)

                #F2
                customer_node_3 = db.users.find_one({"customer_id" : customer_node_2['p_node'] })
                if customer_node_3 is not None:
                    check_f1_node_3 = db.users.find({'$and' :[{"p_node" : customer_node_3['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
                    if int(check_f1_node_3) >= 3 and float(customer_node_3['investment']) > 0:
                        ReceiveThuNhapTrenThuNhap(customer_node_3['customer_id'], amount,5,email_receive)
    return True
def ReceiveThuNhapTrenThuNhap(user_id, amount,percent,email_invest):
    customer = db.users.find_one({"customer_id" : user_id })

    commission = float(amount) * float(percent)/100

    ch_wallet = float(customer['ch_wallet'])
    new_ch_wallet = float(ch_wallet) + float(commission)
    new_ch_wallet = float(new_ch_wallet)

    total_receive = float(customer['total_receive'])
    new_total_receive = float(total_receive) + float(commission)
    new_total_receive = float(new_total_receive)

    balance_wallet = float(customer['balance_wallet'])
    new_balance_wallet = float(balance_wallet) + float(commission)
    new_balance_wallet = float(new_balance_wallet)

    db.users.update({ "_id" : ObjectId(customer['_id']) }, { '$set': {'ch_wallet' :new_ch_wallet, 'total_receive' : new_total_receive,'balance_wallet' : new_balance_wallet} })
    detail = '%s - %s Receive %s' %(str(percent)+str('%'),email_invest,amount)
    SaveHistory(customer['customer_id'],
        customer['email'], 
        commission, 
        'thunhaptrenthunhap',  
        detail,
        customer['fullname']
    )
def SaveHistory(uid, username, amount, types, detail,fullname):
    data_history = {
        'uid' : uid,
        'username' : username,
        'fullname' : fullname,
        'amount': float(amount),
        'type' : types,
        'date_added' : datetime.utcnow(),
        'detail': detail,
        'status' : 0
    }
    db.historys.insert(data_history)
    return True


@api_ctrl.route('/commission-calculation-system', methods=['GET', 'POST'])
def commission_calculation_system():
    dataDict = json.loads(request.data)
    
    customer_id = dataDict['customer_id'].lower()
    #customer_id = '320191892857'
    customer = db.users.find_one({"customer_id" : customer_id })
    if customer is not None:
      
      if binary_left(customer_id) == 1 and binary_right(customer_id) == 1:
        if float(customer['total_pd_left']) > 0 and float(customer['total_pd_right']) > 0:
          if customer['total_pd_left'] > customer['total_pd_right']:
            balanced = customer['total_pd_right']
            pd_left = float(customer['total_pd_left'])-float(customer['total_pd_right'])
            db.users.update({ "customer_id" : customer['customer_id'] }, { '$set': { "total_pd_left": pd_left } })
            db.users.update({ "customer_id" : customer['customer_id'] }, { '$set': { "total_pd_right": 0 } })
          else:
            balanced = customer['total_pd_left']
            pd_right = float(customer['total_pd_right'])-float(customer['total_pd_left'])
            db.users.update({ "customer_id" : customer['customer_id'] }, { '$set': { "total_pd_left": 0 } })
            db.users.update({ "customer_id" : customer['customer_id'] }, { '$set': { "total_pd_right": pd_right } })
        
            percent = 0
            if float(customer['total_node']) >= 10000000:
              percent = 8
              max_out_level = 50000000
            if float(customer['total_node']) >= 20000000:
              percent = 9
              max_out_level = 100000000
            if float(customer['total_node']) >= 30000000:
              percent = 10
              max_out_level = 200000000
            if float(customer['total_node']) >= 40000000:
              percent = 11
              max_out_level = 400000000
            if float(customer['total_node']) >= 50000000:
              percent = 12
              max_out_level = 500000000

            if float(percent) > 0:

              commission = float(balanced)*float(percent)/100
              commission = round(commission,2)

              if float(commission) > float(max_out_level):
                commission = float(max_out_level)

              if float(commission) + float(customer['max_out']) > float(max_out_level):
                commission = float(max_out_level) - float(customer['max_out'])

              n_wallet = float(customer['n_wallet'])
              new_n_wallet = float(n_wallet) + float(commission)
              new_n_wallet = float(new_n_wallet)

              total_receive = float(customer['total_receive'])
              new_total_receive = float(total_receive) + float(commission)
              new_total_receive = float(new_total_receive)

              balance_wallet = float(customer['balance_wallet'])
              new_balance_wallet = float(balance_wallet) + float(commission)
              new_balance_wallet = float(new_balance_wallet)

              max_out = float(customer['max_out'])
              new_max_out = float(max_out) + float(commission)
              new_max_out = float(new_max_out)

              db.users.update({ "_id" : ObjectId(customer['_id']) }, { '$set': {'n_wallet' :new_n_wallet,'max_out' : new_max_out,  'total_receive' : new_total_receive,'balance_wallet' : new_balance_wallet} })
              detail = '%s - %s weak branch' %(str(percent)+str('%'),"{:20,.0f}".format(balanced))
              SaveHistory(customer['customer_id'],
                  customer['email'], 
                  commission, 
                  'hoahongcannhanh',  
                  detail,
                  customer['fullname']
              )
              ThunhapTrenThuNhap(customer_id,commission)
              return json.dumps({
                  'status': 'complete',
                  'total_pd_left' : customer['total_pd_left'],
                  'total_pd_right' : customer['total_pd_right']
              })
            else:
              return json.dumps({
                'status': 'error',
                'message' : 'Bạn chưa đủ doanh số cá nhân'
              })

            
        else:
          return json.dumps({
            'status': 'error',
            'message' : 'Bạn chưa có đủ doanh số'
          })

      else:
        return json.dumps({
          'status': 'error',
          'message' : 'Bạn chưa có đủ hai F1'
        })
    else:
      return json.dumps({
        'status': 'error',
        'message' : 'Error NetWork'
      })
    
   
@api_ctrl.route('/get-version-app', methods=['GET', 'POST'])
def get_version_app():
    return json.dumps({
        'status': 'complete', 
        'version': '1' 
    })




def send_mail_register(code_active,email):
    html = """ 
      <div style="width: 100%; "><div style="background: #2E6F9C; height: 150px;text-align: center;"><img src="https://i.ibb.co/tH5J6C2/logo.png" width="120px;" style="margin-top: 30px;" /></div><br><br>
      Thank you for registering with Asipay. Please enter the code to activate the account.<br><br>
      Your code is: <b>"""+str(code_active)+"""</b>
      <br><br><br>Regards,<br>Asipay Account Services<div class="yj6qo"></div><div class="adL"><br><br><br></div></div>
    """
    return requests.post(
      "https://api.mailgun.net/v3/diamondcapital.co/messages",
      auth=("api", "key-cade8d5a3d4f7fcc9a15562aaec55034"),
      data={"from": "Asipay <info@diamondcapital.co>",
        "to": ["", email],
        "subject": "Account registration successful",
        "html": html}) 
    return True

   
def sendmail_forgot_password(email,password):
    html = """ 
      <div style="width: 100%; "><div style="background: #2E6F9C; height: 150px;text-align: center;"><img src="https://i.ibb.co/tH5J6C2/logo.png" width="120px;" style="margin-top: 30px;" /></div><br><br>
      Thank you for registering with Asipay. Please enter a new password to login.<br><br>
      Your password new is: <b>"""+str(password)+"""</b>
      <br><br><br>Regards,<br>Asipay Account Services<div class="yj6qo"></div><div class="adL"><br><br><br></div></div>
    """
    return requests.post(
      "https://api.mailgun.net/v3/diamondcapital.co/messages",
      auth=("api", "key-cade8d5a3d4f7fcc9a15562aaec55034"),
      data={"from": "Asipay <info@diamondcapital.co>",
        "to": ["", email],
        "subject": "New Password",
        "html": html}) 
    return True

