import bark_api

class BarkAPIClient:

    session_swipes = []

    def __init__(self, username, password, verbose=False):
        self.auth_token = bark_api.get_auth_token(username, password)

    def is_known(self, card_uid):
        return card_uid in self.known_cards

    def create_identity(self, card_uid, student_number):
        bark_api.create_identity(self.auth_token, card_uid, student_number)

    def register_swipe(self, card_uid, time):
        try:
            bark_api.post_swipe(self.auth_token, self.device_id, self.event_id, time.isoformat(), card_uid)
        except e:
            pass
        finally:
            session_swipes.append({'card_uid':card_uid, 'timestamp':time})

    def get_events(self):
        return bark_api.get_events(self.auth_token)

    def set_event(self, event_id):
        self.event_id = event_id
        self.device_id = bark_api.register_device(self.auth_token, event_id)
        event = bark_api.get_event(self.auth_token, event_id)
        group_id = event['event']['group_id']
        self.known_cards = bark_api.get_member_card_uids(self.auth_token, group_id)

    def get_session_swipes(self):
        return session_swipes
