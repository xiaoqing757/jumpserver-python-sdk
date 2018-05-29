# -*- coding: utf-8 -*-
#

from .exception import ResponseError, RequestError
from .models import User
from .request import Http


class UsersMixin:
    def __init__(self, endpoint, auth=None):
        self.endpoint = endpoint
        self.auth = auth
        self.http = Http(endpoint, auth=self.auth)

    @property
    def role(self):
        user = self.get_profile()
        if user:
            return user.role
        else:
            return "Unknown"

    def authenticate_otp(self, seed, otp_code):
        data = {
            'seed': seed,
            'otp_code': otp_code
        }

        try:
            resp = self.http.post('user-otp-auth', data=data, use_auth=False)
        except (ResponseError, RequestError):
            return False

        if resp.status_code == 200:
            return True
        else:
            return False

    def authenticate_sms(self, sms_code, code, remote_addr):
        data = {
            'code': code,
            'sms_code': sms_code,
            'remote_addr': remote_addr
        }

        try:
            resp = self.http.post('user-sms-auth', data=data, use_auth=False)
        except (ResponseError, RequestError):
            return False

        if resp.status_code == 200:
            return True
        else:
            return False

    def authenticate(self, username, password="", public_key="",
                     remote_addr="", login_type='T'):
        data = {
            'username': username,
            'password': password,
            'public_key': public_key,
            'remote_addr': remote_addr,
            'login_type': login_type,
        }
        try:
            resp = self.http.post('user-auth', data=data, use_auth=False)
        except (ResponseError, RequestError):
            return None, None

        if resp.status_code == 200:
            user = User.from_json(resp.json()["user"])
            token = resp.json()["token"]
            return {'user': user, 'token': token}
        elif resp.status_code == 300:
            user = User.from_json(resp.json()["user"])
            seed = resp.json().get('seed', None)
            sms_code = resp.json().get('sms_code', None)
            return {'user': user, 'seed': seed, 'sms_code': sms_code}
        else:
            return dict()

    def check_user_cookie(self, session_id, csrf_token):
        try:
            headers = {"Cookie": "csrftoken={};sessionid={}".format(csrf_token, session_id)}
            resp = self.http.get('user-profile', headers=headers, use_auth=False)
        except (RequestError, ResponseError):
            return None
        return User.from_json(resp.json())

    def check_user_with_authorization(self, authorization):
        try:
            headers = {"Authorization": authorization}
            resp = self.http.get('user-profile', headers=headers, use_auth=False)
        except (ResponseError, ResponseError):
            return None
        return User.from_json(resp.json())

    def get_profile(self):
        try:
            resp = self.http.get('my-profile', use_auth=True)
        except (RequestError, ResponseError):
            return None

        user = User.from_json(resp.json())
        return user

    def get_connection_token_info(self, token):
        try:
            params = {"token": token}
            resp = self.http.get('connection-token', params=params)
        except (ResponseError, RequestError):
            return {}
        return resp.json()

    def get_user_profile(self, user_id):
        try:
            resp = self.http.get('user-user', pk=user_id)
        except (RequestError, RequestError):
            return None
        if resp.status_code == 200:
            user = User.from_json(resp.json())
            return user
        else:
            return None
