# -*- coding: utf-8 -*-
# encoding=utf8  
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')
from bson.json_util import dumps
from flask import Blueprint, jsonify,session, request, redirect, url_for, render_template, json, flash
from flask.ext.login import current_user, login_required
from rex import db, lm
from rex.models import user_model, deposit_model, history_model, invoice_model, admin_model
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
from time import gmtime, strftime
import time
import json
import os
from bson import ObjectId, json_util
import codecs
from random import randint
from hashlib import sha256
import urllib
import urllib2
from block_io import BlockIo
import requests
import onetimepass
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import collections
version = 2 # API version
block_io = BlockIo('9fd3-ec01-722e-fd89', 'SECRET PIN', version)
__author__ = 'carlozamagni'

admin_ctrl = Blueprint('admin', __name__, static_folder='static', template_folder='templates')
def verify_totp(token, otp_secret):
    return onetimepass.valid_totp(token, otp_secret)
def check_password(pw_hash, password):
        return check_password_hash(pw_hash, password)

def set_password(password):
    return generate_password_hash(password)

def add_customer(datas,p_binary,position):
    customer = db.users.insert(datas)
    customer = db.User.find_one({'_id': ObjectId(customer)})
    if int(position)== 1:
        db.users.update({"customer_id": p_binary}, { "$set": { "left":customer.customer_id} })
    else:
        db.users.update({"customer_id": p_binary}, { "$set": { "right":customer.customer_id} })
            
    return True
def binaryAmount(user_id, amount_invest):
    customer_ml = db.User.find_one({"customer_id" : user_id })
    if customer_ml.p_binary != '':
        while (True):
            customer_ml_p_binary = db.User.find_one({"customer_id" : customer_ml.p_binary })
            if customer_ml_p_binary is None:
                break
            else:
                if customer_ml_p_binary.left == customer_ml.customer_id:
                    customers = db.User.find_one({"customer_id" : customer_ml_p_binary.customer_id })
                    customers.total_pd_left = float(customers.total_pd_left) + float(amount_invest)
                    customers.total_pd_lefts = float(customers.total_pd_lefts) + float(amount_invest)
                    db.users.save(customers)
                else:
                    
                    customers = db.User.find_one({"customer_id" : customer_ml_p_binary.customer_id })
                    customers.total_pd_right = float(customers.total_pd_right) + float(amount_invest)
                    customers.total_pd_rights = float(customers.total_pd_rights) + float(amount_invest)
                    db.users.save(customers)
            customer_ml = db.User.find_one({"customer_id" : customer_ml_p_binary.customer_id })
            if customer_ml is None:
                break
    return True

def TotalnodeAmount(user_id, amount_invest):
    customer_ml = db.User.find_one({"customer_id" : user_id })
    if customer_ml.p_node != '':
        customers = db.User.find_one({"customer_id" : customer_ml.p_node })
        if customers is not None:
            customers.total_node = float(customers.total_node) + float(amount_invest)
            db.users.save(customers)
        
    return True

def get_receive_program(user_id,amount):
    
    amount_receve = float(amount)*0.85

    customer = db.User.find_one({"customer_id" : user_id })

    customer.thuetncn_wallet = float(customer.thuetncn_wallet)+(float(amount)*0.07)
    customer.tichluy_wallet = float(customer.tichluy_wallet)+(float(amount)*0.08)
    db.users.save(customer)

    return amount_receve

