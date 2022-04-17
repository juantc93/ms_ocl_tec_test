import uvicorn
import os
import pandas as pd
from fastapi import FastAPI,Body
from google.cloud import storage
import base64
import json
from datetime import datetime as dt


PROJECT_ID="jtoro-test"
INPUT_BUCKET="jtoro-test-input-bucket"
OUTPUT_BUCKET="jtoro-test-output-bucket"
#FILE_TO_DOWNLOAD="test_cloud_function.txt.txt"
FILE_TO_DOWNLOAD="GlobalLandTemperaturesByCity.csv"
LOCAL_TEST_PATH="D:\Juan\Documents\Documentos personales"
CACHE_FOLDER="cache"
CHUNK_SIZE = 262144*10 

app = FastAPI()

def process_df(filename):
    df=pd.read_csv(os.path.join(LOCAL_TEST_PATH,"GlobalLandTemperaturesByCity.csv"))
    print (df.head())

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/",status_code=200)
def trigger_process(request:dict=Body(...)):
    print(request["message"])
    if json.loads(base64.b64decode(request["message"]["data"]))["body"]==FILE_TO_DOWNLOAD:
        if CACHE_FOLDER in os.listdir():
            for file in os.scandir(CACHE_FOLDER):
                os.remove(file.path)
            os.rmdir(CACHE_FOLDER)
        
        os.mkdir(CACHE_FOLDER)  
        storage_client = storage.Client(PROJECT_ID)
        input_bucket = storage_client.get_bucket(INPUT_BUCKET)
        input_blob = input_bucket.blob(FILE_TO_DOWNLOAD)
        input_blob.download_to_filename(os.path.join(CACHE_FOLDER,FILE_TO_DOWNLOAD))
        output_bucket=storage_client.get_bucket(OUTPUT_BUCKET)
        
        df=pd.read_csv(os.path.join(CACHE_FOLDER,FILE_TO_DOWNLOAD))
        df["Longitude"]=pd.util.hash_pandas_object(df["Longitude"])
        df["Latitude"]=pd.util.hash_pandas_object(df["Latitude"])
        for country in df["Country"].unique():
            filename="{}.csv".format(country)
            df[df["Country"]==country].to_csv(os.path.join(CACHE_FOLDER,filename),encoding='utf-8')
        for country in df["Country"].unique():
            storage_client = storage.Client(PROJECT_ID)
            output_bucket=storage_client.get_bucket(OUTPUT_BUCKET)
            output_blob=output_bucket.blob(country,chunk_size=CHUNK_SIZE)
            output_blob.upload_from_filename(os.path.join(CACHE_FOLDER,"{}.csv".format(country)))

        return {"message":"fine_tho"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
