#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from flask import Blueprint, request, session, redirect, url_for, render_template
from flask.ext.login import login_user, logout_user, current_user, login_required
from rex import app, db
from rex.models import user_model, deposit_model, history_model, invoice_model

__author__ = 'carlozamagni'

history_ctrl = Blueprint('history', __name__, static_folder='static', template_folder='templates')


@history_ctrl.route('/history-tructiep', methods=['GET', 'POST'])
def history_tructiep():
	if session.get(u'logged_in') is None:
		return redirect('/user/login')
	uid = session.get('uid')
	query = db.historys.find({'$and' :[{'uid': uid},{'type' :'referral'}]})
	user = db.User.find_one({'customer_id': uid} )
	data ={
		'history' : query,
		'title': 'Hoa hồng trực tiếp',
		'menu' : 'history-tructiep',
		'user': user
	}
	return render_template('account/history.html', data=data)

@history_ctrl.route('/history-cancap', methods=['GET', 'POST'])
def history_cancap():
	if session.get(u'logged_in') is None:
		return redirect('/user/login')
	uid = session.get('uid')
	query = db.historys.find({'$and' :[{'uid': uid},{'type' :'hoahongcannhanh'}]})
	user = db.User.find_one({'customer_id': uid} )
	data ={
		'history' : query,
		'title': 'Hoa hồng cân cặp',
		'menu' : 'history-cancap',
		'user': user
	}
	return render_template('account/history.html', data=data)

@history_ctrl.route('/history-thunhaptrenthunhap', methods=['GET', 'POST'])
def history_trunhaptrenthunhap():
	if session.get(u'logged_in') is None:
		return redirect('/user/login')
	uid = session.get('uid')
	query = db.historys.find({'$and' :[{'uid': uid},{'type' :'thunhaptrenthunhap'}]})
	user = db.User.find_one({'customer_id': uid} )
	data ={
		'history' : query,
		'title': 'Hoa hồng thu nhập trên thu nhập',
		'menu' : 'history-thunhaptrenthunhap',
		'user': user
	}
	return render_template('account/history.html', data=data)

@history_ctrl.route('/history-thuong', methods=['GET', 'POST'])
def history_thuong():
	if session.get(u'logged_in') is None:
		return redirect('/user/login')
	uid = session.get('uid')
	query = db.historys.find({'$and' :[{'uid': uid},{'type' :'thuong'}]})
	user = db.User.find_one({'customer_id': uid} )
	data ={
		'history' : query,
		'title': 'Hoa hồng thưởng danh hiệu',
		'menu' : 'history-thuong',
		'user': user
	}
	return render_template('account/history.html', data=data)

