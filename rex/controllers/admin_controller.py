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
        while (True):
            customer_ml_p_node = db.User.find_one({"customer_id" : customer_ml.p_node })
            if customer_ml_p_node is None:
                break
            else:
                customers = db.User.find_one({"customer_id" : customer_ml_p_node.customer_id })
                customers.total_node = float(customers.total_node) + float(amount_invest)
                db.users.save(customers)
                
            customer_ml = db.User.find_one({"customer_id" : customer_ml_p_node.customer_id })
            if customer_ml is None:
                break
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
    detail = '%s - %s Mua %s RL'%(str(percent)+str('%'),email_invest,amount)
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
                ReceiveTrucHe(customer_node_1['customer_id'], amount,15,email_invest)

            #F2
            customer_node_2 = db.users.find_one({"customer_id" : customer_node_1['p_node'] })
            if customer_node_2 is not None:
                check_f1_node_2 = db.users.find({'$and' :[{"p_node" : customer_node_2['customer_id'] },{"investment": { "$gt": 0 }}]}).count()
                if int(check_f1_node_2) >= 1 and float(customer_node_2['investment']) > 0:
                    ReceiveTrucHe(customer_node_2['customer_id'], amount,2,email_invest)


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
                                    ReceiveTrucHe(customer_node_6['customer_id'], amount,2,email_invest)

       
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
                detail = 'Thưởng %s RL danh hiệu %s' %("{:20,.0f}".format(commission),danhhieu)
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

    # deposit_list = db.deposits.find({})
    # now = datetime.today()
    # for x in deposit_list:
    #     history = db.historys.find({'$and' :[{'username' :x['username']},{'type' :'profit-daily'}]}).count()
    #     date_added = x['date_added']
    #     date_1 = date_added + timedelta(days=35)
    #     db.deposits.update({'_id' :ObjectId(x['_id'])},{'$set' : {'date_finish' : date_1}})
    #     if now > date_1:
            
    #         date_2 = date_added + timedelta(days=65)
    #         db.deposits.update({'_id' :ObjectId(x['_id'])},{'$set' : {'date_finish' : date_2}})
            
    #         if now > date_2:

    #             customer = db.users.find_one({'customer_id' : x['uid']})

    #             new_daily_wallet = float(customer['daily_wallet']) + float(x['monthly'])

    #             db.users.update({'customer_id' : x['uid']},{'$set' : {'daily_wallet' : new_daily_wallet}})
                
    #             detail = 'Nhận %s VNĐ từ Lãi hàng tháng'%("{:20,.0f}".format(float(x['monthly'])))
    #             SaveHistory(customer['customer_id'],
    #                 customer['username'], 
    #                 x['monthly'], 
    #                 'profit-daily',  
    #                 detail,
    #                 customer['name']
    #             )

    #             SaveProfit(
    #                 customer['customer_id'], 
    #                 customer['username'], 
    #                 customer['name'], 
    #                 customer['account_horder'], 
    #                 customer['account_number'],
    #                 customer['bankname'],
    #                 customer['brandname'],
    #                 x['monthly'],
    #                 customer['telephone']
                    
    #             )


    #             print history, 2,x['username']
    #             date_3 = date_added + timedelta(days=95)
    #             db.deposits.update({'_id' :ObjectId(x['_id'])},{'$set' : {'date_finish' : date_3}})
                
    #             if now > date_3:
    #                 print history, 3,x['username']
    #                 date_4 = date_added + timedelta(days=95)
    #                 db.deposits.update({'_id' :ObjectId(x['_id'])},{'$set' : {'date_finish' : date_4}})
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

