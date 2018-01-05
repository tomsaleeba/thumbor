Event bus
=========

TODO - this needs lots of expanding.

The short version is, we publish an event when an image gets uploaded via Redis.
You can subscribe to those events with a python program like:

    import time
    import redis

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    p = r.pubsub(ignore_subscribe_messages=True)
    channel_name = 'thumbor_uploads'

    def handler(msg):
      print('got "%s"' % msg['data'])

    p.subscribe(**{channel_name: handler})

    while True:
        p.get_message()
        time.sleep(0.01)

You need the Redis client, which you can get with:

    pip install redis
