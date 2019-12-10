ExampleApplication
==============

Before starting this application:
1. Following pre-requisites are met:
    * Spectrum Discover 2.0.2 is installed and running in your environment.
    * Spectrum Discover host is reachable over the network from the node on which you want use to run the application.
    * Python 3 is installed on the system.
    * Python package manager `pip` is installed on the system.

2. Install the required python packages:
    ```sh
      $ python3 -m pip install -r requirements.txt
    ```

3. Define environment variables as follows:
    ```sh
      $ export SPECTRUM_DISCOVER_HOST=https://<spectrum_discover_host>
      $ export APPLICATION_NAME=<application_name>
      $ export APPLICATION_USER=<application_user>
      $ export APPLICATION_USER_PASSWORD=<application_user_password>
      $ export KAFKA_DIR=<directory_to_save_certificates>
      $ export LOG_LEVEL=<ERROR WARNING INFO DEBUG>
    ```

4. Now, you can start the sample application, running the code as follows:
    ```
      $ sudo -E python3 ./ExampleApplication.py
    ```

## Implementation of ExampleApplication

The code is extensively commented, and should be fairly self-evident.
The basic flow of an application is:

1. Register and initialize the application
```
    application = ApplicationBase(registration_info)
    application.start()
```
2. Get a message hander and read a message
```
    am = ApplicationMessageBase(application)
```

3. Read and parse the message
```
    msg = am.read_message(timeout=100)  # or timeout can be zero to poll
    work = am.parse_work_message(msg)
```

4. Process the message by getting a key for each document and retrieving it
```
    for docs in work['docs']:
        # DocumentKey is a unique identifier for a document, amalgam of connection + name
        key = DocumentKey(docs)
        drh = DocumentRetrievalFactory().create(application, key)

        tmpfile_path = drh.get_document(key)
```

5. Parse the content in the application specifc way. This is where the custom code is per each application.
    If you are using this as a template, you can replace the code within the "Start Custom Code" and
    "End Custom Code" sections.

6. Construct and send reply
```
     reply = ApplicationReplyMessage(msg)
     reply.add_result('success', key, tags)
     am.send_reply(reply)
```