@admin_ctrl.route('/customer/imfomation/<customer_id>', methods=['GET', 'POST'])
def AdminimfomationCustomer(customer_id):
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    query = db.users.find_one({'customer_id' : customer_id})
    listf1 = db.users.find({'p_node' : query['customer_id']})

    historys = db.historys.find({'uid': customer_id})
    data ={
        'customer': query,
        'listf1' : listf1,
        'menu' : 'customer',
        'float' : float,
        'history' : historys,
        'id_login' : session.get('user_id_admin')
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


@admin_ctrl.route('/deposit/tai-dau-tu/<user_id>', methods=['GET', 'POST'])
def TaiDauTu(user_id):
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    db.deposits.update({ "uid" : user_id }, { '$set': {'status' :1} })
    db.users.update({ "customer_id" : user_id }, { '$set': {'status_re' :0,'total_receive' :0} })
    return redirect('/admin/deposit')


@admin_ctrl.route('/deposit/thay-doi-ngay/<_id>', methods=['GET', 'POST'])
def ThayDoiNgay(_id):

    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    query = db.deposits.find_one({'_id': ObjectId(_id)})
    data ={
        'deposit': query,
        'menu' : 'deposit',
        'float' : float,
        'id': _id
    }
    return render_template('admin/thay-doi-ngay.html', data=data)


@admin_ctrl.route('/deposit/thay-doi-ngay-submit/<_id>', methods=['GET', 'POST'])
def ThayDoiNgaySubmit(_id):

    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    

    date_added =  request.form['date_added']


    date_addeds = datetime.strptime(date_added, '%Y-%m-%d %H:%M:%S')
    date_finish =  datetime.strptime(date_added, '%Y-%m-%d %H:%M:%S') + timedelta(days=35)

    db.deposits.update({ "_id" : ObjectId(_id) }, { '$set': {
            'date_added' :date_addeds,
            'date_finish' :date_finish
    }})

    return redirect('/admin/deposit')

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
        password_transaction = request.form['password_transaction']

        db.users.update({ "_id" : ObjectId(user_id) }, { '$set': {
            'email' :email,
            'telephone' : telephone,
            'fullname' : fullname,
            'status' : int(status)
        } })
        
        if password != '':
            password_new = set_password(password)
            db.users.update({ "_id" : ObjectId(user_id) }, { '$set': {'password' :password_new }})

        if password_transaction != '':
            password_transaction_new = set_password(password_transaction)
            db.users.update({ "_id" : ObjectId(user_id) }, { '$set': {'password_transaction' :password_transaction_new }})
        
        return redirect('/admin/customer/'+user_id)
    else:
        return redirect('/admin/customer/'+user_id)



@admin_ctrl.route('/commision-global', methods=['GET', 'POST'])
def CommissionGloabl():
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    
    query = db.historys.find({'type': {'$regex': 'global'}})
    data ={
            'menu' : 'commision-global',
            'history': query
    }
    return render_template('admin/commision-global.html', data=data)




@admin_ctrl.route('/calculation-commission', methods=['GET', 'POST'])
def CommissionCalculation():
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    level1()
    level2()
    level3()
    level4()
    data ={
        'menu' : 'calculation-commission',
    }
    return render_template('admin/calculation-commission.html', data=data)

@admin_ctrl.route('/profit-daily', methods=['GET', 'POST'])
def profitdaily():
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    now = datetime.today()
    query = db.deposits.find({"date_finish": { "$lte": now }})
    data ={
        'menu' : 'profit-daily',
        'history' :query
    }
    return render_template('admin/profit-daily.html', data=data)

# LAI THANG
@admin_ctrl.route('/profit-daily-submit', methods=['GET', 'POST'])
def ProfitDailySubmit():
    error = None
    #return redirect('/admin/login')
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    now = datetime.today()
    listdeposit = db.deposits.find({"date_finish": { "$lte": now }})
    for x in listdeposit:
        customer = db.users.find_one({'customer_id' : x['uid']})

        new_daily_wallet = float(customer['daily_wallet']) + float(x['monthly'])

        db.users.update({'customer_id' : x['uid']},{'$set' : {'daily_wallet' : new_daily_wallet}})
        
        detail = 'Nhận %s VNĐ từ Lãi hàng tháng'%("{:20,.0f}".format(float(x['monthly'])))
        SaveHistory(customer['customer_id'],
            customer['username'], 
            x['monthly'], 
            'profit-daily',  
            detail,
            customer['name']
        )

        SaveProfit(
            customer['customer_id'], 
            customer['username'], 
            customer['name'], 
            customer['account_horder'], 
            customer['account_number'],
            customer['bankname'],
            customer['brandname'],
            x['monthly'],
            customer['telephone']
            
        )
        nowss = datetime.today() + timedelta(days=30)
        db.deposits.update({'_id' : ObjectId(x['_id'])},{'$set' : {'date_finish' : nowss}} )
    return redirect('/admin/profit-daily')

# HOA HONG TRUC TIEP
@admin_ctrl.route('/calculation-commission/referall-submit', methods=['GET', 'POST'])
def ReferallSubmit():
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    listcustomer = db.users.find({'$and' : [{"r_wallet": { "$gt": 0 }},{'active' : 2}]} )    
    for x in listcustomer:
        amount_receve = x['r_wallet']
        amount_receve = get_receive_program(x['customer_id'],amount_receve)
        if float(amount_receve) > 0:
            db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'r_wallet' :0} })

            new_tructiep_wallet = float(x['tructiep_wallet']) + float(amount_receve)
            db.users.update({'customer_id' : x['customer_id']},{'$set' : {'tructiep_wallet' : new_tructiep_wallet}})

            SaveProfit(
                x['customer_id'], 
                x['username'], 
                x['name'], 
                x['account_horder'], 
                x['account_number'],
                x['bankname'],
                x['brandname'],
                amount_receve,
                x['telephone']
            )

            ThunhapF1(x['customer_id'],amount_receve)
    return redirect('/admin/calculation-commission')

