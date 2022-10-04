from cloudant.client import Cloudant
import ibm_boto3
from ibm_botocore.client import Config
from ibm_botocore.client import ClientError
import pickle
from io import BytesIO


class DocumentDB:
    """
        Class to manage the IBM Cloudant document database
    """

    def __init__(self, username, api_key):
        """
            IBM cloudant connection builder

            Args:
               username (str): user.
               apikey (str): API key.
        """
        self.connection = Cloudant.iam(username, api_key, connect=True)
        self.connection.connect()

    def get_database(self, db_name):
        """
            Function to get the chosen database.

            Args:
               db_name (str):  Database name.

            Returns:
               Database. Connection to the chosen database.
        """
        return self.connection[db_name]

    def database_exists(self, db_name):
        """
            Function to check if the database exists.

            Args:
               db_name (str):  Database name.

            Returns:
               boolean. Exist or not of the database.
        """
        return self.get_database(db_name).exists()

    def create_document(self, db, document_dict):
        """
            Function to create a document in the database

            Args:
               db (str):  Connection to a database.
               document_dict (dict):  Document to insert.
        """
        db.create_document(document_dict)


class IBMCOS:
    """
        Class to manage the repository of IBM COS objects
    """

    def __init__(self, ibm_api_key_id, ibm_service_instance_id, ibm_auth_endpoint, endpoint_url):
        """
            Constructor of the connection to IBM COS

            Args:
               ibm_api_key_id (str): API key.
               ibm_service_instance_id (str): Service Instance ID.
               ibm_auth_endpoint (str): Auth Endpoint.
               endpoint_url (str): Endpoint URL.
        """
        self.connection = ibm_boto3.resource("s3",
                                             ibm_api_key_id=ibm_api_key_id,
                                             ibm_service_instance_id=ibm_service_instance_id,
                                             ibm_auth_endpoint=ibm_auth_endpoint,
                                             config=Config(signature_version="oauth"),
                                             endpoint_url=endpoint_url)

    def save_object_in_cos(self, obj, name, timestamp, bucket_name='deposittitanic'):
        """
            Function to save object in IBM COS.

            Args:
               obj:  Object to save.
               name (str):  Name of the object to save.
               timestamp (float): Seconds elapsed.

            Kwargs:
                bucket_name (str): chosen COS deposit.
        """

        # objeto serializado
        pickle_byte_obj = pickle.dumps(obj)
        # nombre del objeto en COS
        pkl_key = name + "_" + str(int(timestamp)) + ".pkl"

        try:
            # guardado del objeto en COS
            self.connection.Object(bucket_name, pkl_key).put(
                Body=pickle_byte_obj
            )
        except ClientError as be:
            print("CLIENT ERROR: {0}\n".format(be))
        except Exception as e:
            print("Unable to create object: {0}".format(e))

    def get_object_in_cos(self, key, bucket_name='deposittitanic'):
        """
            Function to get an IBM COS object.

            Args:
               key (str):  Name of the object to get from COS.

            Kwargs:
                bucket_name (str): chosen COS repository.

            Returns:
               obj. Downloaded object.
        """

        # conexión de E/S de bytes
        with BytesIO() as data:
            # descarga del objeto desde COS
            self.connection.Bucket(bucket_name).download_fileobj(key, data)
            data.seek(0)
            # des-serialización del objeto descargado
            obj = pickle.load(data)
        return obj
