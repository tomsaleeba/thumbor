#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
'''
Thumbor request lifecycle events.

Thumbor's extensions should use these events to hook functionality.

All events are coroutines.

Example:

    from tornado import gen, ioloop
    from thumbor import Events

    @gen.coroutine
    def on_request_received_handler(sender, request):
        # do something
        return 'done'

    Events.subscribe(Events.Imaging.request_received, on_request_received_handler)
'''

import tornado.gen
from tornado import ioloop
from blinker import signal as sync_signal
from blinker.base import NamedSignal
from asyncblink import signal, NamedAsyncSignal

def scheduler(future):
    '''thumbor scheduler function. Use it in blinker.'''
    loop = ioloop.IOLoop.instance()
    loop.add_future(future, lambda f: f)
    return future

class Events(object):
    '''Thumbor's request lifecycle events'''


    class Server(object):  # pylint: disable=too-few-public-methods
        'Server events'
        # Server Parameter Parsing Events
        before_server_parameters = sync_signal(
            'server.before_server_parameters')
        after_server_parameters = sync_signal('server.after_server_parameters')

        # Configuration loading events
        before_config = sync_signal('server.before_config')
        after_config = sync_signal('server.after_config')

        # Configuration loading events
        before_log_configuration = sync_signal(
            'server.before_log_configuration')
        after_log_configuration = sync_signal('server.after_log_configuration')

        # Importer loading events
        before_importer = sync_signal('server.before_importer')
        after_importer = sync_signal('server.after_importer')

        # Application Start events
        before_application_start = sync_signal(
            'server.before_application_start')
        after_application_start = sync_signal('server.after_application_start')

        # Application Handler events
        before_app_handlers = sync_signal('server.before_app_handlers')
        after_app_handlers = sync_signal('server.after_app_handlers')

        # Server Run events
        before_server_run = sync_signal('server.before_server_run')
        after_server_run = sync_signal('server.after_server_run')
        before_server_block = sync_signal('server.before_server_block')

    class Imaging(object):  # pylint: disable=too-few-public-methods
        'Imaging events - happen when transforming the image'
        before_finish_request = signal('imaging.before_finish_request')
        before_finish_request.scheduler=scheduler
        after_finish_request = signal('imaging.after_finish_request')
        after_finish_request.scheduler=scheduler

        # Event executed before processing anything else
        request_received = signal('imaging.received')
        request_received.scheduler=scheduler

        # Parsing Arguments Events
        before_parsing_arguments = signal('imaging.before_parsing_arguments')
        before_parsing_arguments.scheduler=scheduler
        after_parsing_arguments = signal('imaging.after_parsing_arguments')
        after_parsing_arguments.scheduler=scheduler

        # Source Image loading events
        before_loading_source_image = signal(
            'imaging.before_loading_source_image')#, scheduler=scheduler)
        load_source_image = signal('imaging.loading_source_image')#, scheduler=scheduler)
        after_loading_source_image = signal(
            'imaging.after_loading_source_image')#, scheduler=scheduler)
        source_image_not_found = signal('imaging.source_image_not_found')#, scheduler=scheduler)
        source_image_already_loaded = signal(
            'imaging.source_image_already_loaded')#, scheduler=scheduler)

        # Image transformation events
        before_transforming_image = signal('imaging.before_transforming_image')#, scheduler=scheduler)
        after_transforming_image = signal('imaging.after_transforming_image')#, scheduler=scheduler)

    class Engine(object):  # pylint: disable=too-few-public-methods
        'Engine methods events'
        before_read_image = signal('engine.before_read_image')#, scheduler=scheduler)
        read_image = signal('engine.read_image')#, scheduler=scheduler)
        after_read_image = signal('engine.after_read_image')#, scheduler=scheduler)

        before_resize = signal('engine.before_resize')#, scheduler=scheduler)
        resize = signal('engine.resize')#, scheduler=scheduler)
        after_resize = signal('engine.after_resize')#, scheduler=scheduler)

        before_crop = signal('engine.before_crop')#, scheduler=scheduler)
        crop = signal('engine.crop')#, scheduler=scheduler)
        after_crop = signal('engine.after_crop')#, scheduler=scheduler)

        before_reorientate = signal('engine.before_reorientate')#, scheduler=scheduler)
        reorientate = signal('engine.reorientate')#, scheduler=scheduler)
        after_reorientate = signal('engine.after_reorientate')#, scheduler=scheduler)

        before_serialize = signal('engine.before_serialize')#, scheduler=scheduler)
        serialize = signal('engine.serialize')#, scheduler=scheduler)
        after_serialize = signal('engine.after_serialize')#, scheduler=scheduler)

        get_image_data_as_rgb = signal('engine.get_image_data_as_rgb')#, scheduler=scheduler)
        get_image_size = signal('engine.get_image_size')#, scheduler=scheduler)

    class Healthcheck(object):  # pylint: disable=too-few-public-methods
        'Healthcheck events'
        before_healthcheck = signal('healthcheck.before_healthcheck')#, scheduler=scheduler)
        healthcheck = signal('healthcheck.execute')#, scheduler=scheduler)
        after_healthcheck = signal('healthcheck.after_healthcheck')#, scheduler=scheduler)

    def __init__(self):
        raise RuntimeError('Events class should not be instantiated.')

    @classmethod
    def get(cls, name):
        '''Returns an event by name'''
        if 'server' not in name:
            return signal(name)#, scheduler=scheduler)
        return sync_signal(name)

    @classmethod
    def trigger_sync(cls, event, sender, **kw):
        'Triggers a synchronous event'
        if not isinstance(event, NamedSignal):
            raise RuntimeError(
                'Async signals can\'t be triggered synchronously: %s.' %
                event.name)
        return event.send(sender, **kw)

    @classmethod
    @tornado.gen.coroutine
    def trigger(cls, event, sender, **kw):
        'Triggers an asynchronous event'
        if not isinstance(event, NamedAsyncSignal):
            raise RuntimeError(
                'Sync signals can\'t be triggered asynchronously: %s.' %
                event.name)
        event_action = event.send(sender, **kw)
        if event_action:
            resp = yield event_action[0][1]
            return resp
        return None

    @classmethod
    def subscribe(cls, event, handler):
        'Subscribes to an event'
        event.connect(handler)