# HOA HONG THUONG THEM
@admin_ctrl.route('/calculation-commission/thuongthem-submit', methods=['GET', 'POST'])
def ThuongthemSubmit():
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    listcustomer = db.users.find({'$and' : [{"count_lefts": { "$gt": 4 }},{"count_rights": { "$gt": 4 }},{'active' : 2}]})    
    for x in listcustomer:
        amount_receve = 0
        level_thuongthem = 0
        if int(x['count_lefts']) >= 5 and int(x['count_rights']) >= 5 and int(x['level_thuongthem']) == 0:
            amount_receve = 5000000
            level_thuongthem = 1
        if int(x['count_lefts']) >= 20 and int(x['count_rights']) >= 20 and int(x['level_thuongthem']) <= 1:
            amount_receve = 15000000
            level_thuongthem = 2
        if int(x['count_lefts']) >= 30 and int(x['count_rights']) >= 30 and int(x['level_thuongthem']) <= 2:
            amount_receve = 25000000
            level_thuongthem = 3
        if int(x['count_lefts']) >= 44 and int(x['count_rights']) >= 44 and int(x['level_thuongthem']) <= 3:
            amount_receve = 35000000
            level_thuongthem = 4
        if int(x['count_lefts']) >= 99 and int(x['count_rights']) >= 99 and int(x['level_thuongthem']) <= 4:
            amount_receve = 80000000
            level_thuongthem = 0

        if amount_receve > 0:
            amount_receve = get_receive_program(x['customer_id'],amount_receve)

            if (float(amount_receve)) > 0:

                t_wallet = float(x['t_wallet'])
                new_t_wallet = float(t_wallet) + float(amount_receve)
                new_t_wallet = float(new_t_wallet)

                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'t_wallet' :new_t_wallet ,'level_thuongthem' : level_thuongthem} })

                if int(x['count_lefts']) > int(x['count_rights']):
                    new_counts = int(x['count_lefts']) - int(x['count_rights'])
                    db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'t_wallet' :new_t_wallet ,'count_rights' : 0,'count_lefts' : new_counts} })
                else:
                    new_counts = int(x['count_rights']) - int(x['count_lefts'])
                    db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'t_wallet' :new_t_wallet ,'count_rights' : new_counts,'count_lefts' : 0} })
                
                detail = 'Nhận %s VNĐ từ chương trình thưởng. (%s ID trái %s ID phải)' %("{:20,.0f}".format(amount_receve),x['count_lefts'],x['count_rights'])
                SaveHistory(x['customer_id'],
                    x['username'], 
                    amount_receve, 
                    'chuongtrinhthuong',  
                    detail,
                    x['name']
                )
                SaveProfit(
                    x['customer_id'], 
                    x['username'], 
                    x['name'], 
                    x['account_horder'], 
                    x['account_number'],
                    x['bankname'],
                    x['brandname'],
                    amount_receve,
                    x['telephone']
                )
                ThunhapF1(x['customer_id'],amount_receve)

    return redirect('/admin/calculation-commission')

