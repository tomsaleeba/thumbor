#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import uuid
import mimetypes
import logging
import pika
import json

from thumbor.handlers import ImageApiHandler
from thumbor.engines import BaseEngine

logger = logging.getLogger('thumbor')

##
# Handler to upload images.
# This handler support only POST method, but images can be uploaded  :
#   - through multipart/form-data (designed for forms)
#   - or with the image content in the request body (rest style)
##
class ImageUploadHandler(ImageApiHandler):

    def post(self):
        # Check if the image uploaded is a multipart/form-data
        if self.multipart_form_data():
            file_data = self.request.files['media'][0]
            body = file_data['body']

            # Retrieve filename from 'filename' field
            filename = file_data['filename']
        else:
            body = self.request.body

            # Retrieve filename from 'Slug' header
            filename = self.request.headers.get('Slug')

        # Check if the image uploaded is valid
        if self.validate(body):

            # Use the default filename for the uploaded images
            if not filename:
                content_type = self.request.headers.get('Content-Type', BaseEngine.get_mimetype(body))
                extension = mimetypes.guess_extension(content_type.split(';', 1)[0], False)
                if extension is None:  # Content-Type is unknown, try with body
                    extension = mimetypes.guess_extension(BaseEngine.get_mimetype(body), False)
                if extension == '.jpe':
                    extension = '.jpg'  # Hack because mimetypes return .jpe by default
                if extension is None:  # Even body is unknown, return an empty string to be contat
                    extension = ''
                filename = self.context.config.UPLOAD_DEFAULT_FILENAME + extension

            # Build image id based on a random uuid (32 characters)
            image_id = str(uuid.uuid4().hex)
            self.write_file(image_id, body)
            self.set_status(201)
            location_header_value = self.location(image_id, filename)
            self.set_header('Location', location_header_value)
            self.send_event(location_header_value)

    def send_event(self, location_header_value):
        method = u'POST' # TODO support PUT and DELETE
        # TODO cache connection
        # TODO attempt reconnect if RabbitMQ connection lost
        try:
            rabbit_host = self.context.config.RABBIT_MQ_SERVER_HOST
            rabbit_port = self.context.config.RABBIT_MQ_SERVER_PORT
            rabbit_exchange_type = self.context.config.RABBIT_MQ_EXCHANGE_TYPE
            rabbit_exchange_name = self.context.config.RABBIT_MQ_EXCHANGE_NAME
            logger.debug('Connecting to RabbitMQ at %s:%d, using exchange="%s" of type="%s"'
                % (rabbit_host, rabbit_port, rabbit_exchange_name, rabbit_exchange_type))
            connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host, rabbit_port)) # TODO consider making non-blocking
            channel = connection.channel()
            channel.exchange_declare(exchange=rabbit_exchange_name, exchange_type=rabbit_exchange_type)
            msg = {
                'method': method,
                'location': location_header_value
            }
            channel.basic_publish(
                exchange=rabbit_exchange_name,
                routing_key='',
                body=json.dumps(msg))
            logger.debug('Published event to RabbitMQ: %s' % str(msg))
            connection.close()
        except Exception:
            logger.exception('Failed to publish event to RabbitMQ, continuing processing')

    def multipart_form_data(self):
        if 'media' not in self.request.files or not self.request.files['media']:
            return False
        else:
            return True

    def location(self, image_id, filename):
        base_uri = self.request.uri
        return '%s/%s/%s' % (base_uri, image_id, filename)
