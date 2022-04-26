FROM ibmcom/spectrum-discover-application-sdk:latest

### Required labels
LABEL application_name="file-checksum"
# comma delimted list of file extensions (ex: jpg,jpeg,tiff)
LABEL filetypes="all"
LABEL description="Performs a checksum on a file based on the tag value received."
#smeverv2 (ex: 0.1.2)
LABEL version="0.0.2"
#license type (ex: MIT)
LABEL license="mit"

### Optional labels.
### Uncomment if in use
#LABEL company_name=""
#LABEL company_url=""
LABEL maintainer="drolson@us.ibm.com"
#LABEL icon_url=""
# a comma delimited key,value pair (ex: param1k:param1v,param2k:param2v).
#LABEL parameters=""

COPY file_checksum.py requirements.txt /application/

RUN python3 -m pip install -r /application/requirements.txt && \
    rm -f /application/requirements.txt

ENTRYPOINT []

CMD ["python3", "/application/file_checksum.py"]
