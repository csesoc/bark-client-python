import json
import requests

API_URL = 'https://api.bark.csesoc.unsw.edu.au'

def bark_request(method, endpoint, **kwargs):
    """
    Accepts an auth_token parameter in kwargs
    """
    url = API_URL + endpoint
    if 'auth_token' in kwargs:
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['auth_token'] = kwargs['auth_token']
        del kwargs['auth_token']
    kwargs['timeout'] = 5
    return getattr(requests, method)(url, verify=False, **kwargs)

def json_request(method, endpoint, json_dict=None, **kwargs):
    if json_dict is not None:
        msg = json.dumps(json_dict)
        kwargs['data'] = msg
    if 'headers' not in kwargs:
        kwargs['headers'] = {}
    kwargs['headers']['Accept'] = 'application/json'
    kwargs['headers']['Content-Type'] = 'application/json'
    return bark_request(method, endpoint, **kwargs).json()

def get_auth_token(username, password):
    response = json_request('post', '/login', 
                   dict(username=username, password=password))
    
    return response['auth_token']

def get_event(auth_token, event_id):
    url = '/events/' + str(event_id)
    response = json_request('get', url,  auth_token=auth_token)
    return response

def get_events(auth_token):
    response = json_request('get', '/events', auth_token=auth_token)
    return response['events']

def register_device(auth_token, event_id):
    response = json_request('post', '/devices',
                   dict(event_id=event_id),
                   auth_token=auth_token)

    return response['id']

def post_swipe(auth_token, device_id, event_id, timestamp, card_uid):
    json_dict = dict(device_id=device_id, event_id=event_id, 
                     timestamp=timestamp, card_uid=card_uid)
    response = json_request('post', '/swipes',
                   json_dict,
                   auth_token=auth_token)
    return response

def create_identity(auth_token, swipe, zid):
    response = json_request('post', '/persons', dict(card_uid=swipe, student_number=zid), auth_token=auth_token, timeout=5)
    return response

def get_member_card_uids(auth_token, group_id):
    url = '/groups/' + str(group_id) + '/card_uids'
    response = json_request('get', url,  auth_token=auth_token, timeout=5)
    return response['card_uids']
