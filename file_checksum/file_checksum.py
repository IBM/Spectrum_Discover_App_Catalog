#!/usr/bin/python -W ignore
########################################################## {COPYRIGHT-TOP} ###
# Licensed Materials - Property of IBM
# 5737-I32
#
# (C) Copyright IBM Corp. 2020
#
# US Government Users Restricted Rights - Use, duplication, or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
########################################################## {COPYRIGHT-END} ###
"""
File checksum Application.

Based on the tag value that comes in, this application will perform the specified checksum on the file.
Currently this application supports the following hashes from the haslib library:
  ['md5', 'sha1', 'sha224', 'sha256', 'sha512', 'sha384', 'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512']
"""

import logging
import os
import sys
import hashlib

from ibm_spectrum_discover_application_sdk.ApplicationMessageBase import ApplicationMessageBase, ApplicationReplyMessage
from ibm_spectrum_discover_application_sdk.ApplicationLib import ApplicationBase
from ibm_spectrum_discover_application_sdk.DocumentRetrievalBase import DocumentKey, DocumentRetrievalFactory

ENCODING = 'utf-8'

LOG_LEVELS = {'INFO': logging.INFO, 'DEBUG': logging.DEBUG,
              'ERROR': logging.ERROR, 'WARNING': logging.WARNING}
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(stream=sys.stdout,
                    format=LOG_FORMAT,
                    level=LOG_LEVELS[LOG_LEVEL])
logger = logging.getLogger(os.environ.get('APPLICATION_NAME', 'file-checksum'))


SUPPORTED_CHECKSUMS = ['sha3_384', 'sha1', 'sha256', 'sha512', 'sha384', 'md5', 'sha3_224', 'sha3_512', 'sha224', 'sha3_256']

def main():  # pylint: disable=too-many-locals
    """Perform checksum on given files."""
    registration_info = {
        "action_id": "DEEPINSPECT",
        "action_params": ["extract_tags"]
    }

    # Create sample application instance
    application = ApplicationBase(registration_info)
    # start function performs all required initializations and connections
    application.start()

    # Get a message handler (abstraction of Kafka)
    amb = ApplicationMessageBase(application)

    # Need to create a document retrieval handler for each unique datasource we
    # receive in the work message, create them dynamically and store them.
    # May be persisted to re-use over multiple work messages.
    drh = {}

    # message processing loop
    while True:
        msg = amb.read_message(timeout=100)  # or timeout can be zero to poll

        if msg:
            # Application can choose to parse message, or as below use provided parse function
            work = amb.parse_work_message(msg)

            # similar with reply message, can construct manually, or use helpers as below
            reply = ApplicationReplyMessage(msg)

            try:
                extract_tags = work['action_params']['extract_tags']
                unsupported_checksums = [tag for tag in extract_tags if tag not in SUPPORTED_CHECKSUMS]
                if unsupported_checksums:
                    logger.error('This application does not currently support the following checksum(s): %s. '
                                 'Please contact the maintainer or submit a PR to add support for the specified checksum(s) if needed.',
                                 str(unsupported_checksums))
                    break
            except KeyError:
                logger.error('Could not retrieve the tag value from extract_tags.')
                break

            for docs in work['docs']:

                # check to see if there are any connection updates available and close them
                check_for_connection_updates(application, drh)

                # DocumentKey is a unique identifier for a document, amalgam of connection + name
                key = DocumentKey(docs)
                # Create and store a retriever for this if we haven't yet
                if key.id not in drh:
                    drh[key.id] = DocumentRetrievalFactory().create(application, key)

                logger.info('PID: %s Inspecting Document: %s', str(os.getpid()), key.path.decode(ENCODING))

                # Typical workflow
                # Application does it's work on the file based on the action params
                # get_document the abstracted function that brings back the file path
                try:
                    tmpfile_path = drh[key.id].get_document(key)
                except AttributeError:
                    logger.info("Connection does not exist for %s. Skipping.", str(key.id))
                    reply.add_result('skipped', key)
                    continue

                if tmpfile_path:
                    # Now we have the tmpfile_path, we use the info contained in the action_params
                    # to figure out how to process it. Results are returned as a dictionary
                    # of key value pairs, to be tagged on the Discover DB

                    # As an example, a tag with a simple character count
                    # Tag names must already exist in the Discover DB

                    ##################################################
                    ################ Start Custom Code ###############
                    ##################################################
                    try:
                        with open(tmpfile_path, 'rb') as file:
                            content = file.read()
                    except FileNotFoundError:
                        logger.info("Could not find file: %s.", tmpfile_path)
                        reply.add_result('failed', key)
                        continue
                    except PermissionError:
                        logger.info("Could not open file: %s.", tmpfile_path)
                        reply.add_result('failed', key)
                        continue

                    tags = {}
                    for tag in extract_tags:
                        checksum = getattr(hashlib, tag)()
                        checksum.update(content)
                        tags[tag] = checksum.hexdigest()
                    ##################################################
                    ################# End Custom Code ################
                    ##################################################

                    drh[key.id].cleanup_document()
                    reply.add_result('success', key, tags)
                else:
                    reply.add_result('failed', key)

            # Finally, send our constructed reply
            amb.send_reply(reply)
        else:
            # timeout
            pass

def check_for_connection_updates(application, drh):
    """Check for connection updates and close connection if needed."""
    while True:
        try:
            # This will raise a KeyError when nothing is in the set
            conn = application.kafka_connections_to_update.pop()

            logger.debug("Closing connection: %s", str(conn))
            drh[conn].close_connection()

            # Always remove the element without error
            drh.pop(conn, None)
        except KeyError:
            break

if __name__ == '__main__':
    main()
