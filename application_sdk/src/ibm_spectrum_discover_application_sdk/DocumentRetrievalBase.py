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

import logging
import os
import sys
import re

ENCODING = 'utf-8'

class DocumentRetrievalFactory:
    """Factory class to create the right sort of retrieval object."""

    def create(self, application, key):
        # Connection lookup to find required type
        platform, client = application.connections.get((key.datasource, key.cluster), (None, None))

        if platform and client:
            if platform == 'COS':
                return DocumentRetrievalCOS(client)
            elif platform == 'NFS':
                return DocumentRetrievalNFS(client)
            elif platform == 'Spectrum Scale':
                return DocumentRetrievalScale(client)
            elif platform == 'Spectrum Scale Local':
                return DocumentRetrievalLocalScale(client)


class DocumentRetrievalBase(object):
    """A class to retrieve a document via a Spectrum Discover Connection."""

    def __init__(self, client):
        """Constructor."""
        # Instantiate logger
        loglevels = {'INFO': logging.INFO, 'DEBUG': logging.DEBUG,
                     'ERROR': logging.ERROR, 'WARNING': logging.WARNING}
        log_level = os.environ.get('LOG_LEVEL', 'DEBUG')
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(stream=sys.stdout,
                            format=log_format,
                            level=loglevels[log_level])
        self.logger = logging.getLogger(__name__)

        self.client = client

    def get_document(self, key):
        """
        To be implemented by the child class.

        Receives a document key that uniquely identifies a particular
        object, and is responsible for retrieving that object and
        returning the filepath.

        Returns None if object was not able to be retrieved.
        """
        self.logger.error("get_document has not been implemented for this class")
        return None

    def cleanup_document(self):
        """
        To be implemented by the child class.

        Perform cleanup and/or remove any tmp files as needed.

        Returns None.
        """
        self.logger.error("cleanup_document has not been implemented for this class")
        return None


class DocumentRetrievalCOS(DocumentRetrievalBase):

    def get_document(self, key):
        content = None
        filepath = None

        if self.client:
            obj = self.client.get_object(Bucket=key.datasource, Key=key.path.decode(ENCODING).split('/', 1)[1])
            content = obj['Body'].read()
            filepath = '/tmp/cosfile_' + str(os.getpid())
            with open(filepath, 'w', encoding=ENCODING) as f:
                f.write(content.decode(ENCODING, 'replace'))
        else:
            self.logger.error('Could not access file %s', key.path)

        return filepath

    def cleanup_document(self):
        """Cleanup files as needed."""
        filepath = '/tmp/cosfile_' + str(os.getpid())
        self.logger.debug("COS: Attempting to delete file: %s", filepath)

        try:
            os.remove(filepath)
        except FileNotFoundError:
            self.logger.error('Could not delete file %s', filepath)

        return None


class DocumentRetrievalNFS(DocumentRetrievalBase):

    def get_document(self, key):
        filepath = None

        if self.client:
            mount_path_prefix = self.client['additional_info']['local_mount']
            source_path_prefix = self.client['mount_point']
            filepath = re.sub('^' + source_path_prefix, mount_path_prefix, key.path.decode(ENCODING))
        else:
            print('No document match')

        return filepath

    def cleanup_document(self):
        """Cleanup files as needed."""
        self.logger.debug("NFS: Not doing any cleanup.")
        return None


class DocumentRetrievalScale(DocumentRetrievalBase):

    def get_document(self, key):
        filepath = None

        if self.client:
            try:
                filepath = '/tmp/scalefile_' + str(os.getpid())
                self.client.get(key.path, filepath)
            except UnicodeDecodeError:
                self.logger.error('Could not decode file %s', key.path)
            except FileNotFoundError:
                self.logger.error('Could not find file %s', key.path)

        else:
            print('No document match')

        return filepath

    def cleanup_document(self):
        """Cleanup files as needed."""
        filepath = '/tmp/scalefile_' + str(os.getpid())
        self.logger.debug("SCALE: Attempting to delete file: %s", filepath)

        try:
            os.remove(filepath)
        except FileNotFoundError:
            self.logger.error('Could not delete file %s', filepath)

        return None


class DocumentRetrievalLocalScale(DocumentRetrievalBase):

    def get_document(self, key):
        """Return Document Key."""
        return key.path

    def cleanup_document(self):
        """Cleanup files as needed."""
        self.logger.debug("Scale Local: Not doing any cleanup.")
        return None


class DocumentKey(object):
    """A class to identify a unique document on a Spectrum Discover Connection."""

    def __init__(self, doc):
        self.fkey = doc['fkey']
        self.datasource = doc['datasource']
        self.cluster = doc['cluster']
        self.path = doc['path'].encode(ENCODING)
        # a unique identifier for the connection this document belongs to.
        self.id = self.datasource + ':' + self.cluster

    def __str__(self):
        return "{}/{} -> {} (fkey: {})".format(self.datasource, self.cluster, self.path, self.fkey)
