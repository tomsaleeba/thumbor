# Event bus

TODO - this needs lots of expanding.

The short version is, when an image gets uploaded we publish an event via RabbitMQ.
You can subscribe to those events with a python program like:

    #!/usr/bin/env python
    import pika

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    exchange_name = u'thumbor_exchange' # update if you've changed the config
    channel.exchange_declare(exchange=exchange_name,
                            exchange_type='fanout')

    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange=exchange_name,
                      queue=queue_name)

    def callback(ch, method, properties, body):
      print("[x] Received %r" % body)

    channel.basic_consume(callback, queue=queue_name, no_ack=True)

    print(' [*] Waiting for messages. To exit press ^c')
    channel.start_consuming()

You need `pika` the RabbitMQ client, which you can get with:

    pip install pika