#HOA HONG HE THONG
@admin_ctrl.route('/calculation-commission/system-submit', methods=['GET', 'POST'])
def CommissionSystemSubmitS():
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    
    listcustomer = db.users.find({'$and' : [{"level": { "$gt": 0 }},{"total_node": { "$gt": 0 }},{'active' : 2}]} )    
    for x in listcustomer:
    
        amount_receve = (float(x['total_node']))/100
        doanhso = float(x['total_node'])
        
        amount_receve = get_receive_program(x['customer_id'],amount_receve)
        if float(amount_receve) > 0:

            s_wallet = float(x['s_wallet'])
            new_s_wallet = float(s_wallet) + float(amount_receve)
            new_s_wallet = float(new_s_wallet)

            db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'s_wallet' :new_s_wallet ,'total_node' : 0} })
            detail = 'Nhận %s VNĐ từ %s  hoa hồng hệ thống.(Doanh số %s)' %("{:20,.0f}".format(amount_receve),'1%',"{:20,.0f}".format(doanhso))
            SaveHistory(x['customer_id'],
                x['username'], 
                amount_receve, 
                'system',  
                detail,
                x['name']
            )
            SaveProfit(
                x['customer_id'], 
                x['username'], 
                x['name'], 
                x['account_horder'], 
                x['account_number'],
                x['bankname'],
                x['brandname'],
                amount_receve,
                x['telephone']
            )
            ThunhapF1(x['customer_id'],amount_receve)
    return redirect('/admin/calculation-commission')

#HOA HONG TOAN CAU
@admin_ctrl.route('/calculation-commission/global-submit', methods=['GET', 'POST'])
def CommissionGloablSubmit():
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    
    customer = db.users.find({"level": { "$gt": 1 }})    

    count_level2 = db.users.find({"level": 2}).count()
    count_level3 = db.users.find({"level": 3}).count()
    count_level4 = db.users.find({"level": 4}).count()

    user_admin = db.users.find_one({ "_id" : ObjectId('5b4f63a6a8562a448030cae6') } )    
    total_admin = float(user_admin['total_left']) + float(user_admin['total_right'])
    if float(total_admin) > 0:
        for x in customer:
            if int(x['level']) == 2:
                percent = 1
                dongchia = count_level2
            if int(x['level']) == 3:
                percent = 1
                dongchia = count_level3
            if int(x['level']) >= 4:
                percent = 1.5
                dongchia = count_level4
        
            amount_receve = float(total_admin)*percent/100/dongchia
            
            amount_receve = get_receive_program(x['customer_id'],amount_receve)
            if float(amount_receve) > 0:

                g_wallet = float(x['g_wallet'])
                new_g_wallet = float(g_wallet) + float(amount_receve)
                new_g_wallet = float(new_g_wallet)

                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'g_wallet' :new_g_wallet} })

                detail = 'Nhận đồng chia %s VNĐ từ %s  hoa hồng toàn cầu.(Toàn cầu %s)' %("{:20,.0f}".format(amount_receve),str(percent)+'%',"{:20,.0f}".format(total_admin))
                SaveHistory(x['customer_id'],
                    x['username'], 
                    amount_receve, 
                    'global',  
                    detail,
                    x['name']
                )
                SaveProfit(
                    x['customer_id'], 
                    x['username'], 
                    x['name'], 
                    x['account_horder'], 
                    x['account_number'],
                    x['bankname'],
                    x['brandname'],
                    amount_receve,
                    x['telephone']
                )
                ThunhapF1(x['customer_id'],amount_receve)

        db.users.update({ "_id" : ObjectId("5b4f63a6a8562a448030cae6") }, { '$set': {'total_left' :0,'total_right' :0} })
    return redirect('/admin/calculation-commission')

