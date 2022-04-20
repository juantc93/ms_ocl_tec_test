# ms_ocl_tec_test

to deploy the cloud run ms use this command:

gcloud run deploy --memory 4G --concurrency 1 --timeout 1200 --max-instances 1

desplegar en region us central (24)

cuando se pregunte, seleccionar no permitir peticiones no auténticadas  (N)

## Patrones de diseño identificados.

- Publisher-Subscriber (similar observador):Cloud Functions-> Pub/sub -> Cloud Run. Cloud funtions y Cloud run no se enteran de su existencia mutua (desacople). 
- Decorador: FastApi. un decorador permite además de manejar la petición POST, el enpoint ejectue la lógica de negocio del problema contenida en la función *trigger_process* 

## Decisiones tomadas.
- Cloud function activada por cloud storage mediante evento *Finalizar/crear* desde el bucket jtoro-test-input-bucket.
- Subir archivos a cloud storage por chunks: La prueba local de la api fallaba con archivos de más aprox 20MB, es por esto que se decide subir los archivos utilizando chunks (atributo de la clase blob).
- Limitar la concurrencia del microservicio a 1. Para evitar multiples reprocesamientos en caso de que pub/sub envíe varias veces la misma petición. 
- Fijar el timeout de pub/sub en el maximo: 600s. Esto para que no envíe multiples reintentos durante el procesamiento
- Fijar el timeout de Cloud Run en 1200s. Esto con el fin de no enviar respuestas de fallo en caso de que el proecesamiento del archivo tomase mucho tiempo. 
- La separación de archivos y la subida al bucket de salida se realiza en dos ciclos separados, esto con el fin de que las operaciones de subida no demoraran o entorpecieran la escritura de los archivos cuando se testeaba el ms a nivel local. Es posible que el impacto no sea perceptible en el endpoint en GCP (Cloudrun + GCP)


## Oportunidades de mejora de la solución:

### A nivel de arquitectura

- Pub/sub puede enviar varias veces la misma petición. Se debe implementar la capacidad al endpoint de manejar peticiones idénticas de modo que no realice el procesamiento varias veces. Esto se soluciona parcialmente al configurar el container cloud run para soportar una concurrencia máxima de 1. El parametro de timeout para la petición en Pub/sub es de 600s, de modo que si el procesamiento toma más de 600s volverá a enviar la petición. En este caso dado el tamaño del archivo a procesar, cloud run logra realizar la tarea en aproximadamente 300s. Si el archivo fuera más grande se deben analizar otra opciones como eventarc. 

- Cloud Storage puede publicar directamente mensajes en un topic de pubsub, evitando la necesidad de programar la cloud function. 

- Usar la cloud function para activar un trabajo de Dataproc. Una desventaja sería que el tiempo que se demora en aprovisionar la workstation para el trabajo (aproxi 15 mins). Puede ser una alternativa en caso de tener que procesar archivos más grandes que puedan desbordar la capacidad de cloud run. 

- Usar la cloud function para actviar un pipeline de Dataflow.


### A nivel de implementacion del ms.

- validación de que el archivo *.csv sea efectivamente un csv que pueda ser procesado por el método/función read_csv(). Esto debido a que a veces las personas guardan archivos XLSX o xls con terminación .CSV. 

- Evaluar la implementación de un framework de procesamiento de datos más rápido que pandas. 

- Quitar las variables quemadas como los nombres de los buckets y volverlas variables de entorno al momento de desplegar el contenedor.

## Componente teórico.

Debido a la descripción de la tarea encomendada se sugiere que el producto de google a utilizar sea Dataflow ya que tiene la capacidad de procesamiento de grandes cantidades de datos en paralelo y es una solución serverless. Este servicio se apalanca en Apache Beam por lo que el pipeline de procesamiento de datos puede ser escrito tanto en Java, Python o GO Usando la librería Tink (Tink está disponible para Java,C++,Go y Python)para la encriptación de las 5 columnas. Dataflow puede interactuar con las llaves que se encuentran en el cloud Key management system para hacer cifrado y descifrado de los datos mediante Tink en el DAG que se defina. También se pueden definir otros métodos alternativos para administrar las llaves de encriptación.
El archivo de salida puede ser dispuesto en Bigquery o Cloud Storage

