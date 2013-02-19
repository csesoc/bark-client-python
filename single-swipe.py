"""
Intended to upload a single swipe at a time for testing purposes.
"""

from bark.client import BarkClient

def read_event():
    # Stub
    return 'I am an event description'

def read_swipe():
    # Stub
    return '1am4swip3'

def main():
    client = BarkClient()

    event = read_event()
    swipe = read_swipe()

    client.register_swipe(
        event_description=event,
        swipe_data=swipe)

    # client.upload()

if __name__ == '__main__':
    main()
