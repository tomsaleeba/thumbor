#!/usr/bin/env python
# run with something like:
#  ./runner.py -c uploads/thumbor.conf -l debug
import tornado.gen

from thumbor.lifecycle import Events
import thumbor.server as server

@tornado.gen.coroutine
def on_resize(sender, **kwargs):
    print('async call due to resize event')

@tornado.gen.coroutine
def on_before_upload(sender, **kwargs):
    print('async call due to before_upload event')

@tornado.gen.coroutine
def on_after_upload(sender, **kwargs):
    print('async call due to after_upload event')

def on_after_server_run(sender, **kwargs):
    print('sync call after server is running')

Events.subscribe(Events.Engine.resize, on_resize)
Events.subscribe(Events.Imaging.before_upload_image, on_before_upload)
Events.subscribe(Events.Imaging.after_upload_image, on_after_upload)
Events.subscribe(Events.Server.after_server_run, on_after_server_run)

server.main()
