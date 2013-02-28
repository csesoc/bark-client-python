"""
Various useful things for nicer coding.
"""
import os, fcntl
import struct
import json, requests
from datetime import datetime

BARK_URL = '127.0.0.1:5000'

class BarkApiException(Exception):
    pass

def post_json(url, json):
    r = requests.post(
        BARK_URL + url,
        data=json.dumps(json),
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
    return r.json()

def auth_post_json(url, auth_token, json):
    r = requests.post(
        BARK_URL + url,
        data=json.dumps(json),
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'auth_token': auth_token,
        })
    return r.json()

def get_auth_token(username, password):
    response = post_json('/login', {'username':username, 'password':password})

    if response['status'] != 'OK':
        error = 'Bark API call failed.\n' + json.dumps(response, indent=2)
        raise BarkApiException(error)

    return response['auth_token']

def get_events(self, auth_token):
    response = requests.get(BARK_URL + '/events', headers={'auth_token':auth_token})

    if response.json()['status'] != 'OK':
        error = 'Bark API call failed.\n' + json.dumps(response, indent=2)
        raise BarkApiException(error)

    return response.json()

def send_single_swipe(self, swipe):
    assert isinstance(swipe, dict)
    assert self.auth_token_ is not None, 'Set my auth_token first!'
    assert self.device_id_ is not None, 'Need to get a device ID for the event'

    data = {
        'device': self.device_id_,
        'timestamp': str(datetime.now()),
        'uid': swipe['swipe_data'],
    }

    response = self.auth_post_('/swipe', **data)
    if response['status'] != 'OK':
        error = 'Bark API call failed.\n' + json.dumps(response, indent=2)
        raise BarkApiException(error)
