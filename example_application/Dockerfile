FROM ibmcom/spectrum-discover-application-sdk:latest

### Required labels
LABEL application_name="example"
# comma delimted list of file extensions (ex: jpg,jpeg,tiff)
LABEL filetypes="all"
LABEL description="Performs a character count on a specified file."
#smeverv2 (ex: 0.1.2)
LABEL version="0.0.2"
#license type (ex: MIT)
LABEL license="mit"

### Optional labels.
### Uncomment if in use
#LABEL company_name=""
#LABEL company_url=""
#LABEL maintainer="" # email address
#LABEL icon_url=""
# a comma delimited key,value pair (ex: param1k:param1v,param2k:param2v).
#LABEL parameters=""

COPY ExampleApplication.py requirements.txt /application/

RUN    python3 -m pip install -r /application/requirements.txt && \
       rm -f /application/requirements.txt

#RUN yum install -y pkg1 pkg2 pkg3 etc

ENTRYPOINT []
CMD ["python3", "/application/ExampleApplication.py"]
