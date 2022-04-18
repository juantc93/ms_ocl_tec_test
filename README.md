# ms_ocl_tec_test

to deploy the cloud run ms use this command:

gcloud run deploy --memory 4G --concurrency 1 --timeout 1200 --max-instances 1


## Patrones de diseño identificados.
-Publisher-Subscriber:Cloud Functions-> Pub/sub -> Cloud Run. Cloud funtions y Cloud run no se enteran de su existencia mutua (desacople). 
-Decorador: FastApi. un decorador permite además de manejar la petición POST, el enpoint ejectue la lógica de negocio del problema contenida en la función *trigger_process* 
-