#HOA HONG THU NHAP F1
@admin_ctrl.route('/calculation-commission/thunhapf1-submit', methods=['GET', 'POST'])
def Thunhapf1Submit():
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    listcustomer = db.users.find({'$and' :[{"m_wallet": { "$gt": 0 }},{'active' : 2}]} )    
    for x in listcustomer:
        amount_receve = x['m_wallet']


        thunhapf1_wallet = float(x['thunhapf1_wallet'])
        new_thunhapf1_wallet = float(thunhapf1_wallet) + float(amount_receve)
        new_thunhapf1_wallet = float(new_thunhapf1_wallet)

        db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'m_wallet' :0, 'thunhapf1_wallet' : new_thunhapf1_wallet} })
        SaveProfit(
            x['customer_id'], 
            x['username'], 
            x['name'], 
            x['account_horder'], 
            x['account_number'],
            x['bankname'],
            x['brandname'],
            amount_receve,
            x['telephone']
        )
    return redirect('/admin/calculation-commission')


# HOA HONG can cap
@admin_ctrl.route('/calculation-commission/cancap-submit', methods=['GET', 'POST'])
def CancapSubmit():
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    listcustomer = db.users.find({'$and' : [{'active' : 2},{"count_leftss": { "$gt": 0 }},{"count_rightss": { "$gt": 0 }}]})    
    for x in listcustomer:

        if int(x['count_leftss']) > int(x['count_rightss']): 
            amount_receve = int(x['count_rightss'])*300000
            cancap =  int(x['count_rightss'])
        else:
            amount_receve = int(x['count_leftss'])*300000
            cancap =  int(x['count_leftss'])
        amount_receve = get_receive_program(x['customer_id'],amount_receve)

        if (float(amount_receve)) > 0:
            if int(x['count_leftss']) > int(x['count_rightss']):
                new_counts = int(x['count_leftss']) - int(x['count_rightss'])
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'count_rightss' : 0,'count_leftss' : new_counts} })
            else:
                new_counts = int(x['count_rightss']) - int(x['count_leftss'])
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'count_rightss' : new_counts,'count_leftss' : 0} })
            

            cancap_wallet = float(x['cancap_wallet'])
            new_cancap_wallet = float(cancap_wallet) + float(amount_receve)
            new_cancap_wallet = float(new_cancap_wallet)

            db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'cancap_wallet' : new_cancap_wallet} })

            detail = 'Nhận %s VNĐ từ cân cặp. (%s cặp)' %("{:20,.0f}".format(amount_receve),cancap)
            SaveHistory(x['customer_id'],
                x['username'], 
                amount_receve, 
                'cancap',  
                detail,
                x['name']
            )
            SaveProfit(
                x['customer_id'], 
                x['username'], 
                x['name'], 
                x['account_horder'], 
                x['account_number'],
                x['bankname'],
                x['brandname'],
                amount_receve,
                x['telephone']
            )
            ThunhapF1(x['customer_id'],amount_receve)

    return redirect('/admin/calculation-commission')

@admin_ctrl.route('/updatePassword', methods=['GET', 'POST'])
def updatePassword():
    error = None
    if session.get('logged_in_admin') is None:
        return json.dumps({
            'status': 'error', 
            'message': 'Please login' 
        })
    password = request.form['password']
    
    repeat_password = request.form['repeat_password']
    wallet = request.form['wallet']
    email = request.form['email']
    telephone = request.form['telephone']


    if wallet =='':
        return json.dumps({
            'status': 'error', 
            'message': 'Please enter wallet' 
        })
    if email =='':
        return json.dumps({
            'status': 'error', 
            'message': 'Please enter email' 
        })
    if telephone =='':
        return json.dumps({
            'status': 'error', 
            'message': 'Please enter telephone' 
        })
    if password =='' or repeat_password =='':
        return json.dumps({
            'status': 'error', 
            'message': 'Please enter password' 
        })
    if password != repeat_password:
        return json.dumps({
            'status': 'error', 
            'message': 'Wrong repeat password ' 
        })
    user_id = request.form['user_id']
    query = db.users.find({'_id': ObjectId(user_id)})
    if query is None:
        return json.dumps({
            'status': 'error', 
            'message': 'That user dose not exits ' 
        })
    password_new = set_password(password)
    db.users.update({ "_id" : ObjectId(user_id) }, { '$set': { "password": password_new ,"wallet" : wallet,'telephone' : telephone,'email' : email} })
    return json.dumps({
        'status': 'success', 
        'message': 'Update Success ' 
    })
