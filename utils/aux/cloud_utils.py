import os
import logging
import pandas as pd

import gcsfs
import pandas_gbq
from google.cloud import storage
from google.cloud import bigquery
from google.oauth2 import service_account

import dotenv
dotenv.load_dotenv()


class CloudUtility:

    def __init__(self, ):
        # e.g. rising-woods-284132
        self.project_id = os.environ['GOOGLE_PROJECT_ID']
        # e.g. synthesisbucket
        self.bucket_name = os.environ['GOOGLE_BUCKET_NAME']
        self.credentials_url = os.environ['GOOGLE_APPLICATION_CREDENTIALS']

        self.credentials = service_account.Credentials.from_service_account_file(
            self.credentials_url)

        self.client = bigquery.Client(
            credentials=self.credentials, project=self.project_id)
        # Update the in-memory credentials cache (added in pandas-gbq 0.7.0).
        pandas_gbq.context.credentials = self.credentials
        pandas_gbq.context.project = self.project_id

        self.fs = gcsfs.GCSFileSystem(
            project=self.project_id, token=os.environ["GOOGLE_APPLICATION_CREDENTIALS"])

    def get_files_with_prefix_from_gcs(self, bucket_name = os.environ['GOOGLE_BUCKET_NAME'], prefix="", delimiter=None):
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        blob_names = [blob.name for blob in blobs]
        return blob_names

    def read_files_from_gcs(self, folder, prefix="", sep="\t", delimiter=None):
        read_base = "gs://" + self.bucket_name + "/"
        blobs = self.get_files_with_prefix_from_gcs(self.bucket_name, prefix=folder)
        all_data = pd.DataFrame()
        temp = pd.DataFrame()
        files_done = 0
        for blob in blobs:
            with self.fs.open(read_base + blob) as f:
                df = pd.read_csv(f, sep=sep, encoding="utf8")
                temp = pd.concat([temp, df])
                if(files_done % 1000 == 0):
                    all_data = pd.concat([all_data, temp])
                    files_done = 0
                    temp = pd.DataFrame()
                files_done = files_done + 1
        all_data = pd.concat([all_data, temp])
        return all_data

    def write_files_to_gcs(self, df, write_path, sep="\t"):
        with self.fs.open("gs://" + self.bucket_name + "/" + write_path, "w") as f:
            df.to_csv(f, encoding="utf8", index=None, sep=sep)

    @staticmethod
    def query_from_bq(query):
        """ Pass in query string
        """
        return pandas_gbq.read_gbq(query)

    def query_generic_from_bq(self, database, tablename, columns="*"):
        if(type(columns) == "list"):
            columns = ",".join(columns)
        query = "SELECT %s FROM `%s.%s`" % (columns, database, tablename)
        return self.query_big_query(query)

    def write_files_to_bq(self, df, database, tablename, mode="append"):
        destination = "%s.%s" % (database, tablename)
        df.to_gbq(destination_table=destination,
                  if_exists=mode)
