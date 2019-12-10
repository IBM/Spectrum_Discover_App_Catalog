# IBM Spectrum Discover Application Catalog
The Spectrum Discover Application Catalog is meant to be a single place where customers can search, download, and deploy applications for use in IBM Spectrum Discover. These applications are provided by IBM, customers, and 3rd parties.

# Using the IBM Spectrum Discover Application Catalog
All the commands below assume you are logged into the Spectrum Discover node via ssh. It is also assumed that you have a token generated from the CLI used for authentication. This token expires after 1 hour.
You can login and generate a token with the following commands:
```
ssh moadmin@<your IP entered during mmconfigappliance>
# Enter in the password you set during the mmconfigappliance
export SD_USER=<sdadmin or another user with dataadmin privileges>
export SD_PASSWORD=<password for SD_USER above>
export OVA=images
gettoken
```
`gettoken` is an alias under the moadmin user. This will save your token in an env var called `TOKEN`
Below we will also be using aliases `tcurl` and `tcurl_json` under the moadmin user which uses the `TOKEN` var.

## Information about the endpoints
More information about the endpoints used below can be found at:\
https://www.ibm.com/support/knowledgecenter/en/SSY8AC\
Choose the version of Spectrum Discover you are running and navigate to:\
`Table of Contents -> REST API -> Application management using APIs`

## Querying the available applications
You can query the available applications available on dockerhub by running:
```
tcurl https://${OVA}/api/application/appcatalog/publicregistry | jq
```
This outout contains information gathered from the image itself and from dockerhub.

## Downloading an application image
Once you have identified an application that you would like to download you can run the following
```
tcurl_json https://localhost/api/application/appcatalog/image/ibmcom/spectrum-discover-example-application -X POST | jq
```
Where `ibmcom/spectrum-discover-example-application` was the `repo_name` from the publicregistry command above.

## Running an application
Once you have an application downloaded to your local docker cache you can run it with the following as a Kubernetes pod within Spectrum Discover:
Create a json formatted file with the following information
```
{
  "repo_name": "ibmcom/spectrum-discover-example-application",
  "version": "1.2.3",
  "description": "Unique description about your use of this application",
  "application_name": "example"
}
```
A couple notes about the json file.
1. The `repo_name` will be the same repo_name you used to download the application image.
2. The `version` will be the same as the version from the output of the publicregistry command.
3. The `description` will be a unique description based on your use of the application.
4. The `application_name` will be the name that gets registered within the policyengine. We will automatically append a `-application` to the end for easier identification.

Start the application as a Kubernetes pod
```
tcurl_json https://localhost/api/application/appcatalog/helm -d@example.json -X POST | jq
```

## Scaling an application
An application by design will process each of the records one at a time. You can scale the number of replicas the pod is running to process records in parallel.
You can scale the replicas up to 10 based on the number of partitions we have for the kafka topics.
Create a json formatted file with the following information:
```
{
  "replicas": 10
}
```

Scale the replicas:
```
tcurl_json https://localhost/api/application/appcatalog/helm/interesting-anaconda-example-application -d@replicas.json -X PATCH
```
Where `interesting-anaconda-example-application` is the combination of deployment_name and chart_name from the `Running an application` section.

## Stopping an application
If you want to stop an application (no matter the number of replicas) you can run the following command:
```
tcurl_json https://localhost/api/application/appcatalog/helm/interesting-anaconda -X DELETE | jq
```
Where `interesting-anaconda` is the chart_name when the application was started.

## Deleting an application image
To delete the application from your local docker cache, you can run the following command once the application is stopped:
```
tcurl https://localhost/api/application/appcatalog/image/ibmcom/spectrum-discover-example-application -X DELETE | jq
```

# Creating your own application to be found on the Application Catalog

## Editing Example Application with custom code
The first thing to do is to clone this repository. You can do so with the following command:
```
git clone git@github.com:IBM/Spectrum_Discover_App_Catalog.git

```
You can use the ex
From here, you can grab the example_application code and use that as a basis for creating your own custom application.
The example application is documented with comments to explain what is happening within the file, but for a lot of use cases, you will only need to edit the code between
```
################ Start Custom Code ###############
```
and
```
################# End Custom Code ################
```

## Populating Labels within Dockerfile
In the example_application Dockerfile you will see `LABELS`. Some of these are required and others are optional.
The required ones are:
   ```
   LABEL application_name="example"
   The name of the application. We will append -application to the end for identification.
   ```
   ```
   LABEL filetypes="all"
   A comma separated list of file types this application works on. For ex: jpg,jpeg,tiff.
   ```
   ```
   LABEL description="Performs a character count on a specified file."
   A description of the application.
   ```
   ```
   LABEL version="1.2.3"
   A "Semantic Versioning 2.0.0" format of this application.
   ```
   ```
   LABEL license="mit"
   A short hand description of the license the source code is published under.
   ```

The optional ones are:
   ```
   LABEL company_name=""
   The company name that published the application.
   ```
   ```
   LABEL company_url=""
   A URL linking to the company that created the application or link to the source code.
   ```
   ```
   LABEL maintainer="" # email address
   Email address of the maintainer.
   ```
   ```
   LABEL icon_url=""
   A URL to an icon to display from the UI.
   ```
   ```
   LABEL parameters=""
   A json formatted string of parameters.
   ```

## Add needed requirements
If your custom code requires any python modules, add them to the requirements.txt file. These will be installed as part of the docker image that gets created below.\
If your custom code requires any additional software packages, you can modify the RUN command in the Dockerfile as a space separated list of packages:
```
RUN yum install -y pkg1 pkg2 pkg3 etc
```

## Edit Dockerfile for application filename
If you had changed the filename of the python file (ex: ExampleApplication.py), there are two references in the Dockerfile that will need to be updated.
```
COPY ExampleApplication.py requirements.txt /application/
```
and
```
CMD ["python3", "/application/ExampleApplication.py"]
```

## Building the application image
From the folder that you added your custom code from, you can run the following command to build the docker image:
```
docker build .
```
Keep note of the last line that will look something like:
`Successfully built xxxxxxxxxxxx`

## Testing the application
A formal test suite will be coming in the future. Until then, keep in mind that applications are supported to be run as standalone python files both on Spectrum Discover and on remote machines, in a container (manual setup), and as a kubernetes pod within Spectrum Discover.

## Tagging the image
Once the application is built and tested you will need to tag the docker image based on your company or username in dockerhub along with your application name.
For example:
```
docker tag xxxxxxxxxxxx ibmcom/spectrum-discover-example-application
```

## Uploading image to Dockerhub
Once the image is built, tested, and tagged, you can upload it to your dockerhub.
```
EX: docker push ibmcom/spectrum-discover-example-application
```

## Editing short description
Once your application is uploaded to dockerhub, you have to edit the short description on the dockerhub page for that application. We use this to query available applications.
For the short description, add:
`IBM_Spectrum_Discover_Application`