File Checksum Application
==============

Table of contents
=================

   * [Overview](#Overview)
   * [Running the application](#Running-the-application)

## Overview
This application can perform one or more checksums on a given file. The files to perform the checksum are determined by the given policy.
The tag names from the policy need to match the names that are supported from the built-in hashlib library. Currently, the following hashes
are accepted:
```
md5
sha1
sha224
sha256
sha512
sha384
sha3_224
sha3_256
sha3_384
sha3_512
```

## Running the application
There is nothing unique running this application compared to other applications / policies. There are just a few pre-reqs needed for the application to run properly.
1) Create the tag(s)
    In order to run the application, a tag is needed to let the application know which hash should be performed on each of the files. One or more tags can passed to the application from the policy. All the tags have to be valid and supported (specified above).
2) Add the tags to the policy
    When creating the policy, add the tag(s) to the 'extract_tags' values section.