@admin_ctrl.route('/updateSponsor', methods=['GET', 'POST'])
def updateSponsor():
    error = None
    if session.get('logged_in_admin') is None:
        return json.dumps({
            'status': 'error', 
            'message': 'Please login' 
        })
    p_node = request.form['p_node']
    p_node = p_node.lower()
    user_id = request.form['user_id']
    query = db.users.find_one({'_id': ObjectId(user_id)})
    if query is None:
        return json.dumps({
            'status': 'error', 
            'message': 'That user dose not exits ' 
        })
    find_node = db.users.find_one({'username': p_node})
    if find_node is None:
        return json.dumps({
            'status': 'error', 
            'message': 'Username dose not exits' 
        })
    db.users.update({ "_id" : ObjectId(user_id) }, { '$set': { "p_node": find_node['customer_id'] } })
    return json.dumps({
        'status': 'success', 
        'message': 'Update Success ' 
    })
@admin_ctrl.route('/updatePbinary', methods=['GET', 'POST'])
def updatePbinary():
    error = None
    if session.get('logged_in_admin') is None:
        return json.dumps({
            'status': 'error', 
            'message': 'Please login' 
        })
    p_binary = request.form['p_binary']
    p_binary = p_binary.lower()
    user_id = request.form['user_id']
    query = db.users.find_one({'_id': ObjectId(user_id)})
    if query is None:
        return json.dumps({
            'status': 'error', 
            'message': 'That user dose not exits ' 
        })
    find_binary = db.users.find_one({'username': p_binary})
    if find_binary is None:
        return json.dumps({
            'status': 'error', 
            'message': 'Username dose not exits' 
        })
    if query['p_binary'] == '':
        print 'None'
    else:
        binary_current = db.users.find_one({'customer_id': query['p_binary']})
        if binary_current is None:
            print 'Current None'
        else:
            if query['customer_id'] == binary_current['left']:
                db.users.update({ "_id" : ObjectId(binary_current['_id']) }, { '$set': { "left": '' } })
            else:
                db.users.update({ "_id" : ObjectId(binary_current['_id']) }, { '$set': { "right": '' } })
    if find_binary['left'] == '':
        db.users.update({ "_id" : ObjectId(find_binary['_id']) }, { '$set': { "left": query['customer_id'] } })
        db.users.update({ "_id" : ObjectId(user_id) }, { '$set': { "p_binary": find_binary['customer_id'], 'type': 1 } })
        return json.dumps({
            'status': 'success', 
            'message': 'Update Success ' 
        })
    if find_binary['right'] == '':
        db.users.update({ "_id" : ObjectId(find_binary['_id']) }, { '$set': { "right": query['customer_id'] } })
        db.users.update({ "_id" : ObjectId(user_id) }, { '$set': { "p_binary": find_binary['customer_id'], 'type': 1 } })
        return json.dumps({
            'status': 'success', 
            'message': 'Update Success ' 
        })
    return json.dumps({
        'status': 'error', 
        'message': 'Position already exists ' 
    })
    



@admin_ctrl.route('/logout')
def logout():
    session.pop('logged_in_admin', None)
    # logout_user()
    return redirect('/admin/login')


@admin_ctrl.route('/support', methods=['GET', 'POST'])
def support():
    if session.get(u'logged_in_admin') is None:
        return redirect('/admin/login')
    query = db.supports.find({})
    data ={
    'support' : query,
    'title': 'Support',
    'menu' : 'support'
    }
    return render_template('admin/support.html', data=data)
@admin_ctrl.route('/support/<ids>', methods=['GET', 'POST'])
def Replysupport(ids):
    if session.get(u'logged_in_admin') is None:
        return redirect('/admin/login')
    support = db.supports.find_one({'_id': ObjectId(ids)})

    data ={
    'data_support' : support,
    'title': 'Support',
    'menu' : 'support'
    }
    return render_template('admin/reply_support.html', data=data)

