FROM ibmcom/spectrum-discover-application-sdk:latest

### Required labels
LABEL application_name="exif-header-extractor"
# comma delimted list of file extensions (ex: jpg,jpeg,tiff)
LABEL filetypes="jpg,jpeg,tiff"
LABEL description="Extracts exif header information for jpeg, tiff files"
#smeverv2 (ex: 0.1.2)
LABEL version="0.0.4"
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

COPY exif_header_extractor.py requirements.txt /application/

RUN    python3.6 -m pip install -r /application/requirements.txt && \
       rm -f /application/requirements.txt

ENTRYPOINT []
CMD ["python3.6", "/application/exif_header_extractor.py"]
