#!/usr/bin/python -W ignore
########################################################## {COPYRIGHT-TOP} ###
# Licensed Materials - Property of IBM
# 5737-I32
#
# (C) Copyright IBM Corp. 2019
#
# US Government Users Restricted Rights - Use, duplication, or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
########################################################## {COPYRIGHT-END} ###

from ibm_spectrum_discover_application_sdk.ApplicationMessageBase import ApplicationMessageBase, ApplicationReplyMessage
from ibm_spectrum_discover_application_sdk.ApplicationLib import ApplicationBase
from ibm_spectrum_discover_application_sdk.DocumentRetrievalBase import DocumentKey, DocumentRetrievalFactory

import os

ENCODING = 'utf-8'

if __name__ == '__main__':
    registration_info = {
        "action_id": "DEEPINSPECT",
        "action_params": ["extract_tags"]
    }

    # Create sample application instance
    application = ApplicationBase(registration_info)
    # start function performs all required initializations and connections
    application.start()

    # Get a message handler (abstraction of Kafka)
    am = ApplicationMessageBase(application)

    # Need to create a document retrieval handler for each unique datasource we
    # receive in the work message, create them dynamically and store them.
    # May be persisted to re-use over multiple work messages.
    drh = {}

    # message processing loop
    while True:
        msg = am.read_message(timeout=100)  # or timeout can be zero to poll

        if msg:
            # Application can choose to parse message, or as below use provided parse function
            work = am.parse_work_message(msg)

            # similar with reply message, can construct manually, or use helpers as below
            reply = ApplicationReplyMessage(msg)

            for docs in work['docs']:
                # DocumentKey is a unique identifier for a document, amalgam of connection + name
                key = DocumentKey(docs)
                # Create and store a retriever for this if we haven't yet
                if key.id not in drh:
                    drh[key.id] = DocumentRetrievalFactory().create(application, key)

                print('PID:{} Inspecting Document:{}'.format(os.getpid(), key.path))

                # Typical workflow
                # Application does it's work on the file based on the action params
                # get_document the abstracted function that brings back the file path
                try:
                    tmpfile_path = drh[key.id].get_document(key)
                except AttributeError:
                    print("Connection does not exist for {}. Skipping.".format(key.id))
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
                            tags = {'char_count': str(len(content))}
                    except FileNotFoundError:
                        print("Could not find file: %s.", tmpfile_path)
                        reply.add_result('failed', key)
                        continue
                    ##################################################
                    ################# End Custom Code ################
                    ##################################################

                    drh[key.id].cleanup_document()
                    reply.add_result('success', key, tags)
                else:
                    reply.add_result('failed', key)

            # Finally, send our constructed reply
            am.send_reply(reply)
        else:
            # timeout
            pass