@admin_ctrl.route('/support/reply-support', methods=['POST'])
def newsupporReplyt():
    if session.get(u'logged_in_admin') is None:
        flash({'msg':'Please login', 'type':'danger'})
        return redirect('/admin/login')
    if request.method == 'POST':
        user_id = session.get('user_id')
        sp_id = request.form['sp_id']
        support = db.supports.find_one({'_id': ObjectId(sp_id)})
        if support is None:
            flash({'msg':'Not Found', 'type':'danger'})
            return redirect('/admin/support/'+str(sp_id))
        else: 
            user = db.users.find_one({'_id': ObjectId(user_id)})
            message = request.form['message']
          
            if  message == '':
                flash({'msg':'Please enter message', 'type':'danger'})
            else:    
                data_support = {
                'user_id': 'admin',
                'username' : 'WordTrade Support',
                'message': message,
                'date_added' : datetime.utcnow()
                }
                db.supports.update({ "_id" : ObjectId(sp_id) }, { '$set': { "status": 1 }, '$push':{'reply':data_support } })
                flash({'msg':'Success', 'type':'success'})
                return redirect('/admin/support/'+str(sp_id))    

    return redirect('/admin/support/'+str(sp_id))



@admin_ctrl.route('/quan-ly-thiet-bi-submit', methods=['GET', 'POST'])
def QuanlythietbiSubmit():
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    if request.method == 'POST':

        fullname = request.form['fullname']
        
        address = request.form['address']
        telephone = request.form['telephone']
        description = request.form['description']
        date_added = request.form['date_added']
        profit = request.form['profit']
        datas = {
            'fullname': fullname,
            'telephone' : telephone,
            'address':address,
            'profit' : float(profit),
            'description' : description,
            'date_added': datetime.strptime(date_added, '%Y-%m-%d %H:%M:%S'),
            'date_finish' : datetime.strptime(date_added, '%Y-%m-%d %H:%M:%S') + timedelta(days=30)
        }
        db.devices.insert(datas)
        return redirect('/admin/quan-ly-thiet-bi')
    else:
        
        return redirect('/admin/quan-ly-thiet-bi')


@admin_ctrl.route('/remove/quan-ly-thiet-bi/<ids>', methods=['GET', 'POST'])
def RemoveQuanLyThietBi(ids):
    if session.get(u'logged_in_admin') is None:
        return redirect('/admin/login')
    devices = db.devices.remove({'_id': ObjectId(ids)})

    return redirect('/admin/quan-ly-thiet-bi')

@admin_ctrl.route('/edit/quan-ly-thiet-bi/<ids>', methods=['GET', 'POST'])
def EditQuanLyThietBi(ids):
    if session.get(u'logged_in_admin') is None:
        return redirect('/admin/login')
    devices = db.devices.find_one({'_id': ObjectId(ids)})
    data ={
        'ids' : ids,
        'menu' : 'quan-ly-thiet-bi',
        'history': devices
    }
    return render_template('admin/edit-quan-ly-thiet-bi.html', data=data)


@admin_ctrl.route('/edit-quan-ly-thiet-bi-submit/<ids>', methods=['GET', 'POST'])
def EditQuanlythietbiSubmit(ids):
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')

    if request.method == 'POST':

        fullname = request.form['fullname']
        
        address = request.form['address']
        telephone = request.form['telephone']
        description = request.form['description']
        date_added = request.form['date_added']
        profit = request.form['profit']
        
        db.devices.update({'_id' : ObjectId(ids)},{'$set' : {'fullname': fullname,
            'telephone' : telephone,
            'address':address,
            'profit' : float(profit),
            'description' : description,
            'date_added': datetime.strptime(date_added, '%Y-%m-%d %H:%M:%S'),
            'date_finish' : datetime.strptime(date_added, '%Y-%m-%d %H:%M:%S') + timedelta(days=30)}
        })
        return redirect('/admin/quan-ly-thiet-bi')
    else:
        
        return redirect('/admin/quan-ly-thiet-bi')