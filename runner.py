#!/usr/bin/env python
# run with something like:
#  ./runner.py -c uploads/thumbor.conf -l debug
import tornado.gen

from thumbor.lifecycle import Events
import thumbor.server as server

@tornado.gen.coroutine
def on_resize(sender, **kwargs):
    print('async call due to resize event')

def on_after_server_run(sender, **kwargs):
    print('sync call after server is running')

Events.subscribe(Events.Engine.resize, on_resize)
Events.subscribe(Events.Server.after_server_run, on_after_server_run)

server.main()
