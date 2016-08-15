# DFP Playground

This is a project that demonstrates the DoubleClick for Publishers (DFP) API
to the open source community. It also demonstrates a working example of
handling an OAuth2 web flow and good usage patterns of highly used services
in the DFP API.

[TOC]

## Overview

To use the playground, users must authenticate using OAuth2 and authorize
the application to make calls to the DFP API on the user's behalf. For new
API developers, the DFP Playground will create a new test network if your
Google account is not yet associated with any networks. In the application,
you can load various DFP entities across various services and filter on
them using PQL statements.

Please note that the DFP Playground does *not* support Python 3 as webapp2
is not fully compatible with Python 3. View the
[issue on GitHub](https://github.com/GoogleCloudPlatform/webapp2/issues/40).


## Getting Started

### Register a Google AppEngine Application

If you have not registered an AppEngine application, please do so at
https://appengine.google.com.

### Installing Python Libraries

DFP Playground relies on some dependencies listed in `requirements.txt`.
In order to install them, you first must have
[PIP](https://pip.pypa.io/en/stable/installing/) installed. Then, cd into
the project directory and run `pip install -t lib -r requirements.txt`
to install the necessary Python libraries. If you also want to run tests,
globally install the libraries listed under "Test-only dependencies".

### Creating Application Credentials

If you have not created a client ID and a client secret,
please refer to the guide at
https://developers.google.com/doubleclick-publishers/docs/authentication#webapp.

### Adding Application Credentials to Google Datastore

Navigate to the Datastore dashboard, found in the "Storage" section of the
sidebar, and click on "Create an entity." Type in "AppCredential" in the
Kind field. For the properties, specify a `client_id` and a `client_secret`,
with the values of the client ID and the client secret, respectively.
Once finished, click "Create." If done correctly, one row will show up in
the entities list.

### Deploying DFP Playground to Google AppEngine

If you have not downloaded the Google App Engine SDK for Python,
please do so at
https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python.
Then, cd into the downloaded directory and run
`python appcfg.py -A <insert_project_id_here> -V <insert_version_here>
update <insert_path_to_dfp_playground_root_dir_here>`,
replacing the placeholders with the appropriate values.

More info on deploying apps to AppEngine can be found at
https://cloud.google.com/appengine/docs/python/tools/uploadinganapp.


## Live Demo

See a live demo of this project at https://dfp-playground.appspot.com.


## Where do I submit bug reports, feature requests and patches?

All of these items can be submitted at
https://github.com/googleads/dfp-playground/issues.


## How do I get help?

Post a question to the forum for the community and API advisors:
https://groups.google.com/forum/#!forum/google-doubleclick-for-publishers-api