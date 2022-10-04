#!/usr/bin/env python

import requests
import logging
from urllib.parse import urlencode
import json

class HttpLoginError(Exception):
   pass

class HttpSession():
    def __init__(self, root_url, cred):
        self.root_url = root_url
        self.session = requests.session()
        self.cred = cred
        self._login()

    def _login(self):
        url = '%s/login' % self.root_url
        r = self.session.post(
                url,
                json=self.cred,
                headers={'Content-type': 'application/json'},
                verify=False)
        if r.status_code==200 and 'user' in r.json()['response'].keys():
            response = (r.json()['response']['user'])
            print("User %s is successfully authenticated:" % self.cred['email'])
            print("UserId:                %s" % response['id'])
            print("Authenticateion Token: %s" % response['authentication_token'])
            self.cred['id'] = int(response['id'])
        return r.status_code==200

    def user_man(self, data, add_user=True):  
        url = '%s/api/user' % self.root_url
        if add_user:
	        r = self.session.post(
	                url, 
	                data=data,
	                verify=False)
        else:
	        r = self.session.patch(
	                url, 
	                data=data,
	                verify=False)
        if r.status_code!=200:
            print("Received error for api call: %d, %s"  %  (r.status_code, r.content))
        else:
            print("User add succesful, %s" % r.content)

def add_user_negative_test(s):
    # duplicate user
    data = {'email': 'test3@mns.vc', 'name': 'test3', 'password': 'test1234', 'company_id': 2}
    s.user_man(data)
    data = {'email': 'test3@mns.vc', 'name': 'test3', 'password': 'test1234', 'company_id': 2}
    s.user_man(data)
    # no email provided
    data = {'name': 'test3', 'password': 'test1234', 'company_id': 2}
    s.user_man(data)
    # no name provided
    data = {'email': 'test3@mns.vc', 'password': 'test1234', 'company_id': 2}
    s.user_man(data)
    # no password provided
    data = {'email': 'test3@mns.vc', 'name': 'test3', 'company_id': 2}
    s.user_man(data)
    # no company_id provided
    data = {'email': 'test3@mns.vc', 'name': 'test3', 'password': 'test1234'}
    s.user_man(data)
    # invalid email
    data = {'email': '', 'name': 'test3', 'password': 'test1234', 'company_id': 2}
    s.user_man(data)
    # invalid password
    data = {'email': 'test3@mns.vc', 'name': 'test3', 'password': '', 'company_id': 2}
    s.user_man(data)
    # invalid company id
    data = {'email': 'test4@mns.vc', 'name': 'test4', 'password': 'test1234', 'company_id': 100}
    s.user_man(data)
    # invalid company id
    data = {'email': 'test4@mns.vc', 'name': 'test4', 'password': 'test1234', 'company_id': None}
    s.user_man(data)
    # invalid email - longer than 64 chars
    data = {'email': 'test3@mns.vc', 'name': 'test3', 'password':
            'a12345678901234567890123456789012345678901234567890123456789012345',
            'company_id': 2}
    s.user_man(data)
    # 64 numbers
    data = {'email': 'test3@mns.vc', 'name': 'test3', 'password':
            '0123456789012345678901234567890123456789012345678901234567890123',
            'company_id': 2}
    s.user_man(data)
    # 64 chars
    data = {'email': 'test3@mns.vc', 'name': 'test3', 'password':
            'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijkl',
            'company_id': 2}
    # 7 numbers 
    data = {'email': 'test3@mns.vc', 'name': 'test3', 'password':
            '0123456',
            'company_id': 2}
    s.user_man(data)
    # 7 chars
    data = {'email': 'test3@mns.vc', 'name': 'test3', 'password':
            'abcdefg',
            'company_id': 2}
    s.user_man(data)

def add_user_positive_test(s):
    data = {'email': 'test5@mns.vc', 'name': 'test5', 'password':
            '01234abcdef',
            'company_id': 2}
    s.user_man(data)
    # special char is allowed
    data = {'email': 'test6@mns.vc', 'name': 'test6', 'password':
            '01234abcdef%!&*',
            'company_id': 2}
    s.user_man(data)
    # white space is allowed
    data = {'email': 'test7@mns.vc', 'name': 'test7', 'password':
            '01234abcdef %!&*  ',
            'company_id': 2}
    s.user_man(data)

def admin_session(root_url):
    cred = {'email': "nancy@mns.vc", 'password': "Syltetoy345", 'id': 0}
    s = HttpSession(root_url, cred)
    return s

def non_admin_session(root_url):
    cred = {'email': "test5.changed.new2@mns.vc", 'password': "01234abcdef _!@*$)", 'id': 0}
    s = HttpSession(root_url, cred)
    return s

def update_user_positive_test(s):
    # change email address 
    data = {'id': 118, 
            'email': 'test5.changed.new1@mns.vc'}
    s.user_man(data, False)

    # change name
    data = {'id': 118, 
            'name': 'test5 changed new 1'}
    s.user_man(data, False)

    # change password
    data = {'id': 118, 
            'password': '01234abcdef _!@*'}
    s.user_man(data, False)

    # change company_id
    data = {'id': 118, 
            'company_id': 1}
    s.user_man(data, False)

    # change user admin 
    data = {'id': 118, 
            'admin': 1}
    s.user_man(data, False)

def update_user_positive_test_multiple_parameters(s):
    # change user with multiple parameters
    data = {'id': 118,
            'email': 'test5.changed.new2@mns.vc',
            'name': 'test5 changed new 2',
            'password': '01234abcdef _!@*$)',
            'company_id': 2, 
            'admin': 0}
    s.user_man(data, False)

def update_user_negative_test(s):
    # no user id 
    data = {'email': 'test6@mns.vc'}
    s.user_man(data, False)

    # invalid email 
    data = {'id': 113, 
            'email': ''}
    s.user_man(data, False)

    # invalid password 
    data = {'id': 113, 
            'password': ''}
    s.user_man(data, False)

    # invalid user id
    data = {'id': 1000,
            'email': 'test1000@mns.vc'
            }
    s.user_man(data, False)

    # invali parameter
    data = {'id': 112,
            'nonexis': 'does not exist'}
    s.user_man(data, False)

    # multiple invalid input data
    data = {'id': 112,
            'email': '',
            'password': ''}
    s.user_man(data, False)

def tmp(s):
    # change email address 
    data = {'id': 112, 
            'email': 'test5.changed.@mns.vc', 
            'admin': 0}
    s.user_man(data, False)

if __name__=='__main__':
    root_url = "http://nocdev.mnsbone.net:5002"

    admin_session = admin_session(root_url)
    non_admin_session = non_admin_session(root_url)

#    add_user_positive_test(admin_session)
#    add_user_positive_test(non_admin_session)
#    add_user_negative_test(admin_session)

    #update_user_positive_test(non_admin_session)
    #update_user_positive_test_multiple_parameters(admin_session)
    update_user_negative_test(admin_session)