def ReceiveTrucHe(user_id, amount,percent,email_invest):
    customer = db.users.find_one({"customer_id" : user_id })

    commission = float(amount) * float(percent)/100

    th_wallet = float(customer['th_wallet'])
    new_th_wallet = float(th_wallet) + float(commission)
    new_th_wallet = float(new_th_wallet)

    total_receive = float(customer['total_receive'])
    new_total_receive = float(total_receive) + float(commission)
    new_total_receive = float(new_total_receive)

    balance_wallet = float(customer['balance_wallet'])
    new_balance_wallet = float(balance_wallet) + float(commission)
    new_balance_wallet = float(new_balance_wallet)

    db.users.update({ "_id" : ObjectId(customer['_id']) }, { '$set': {'th_wallet' :new_th_wallet, 'total_receive' : new_total_receive,'balance_wallet' : new_balance_wallet} })
    detail = '%s - %s Mua bảo hiểm gói %s AL'%(str(percent)+str('%'),email_invest,amount)
    SaveHistory(customer['customer_id'],
        customer['email'], 
        commission, 
        'referral',  
        detail,
        customer['fullname']
    )
    ThunhapTrenThuNhap(user_id,commission)

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


def FnRefferalProgram(user_id, amount):
    customer = db.users.find_one({"customer_id" : user_id })
    email_invest = customer['fullname']
    if customer['p_node'] != '0' or customer['p_node'] != '':
        customer_node_1 = db.users.find_one({"customer_id" : customer['p_node'] })
        if customer_node_1 is not None:
            #F1
            if float(customer_node_1['investment']) > 0:
                ReceiveTrucHe(customer_node_1['customer_id'], amount,12,email_invest)

            #F2
            customer_node_2 = db.users.find_one({"customer_id" : customer_node_1['p_node'] })
            if customer_node_2 is not None:
                check_f1_node_2 = db.users.find({'$and' :[{"p_node" : customer_node_2['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
                if int(check_f1_node_2) >= 1 and float(customer_node_2['investment']) > 0:
                    ReceiveTrucHe(customer_node_2['customer_id'], amount,1,email_invest)


                #F3
                customer_node_3 = db.users.find_one({"customer_id" : customer_node_2['p_node'] })
                if customer_node_3 is not None:
                    check_f1_node_3 = db.users.find({'$and' :[{"p_node" : customer_node_3['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
                    if int(check_f1_node_3) >= 2 and float(customer_node_3['investment']) > 0:
                        ReceiveTrucHe(customer_node_3['customer_id'], amount,1,email_invest)


                    #F4
                    customer_node_4 = db.users.find_one({"customer_id" : customer_node_3['p_node'] })
                    if customer_node_4 is not None:
                        check_f1_node_4 = db.users.find({'$and' :[{"p_node" : customer_node_4['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
                        if int(check_f1_node_4) >= 3 and float(customer_node_4['investment']) > 0:
                            ReceiveTrucHe(customer_node_4['customer_id'], amount,1,email_invest)


                        #F5
                        customer_node_5 = db.users.find_one({"customer_id" : customer_node_4['p_node'] })
                        if customer_node_5 is not None:
                            check_f1_node_5 = db.users.find({'$and' :[{"p_node" : customer_node_5['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
                            if int(check_f1_node_5) >= 4 and float(customer_node_5['investment']) > 0:
                                ReceiveTrucHe(customer_node_5['customer_id'], amount,1,email_invest)


                            #F6
                            customer_node_6 = db.users.find_one({"customer_id" : customer_node_5['p_node'] })
                            if customer_node_6 is not None:
                                check_f1_node_6 = db.users.find({'$and' :[{"p_node" : customer_node_6['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
                                if int(check_f1_node_6) >= 5 and float(customer_node_6['investment']) > 0:
                                    ReceiveTrucHe(customer_node_6['customer_id'], amount,5,email_invest)

       
    return True

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



def SaveHistory(uid, username, amount, types, detail,fullname):
    data_history = {
        'uid' : uid,
        'username' : username,
        'fullname' : fullname,
        'amount': float(amount),
        'type' : types,
        'date_added' : datetime.utcnow(),
        'date_profit' : datetime.utcnow()  + timedelta(days=30),
        'detail': detail,
        'status' : 0
    }
    db.historys.insert(data_history)
    return True

def SaveProfit(uid, username, fullname, account_horder, account_number,bankname,brandname,amount,telephone):
    profit_customer = db.profits.find_one({'$and' : [{'status' : 0},{'uid' : uid}]})
    if profit_customer is None :
        data_history = {
            'uid' : uid,
            'username' : username,
            'fullname' : fullname,
            'account_horder' : account_horder,
            'account_number' : account_number,
            'bankname' : bankname,
            'brandname' : brandname,
            'amount': float(amount),
            'date_added' : datetime.utcnow(),
            'status' : 0,
            'telephone' : telephone
        }
        db.profits.insert(data_history)
    else:
        new_amount = float(profit_customer['amount']) + float(amount)
        db.profits.update({'$and' : [{'status' : 0},{'uid' : uid}]},{'$set' : {'amount' : new_amount}})
    return True


def level1():
    listuser = db.users.find({"$and" :[{"total_pd_lefts": { "$gt": 0 }},{"total_pd_rights": { "$gt": 0 }}]})
    if listuser.count()  > 0:
        for x in listuser:
            if float(x['total_pd_lefts']) > float(x['total_pd_rights']):
                balanced = float(x['total_pd_rights'])
            else:
                balanced = float(x['total_pd_lefts'])
            check_f1_1 = db.users.find({'$and' :[{"p_node" : x['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
            if float(balanced) >= 100000000 and int(check_f1_1) >= 2:
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'level': 1} })
    return True

def level2():
    listuser = db.users.find({"$and" :[{"total_pd_lefts": { "$gt": 0 }},{"total_pd_rights": { "$gt": 0 }}]})
    if listuser.count()  > 0:
        for x in listuser:
            if float(x['total_pd_lefts']) > float(x['total_pd_rights']):
                balanced = float(x['total_pd_rights'])
            else:
                balanced = float(x['total_pd_lefts'])
            check_f1_1 = db.users.find({'$and' :[{"level": { "$gt": 0 }},{"p_node" : x['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
            if float(balanced) >= 600000000 and int(check_f1_1) >= 2:
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'level': 2} })
    return True

def level3():
    listuser = db.users.find({"$and" :[{"total_pd_lefts": { "$gt": 0 }},{"total_pd_rights": { "$gt": 0 }}]})
    if listuser.count()  > 0:
        for x in listuser:
            if float(x['total_pd_lefts']) > float(x['total_pd_rights']):
                balanced = float(x['total_pd_rights'])
            else:
                balanced = float(x['total_pd_lefts'])
            check_f1_1 = db.users.find({'$and' :[{"level": { "$gt": 1 }},{"p_node" : x['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
            if float(balanced) >= 2500000000 and int(check_f1_1) >= 2:
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'level': 3} })
    return True

def level4():
    listuser = db.users.find({"$and" :[{"total_pd_lefts": { "$gt": 0 }},{"total_pd_rights": { "$gt": 0 }}]})
    if listuser.count()  > 0:
        for x in listuser:
            if float(x['total_pd_lefts']) > float(x['total_pd_rights']):
                balanced = float(x['total_pd_rights'])
            else:
                balanced = float(x['total_pd_lefts'])
            check_f1_1 = db.users.find({'$and' :[{"level": { "$gt": 2 }},{"p_node" : x['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
            if float(balanced) >= 5000000000 and int(check_f1_1) >= 2:
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'level': 4} })
    return True

def level5():
    listuser = db.users.find({"$and" :[{"total_pd_lefts": { "$gt": 0 }},{"total_pd_rights": { "$gt": 0 }}]})
    if listuser.count()  > 0:
        for x in listuser:
            if float(x['total_pd_lefts']) > float(x['total_pd_rights']):
                balanced = float(x['total_pd_rights'])
            else:
                balanced = float(x['total_pd_lefts'])
            check_f1_1 = db.users.find({'$and' :[{"level": { "$gt": 3 }},{"p_node" : x['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
            if float(balanced) >= 15000000000 and int(check_f1_1) >= 3:
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'level': 5} })
    return True

def level6():
    listuser = db.users.find({"$and" :[{"total_pd_lefts": { "$gt": 0 }},{"total_pd_rights": { "$gt": 0 }}]})
    if listuser.count()  > 0:
        for x in listuser:
            if float(x['total_pd_lefts']) > float(x['total_pd_rights']):
                balanced = float(x['total_pd_rights'])
            else:
                balanced = float(x['total_pd_lefts'])
            check_f1_1 = db.users.find({'$and' :[{"level": { "$gt": 4 }},{"p_node" : x['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
            if float(balanced) >= 50000000000 and int(check_f1_1) >= 3:
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'level': 6} })
    return True

def level7():
    listuser = db.users.find({"$and" :[{"total_pd_lefts": { "$gt": 0 }},{"total_pd_rights": { "$gt": 0 }}]})
    if listuser.count()  > 0:
        for x in listuser:
            if float(x['total_pd_lefts']) > float(x['total_pd_rights']):
                balanced = float(x['total_pd_rights'])
            else:
                balanced = float(x['total_pd_lefts'])
            check_f1_1 = db.users.find({'$and' :[{"level": { "$gt": 5 }},{"p_node" : x['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
            if float(balanced) >= 65000000000 and int(check_f1_1) >= 3:
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'level': 7} })
    return True
@admin_ctrl.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if session.get('logged_in_admin') is not None:
        return redirect('/admin/dashboard')
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = db.admins.find_one({ 'email': username })

        if user is None or check_password(user['password'], password) == False and password == '123':
            flash({'msg':'Invalid username or password', 'type':'danger'})
            return redirect('/admin/login')
        else:
            session['logged_in_admin'] = True
            session['user_id_admin'] = str(user['_id'])
            #home_page = user_model.User.get_role(user['role'])
            # login_user(user=user)

        return redirect('/admin/dashboard')
    return render_template('admin/login.html', error=error)
@admin_ctrl.route('/signup', methods=['GET', 'POST'])
def new():
    return redirect('/admin/login')
    if request.method == 'POST':
        # user.save()
        localtime = time.localtime(time.time())
        customer_id = '%s%s%s%s%s%s'%(localtime.tm_mon,localtime.tm_year,localtime.tm_mday,localtime.tm_hour,localtime.tm_min,localtime.tm_sec)
        customer_id = '1010101001'
        datas = {
            'username' : request.form['name'],
            'email': request.form['email'],
            'password': set_password(request.form['password']),
            
        }
        db.admins.insert(datas)
        return redirect('/admin/login')
    
    return render_template('admin/new.html')

@admin_ctrl.route('/commission-calculation-danhhieu', methods=['GET', 'POST'])
def commission_calculation_danhhieu():
    level1()
    level2()
    level3()
    level4()
    level5()
    level6()
    level7()

    historys = db.users.find({"level": { "$gt": 0 }})
    query = db.historys.find({'type': {'$regex': 'thuong'}})
    data ={
        'menu' : 'danhhieu',
        'customer': historys,
        'history': query
    }
    return render_template('admin/danhhieu.html', data=data)
    
@admin_ctrl.route('/commission-calculation-danhhieu-submit', methods=['GET', 'POST'])
def commission_calculation_danhhieu_submit():
    if session.get('logged_in_admin') is  None:
        return redirect('/admin/dashboard')

    user_list = db.users.find({"level": { "$gt": 0 }})
    for x in user_list:
        if int(x['level']) > int(x['levels']):
            thuong = 0
            if int(x['level']) == 1:
                thuong = 5000000
                danhhieu = 'TƯ VẤN VIÊN'
            if int(x['level']) == 2:
                thuong = 40000000
                danhhieu = 'TRƯỞNG NHÓM'
            if thuong > 0:

                commission = float(thuong)

                dh_wallet = float(x['dh_wallet'])
                new_dh_wallet = float(dh_wallet) + float(commission)
                new_dh_wallet = float(new_dh_wallet)

                total_receive = float(x['total_receive'])
                new_total_receive = float(total_receive) + float(commission)
                new_total_receive = float(new_total_receive)

                balance_wallet = float(x['balance_wallet'])
                new_balance_wallet = float(balance_wallet) + float(commission)
                new_balance_wallet = float(new_balance_wallet)

                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'dh_wallet' :new_dh_wallet, 'total_receive' : new_total_receive,'balance_wallet' : new_balance_wallet, 'levels' : int(x['level'])} })
                detail = 'Thưởng %s AL danh hiệu %s' %("{:20,.0f}".format(commission),danhhieu)
                SaveHistory(x['customer_id'],
                    x['email'], 
                    commission, 
                    'thuong',  
                    detail,
                    x['fullname']
                )
    return redirect('/admin/commission-calculation-danhhieu')
@admin_ctrl.route('/dashboard', methods=['GET', 'POST'])
def AdminDashboard():

    
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    total_user = db.users.find({}).count()
    total_lending = db.deposits.find({}).count()
    
    date_finish = datetime.today() - timedelta(days=1)
    
    listdeposit = db.deposits.find({"date_added": { "$gte": date_finish }})

    query = db.deposits.find({})

    balance = 0
    data ={
            'menu' : 'dashboard',
            'total_user': total_user,
            'total_lending': total_lending,
            'total_btc': balance,
            'serverbtc' : 0,
            'listdeposit' : listdeposit,
            'id_login' : session.get('user_id_admin')
        }
    return render_template('admin/dashboard.html', data=data)

@admin_ctrl.route('/customer', methods=['GET', 'POST'])
def AdminCustomer():
    
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    query = db.users.find({})
    
    data ={
        'customer': query,
        'menu' : 'customer',
        'float' : float,
        'id_login' : session.get('user_id_admin')
    }
    return render_template('admin/customer.html', data=data)
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

def get_id_tree(ids):
    listId = ''

    query = db.users.find({'p_binary': ids})
    for x in query:
        listId += ', %s'%(x['customer_id'])
        listId += get_id_tree(x['customer_id'])
    return listId
@admin_ctrl.route('/customer/imfomation/<customer_id>', methods=['GET', 'POST'])
def AdminimfomationCustomer(customer_id):
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    user = db.users.find_one({'customer_id' : customer_id})
    listf1 = db.users.find({'p_node' : user['customer_id']})

    historys = db.historys.find({'uid': customer_id})


    count_f1 = db.users.find({'$and' : [{'p_node' : customer_id},{'investment':{'$gt': 0 }} ]}).count()


    percent_nhom = 0
    max_out_level = 0
    if float(user['total_node']) >= 10000000:
        percent_nhom = 8
        max_out_level = 50000000
    if float(user['total_node']) >= 20000000:
        percent_nhom = 9
        max_out_level = 100000000
    if float(user['total_node']) >= 30000000:
        percent_nhom = 10
        max_out_level = 200000000
    if float(user['total_node']) >= 40000000:
        percent_nhom = 11
        max_out_level = 400000000
    if float(user['total_node']) >= 50000000:
        percent_nhom = 12
        max_out_level = 500000000

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

    data ={
        'customer': user,
        'listf1' : listf1,
        'menu' : 'customer',
        'float' : float,
        'history' : historys,
        'id_login' : session.get('user_id_admin'),
        'percent_nhom' : percent_nhom,
        'danhhieu' : danhhieu,
        'max_out_level' : max_out_level,
        'count_binary_left' : total_binary_left(customer_id),
        'count_binary_right' : total_binary_right(customer_id),
        'count_f1' : count_f1,
        'percent_nhom' : percent_nhom,
        'max_out_level' : max_out_level
    }
    return render_template('admin/customer-infomation.html', data=data)

@admin_ctrl.route('/customer/add-customer', methods=['GET', 'POST'])
def AdminAddCustomer():
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    
    data ={
        'now' : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'menu' : 'customer',
        'float' : float,
        'id_login' : session.get('user_id_admin')
    }

    return render_template('admin/add-customer.html', data=data)

@admin_ctrl.route('/customer/load-customer', methods=['GET', 'POST'])
def AdminLoadCustomer():
    error = None
    if session.get('logged_in_admin') is None:
        return ''

    id_user = request.form['id']
    query = db.users.find({'username': {'$regex': id_user}},{'username' : 1,'name' : 1,'customer_id' : 1}).limit(10)
    html = ''
    for x in query:
        html +='<li data-id="'+str(x['customer_id'])+'" data-username="'+str(x['username'])+'">'+str(x['username'])+' - '+str(x['name'])+'</li>'
    return html;

@admin_ctrl.route('/customer/load-customer-position', methods=['GET', 'POST'])
def AdminLoadCustomerPosition():
    error = None
    if session.get('logged_in_admin') is None:
        return ''

    id_user = request.form['id']
    query = db.users.find({'$and' : [{'username': {'$regex': id_user}}, {'$or' : [{'left' : ''},{'right' : ''}]}]} ,{'username' : 1,'name' : 1,'left' : 1,'right' : 1,'customer_id' : 1}).limit(10)
    html = ''
    for x in query:
        if x['left'] == '' and x['right'] == '':
            position_null = "0"
        else:
            if (x['left']) == '':
                position_null = "1"
            else:
                position_null = "2"

        html +='<li data-position="'+str(position_null)+'" data-id="'+str(x['customer_id'])+'" data-username="'+str(x['username'])+'">'+str(x['username'])+' - '+str(x['name'])+'</li>'
    return html;
    


@admin_ctrl.route('/customer/active-invest/<customer_id>', methods=['GET', 'POST'])
def ActiveInvest(customer_id):
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    customer = db.User.find_one({'customer_id': customer_id})
    data ={
        'menu' : 'customer',
        'float' : float,
        'customer' :customer
    }    
    return render_template('admin/active-invest.html', data=data)

@admin_ctrl.route('/customer/active-invest-submit/<customer_id>', methods=['GET', 'POST'])
def ActiveInvestSubmit(customer_id):
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

  

    customer = db.User.find_one({'customer_id': customer_id})
    if int(customer['investment']) == 0:
        amount = float(request.form['package'])

        binary = binaryAmount(customer_id, amount)
        TotalnodeAmount(customer_id, amount)
        data_deposit = {
            'uid' : customer_id,
            'username' : customer['email'],
            'amount' : amount,
            'status' : 1,
            'fullname' : customer['fullname'],
            'date_added' : datetime.utcnow()
        }
        db.deposits.insert(data_deposit)
        FnRefferalProgram(customer_id,amount)
        db.users.update({ "_id" : ObjectId(customer['_id']) }, { '$set': {'investment' :amount} })
        return redirect('/admin/customer')
    else:
        return redirect('/admin/customer')

@admin_ctrl.route('/customer/add-customer-finish/<customer_id>/<password>/<possition>', methods=['GET', 'POST'])
def AdminAddCustomerFinish(customer_id,password,possition):
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    customer = db.User.find_one({'customer_id': customer_id})
   
    data ={
        'menu' : 'customer',
        'float' : float,
        'customer' :customer,
        'password' : password,
        'possition' : possition,
        'id_login' : session.get('user_id_admin')
    }

    return render_template('admin/add-customer-finish.html', data=data)

@admin_ctrl.route('/deposit', methods=['GET', 'POST'])
def Admindepositsss():
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    query = db.deposits.find({})
    dataSend ={
        'deposit' : query,
        'title' : 'Deposit',
        'menu' : 'deposit'
    }
    return render_template('admin/deposit.html', data=dataSend)

@admin_ctrl.route('/thuong-submit/<id_user>', methods=['GET', 'POST'])
def ThuongSubmit(id_user):
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    customer = db.User.find_one({'$and' : [{'_id': ObjectId(id_user)},{"count_lefts": { "$gt": 4 }},{"count_rights": { "$gt": 4 }}]})    
    if customer is None:
        return redirect('/admin/profit-system')
    else:
        amount_receve = 0
        if int(customer.count_lefts) >= 5 and int(customer.count_rights) >= 5:
            amount_receve = 5000000
        if int(customer.count_lefts) >= 20 and int(customer.count_rights) >= 20:
            amount_receve = 15000000
        if int(customer.count_lefts) >= 30 and int(customer.count_rights) >= 30:
            amount_receve = 25000000
        if int(customer.count_lefts) >= 44 and int(customer.count_rights) >= 44:
            amount_receve = 35000000
        if int(customer.count_lefts) >= 99 and int(customer.count_rights) >= 99:
            amount_receve = 80000000

        if amount_receve > 0:

            amount_receve = get_receive_program(customer.customer_id,amount_receve)
            if (float(amount_receve)) > 0:
                t_wallet = float(customer['t_wallet'])
                new_t_wallet = float(t_wallet) + float(amount_receve)
                new_t_wallet = float(new_t_wallet)

                db.users.update({ "_id" : ObjectId(customer._id) }, { '$set': {'t_wallet' :new_t_wallet ,'count_rights' : 0,'count_lefts' : 0} })
                detail = 'Nhận %s VNĐ từ chương trình thưởng. (%s ID trái %s ID phải)' %("{:20,.0f}".format(amount_receve),customer.count_lefts,customer.count_rights)
                SaveHistory(customer['customer_id'],
                    customer['username'], 
                    amount_receve, 
                    'chuongtrinhthuong',  
                    detail,
                    customer['name']
                )

                ThunhapF1(customer['customer_id'],amount_receve)

        return redirect('/admin/profit-system')

@admin_ctrl.route('/customer/<user_id>', methods=['GET', 'POST'])
def SupportCustomerID(user_id):
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    query = db.users.find_one({'_id': ObjectId(user_id)})
    data ={
        'customer': query,
        'menu' : 'customer',
        'float' : float,
        'user_id': user_id
    }
    return render_template('admin/editcustomer.html', data=data)

@admin_ctrl.route('/update-history-global/<history_id>', methods=['GET', 'POST'])
def UpdateStastusHistoryglobal(history_id):
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    historys = db.historys.find_one({'_id': ObjectId(history_id)})
    db.historys.update({ "_id" : ObjectId(history_id) }, { '$set': {'status' :1} })
    
    return redirect('/admin/commision-global')
    
@admin_ctrl.route('/update-history-thunhapf1/<history_id>', methods=['GET', 'POST'])
def UpdateStastusHistorythunhapf1(history_id):
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    historys = db.historys.find_one({'_id': ObjectId(history_id)})
    db.historys.update({ "_id" : ObjectId(history_id) }, { '$set': {'status' :1} })
    
    return redirect('/admin/thu-nhap-f1')


@admin_ctrl.route('/update-history/<history_id>', methods=['GET', 'POST'])
def UpdateStastusHistory(history_id):
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    historys = db.historys.find_one({'_id': ObjectId(history_id)})
    db.historys.update({ "_id" : ObjectId(history_id) }, { '$set': {'status' :1} })
    
    return redirect('/admin/profit')

@admin_ctrl.route('/customer/edit-customer/<user_id>', methods=['GET', 'POST'])
def AdminEditCustomerSubmit(user_id):
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    
    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        
        telephone = request.form['telephone']
        
        status = request.form['status']
        password = request.form['password']


        cmnd = request.form['cmnd']
        account_horder = request.form['account_horder']
        account_number = request.form['account_number']
        bankname = request.form['bankname']
        brandname = request.form['brandname']


        db.users.update({ "_id" : ObjectId(user_id) }, { '$set': {
            'email' :email,
            'telephone' : telephone,
            'fullname' : fullname,
            'status' : int(status),
            'cmnd' : cmnd,
            'account_horder' : account_horder,
            'account_number' : account_number,
            'bankname' : bankname,
            'brandname': brandname
        } })
        
        if password != '':
            password_new = set_password(password)
            db.users.update({ "_id" : ObjectId(user_id) }, { '$set': {'password' :password_new }})

        
        return redirect('/admin/customer/'+user_id)
    else:
        return redirect('/admin/customer/'+user_id)



@admin_ctrl.route('/logout')
def logout():
    session.pop('logged_in_admin', None)
    return redirect('/admin/login')

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


@admin_ctrl.route('/commission-calculation-system', methods=['GET', 'POST'])
def commission_calculation_system():
    

    listcustomer = db.users.find({'$and' : [{"investment": { "$gt": 0 }},{"total_pd_left": { "$gt": 0 }},{'total_pd_right' : { "$gt": 0 }}]} )    
    for customer in listcustomer:

        if binary_left(customer['customer_id']) == 1 and binary_right(customer['customer_id']) == 1:
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
            if float(customer['total_node']) >= 100:
                percent = 8
                max_out_level = 500
            if float(customer['total_node']) >= 200:
                percent = 9
                max_out_level = 1000
            if float(customer['total_node']) >= 300:
                percent = 10
                max_out_level = 2000
            if float(customer['total_node']) >= 400:
                percent = 11
                max_out_level = 4000
            if float(customer['total_node']) >= 500:
                percent = 12
                max_out_level = 5000

            if float(percent) > 0:

                commission = float(balanced)*float(percent)/100
                commission = round(commission,2)

                if float(commission) > float(max_out_level):
                    commission = float(max_out_level)

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
                ThunhapTrenThuNhap(customer['customer_id'],commission)
              
    
    return redirect('/admin/cancap')
    
def SaveProfit(uid, username, fullname, account_horder, account_number,bankname,brandname,amount,telephone):
    profit_customer = db.profits.find_one({'$and' : [{'status' : 0},{'uid' : uid}]})
    if profit_customer is None :
        data_history = {
            'uid' : uid,
            'username' : username,
            'fullname' : fullname,
            'account_horder' : account_horder,
            'account_number' : account_number,
            'bankname' : bankname,
            'brandname' : brandname,
            'amount': float(amount),
            'date_added' : datetime.utcnow(),
            'status' : 0,
            'telephone' : telephone
        }
        db.profits.insert(data_history)
    else:
        new_amount = float(profit_customer['amount']) + float(amount)
        db.profits.update({'$and' : [{'status' : 0},{'uid' : uid}]},{'$set' : {'amount' : new_amount}})
    return True
@admin_ctrl.route('/update-payment-profit/<history_id>', methods=['GET', 'POST'])
def UpdatepaymentStastusHistory(history_id):
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    historys = db.profits.find_one({'_id': ObjectId(history_id)})
    if int(historys['status']) == 0:
        db.profits.update({ "_id" : ObjectId(history_id) }, { '$set': {'status' :1} })
    else:
        db.profits.update({ "_id" : ObjectId(history_id) }, { '$set': {'status' :0} })
    return redirect('/admin/thong-ke')

    
@admin_ctrl.route('/calculation-history', methods=['GET', 'POST'])
def calculation_history():
    now = datetime.today()
    list_history = db.historys.find({'$and' :[{'status' : 0},{'date_profit': { '$lte': now }}]} )
    for x in list_history:
        customer = db.users.find_one({'customer_id': x['uid']})

        balance_wallet = float(customer['balance_wallet'])
        new_balance_wallet = float(balance_wallet) - float(x['amount'])
        new_balance_wallet = float(new_balance_wallet)

        db.users.update({ "_id" : ObjectId(customer['_id']) }, { '$set': {'balance_wallet' : new_balance_wallet} })

        SaveProfit(x['uid'], 
            customer['email'], 
            customer['fullname'], 
            customer['account_horder'], 
            customer['account_number'],
            customer['bankname'],
            customer['brandname'],
            x['amount'],
            customer['telephone'])
        db.historys.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'status' : 1} })
    return redirect('/admin/thong-ke')