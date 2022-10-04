# app/__init__.py
# -*- coding: utf-8 -*-

import os
import json
from app.src.utils.utils import DocumentDB, IBMCOS

# definition of constants to use in the app
client = None
cos = None
COS_ENDPOINT = "https://s3.ap.cloud-object-storage.appdomain.cloud"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"

# project root directory path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# connect to IBM Cloud services (VCAP_SERVICES) using environment variables or local file
# Environment Variable (Deployment)
if 'VCAP_SERVICES' in os.environ:
    # loading the VCAP_SERVICES environment variable
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    # IBM Cloudant service is searched (must be connected in IBM Cloud to our app)
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        api_key = creds['apikey']
        host = creds['host']
        url = creds['url']
        username = creds['username']
        # the connection to IBM Cloudant is created
        client = DocumentDB(username, api_key)

    # IBM COS service is searched (must be connected in IBM Cloud to our app)
    if 'cloud-object-storage' in vcap:
            creds = vcap['cloud-object-storage'][0]['credentials']
            endpoint_url = COS_ENDPOINT
            ibm_service_instance_id = creds['resource_instance_id']
            ibm_api_key_id = creds['apikey']
            # the connection to IBM COS is created
            cos = IBMCOS(ibm_api_key_id, ibm_service_instance_id, COS_AUTH_ENDPOINT, endpoint_url)

# Environment Variable (Local)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        if 'cloud-object-storage' in vcap['services']:
            creds = vcap['services']['cloud-object-storage'][0]['credentials']
            endpoint_url = creds['endpoints']
            ibm_service_instance_id = creds['resource_instance_id']
            ibm_api_key_id = creds['apikey']
            # Constantes correspondientes a valores de IBM COS

            cos = IBMCOS(ibm_api_key_id, ibm_service_instance_id, COS_AUTH_ENDPOINT, endpoint_url)

        if 'cloudantNoSQLDB' in vcap['services']:
            creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
            api_key = creds['apikey']
            host = creds['host']
            url = creds['url']
            username = creds['username']
            # the connection to IBM Cloudant is created
            client = DocumentDB(username, api_key)
