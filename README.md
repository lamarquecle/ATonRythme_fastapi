



Installation de google cloud
    # cf : https://cloud.google.com/sdk/docs/install?hl=fr
    sudo apt-get update
    sudo apt-get install apt-transport-https ca-certificates gnupg curl
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://4efce6037615
    sudo apt-get update && sudo apt-get install google-cloud-cli

# gcloud doc
if "WANT DOC ABOUT GCLOUD":
    gcloud topic configurations >> gcloud_doc.txt

# Configuration

### See existents configurations
gcloud config list
gcloud config configurations list

gcloud config configurations describe CONFIGURATION_NAME
gcloud config configurations rename OLD_CONFIGURATION_NAME NEW_CONFIGURATION_NAME

### create a configuration
gcloud init --skip-diagnostics                     # with initialisation
gcloud config configurations create my-config      # sans initialisation

### Make an active account ###
gcloud config set account VOTRE_EMAIL@gmail.com

### Initialistion par default de gcloud ###
gcloud config set project PROJECT_ID         (cf plus bas pour en créer)
gcloud config set compute/zone ZONE_NAME
gcloud config set run/region REGION_NAME     (europe-west1)
gcloud config set account VOTRE_EMAIL@gmail.com

### Activate a configuration
gcloud config configurations activate my-config
gcloud config configurations delete   my-config
    ! une configuration ne se désactive pas, il est proposé de la supprimer ou d'en rendre una autre active

### Activate gcloud API ###
-> Activer Cloud Run, Artifact Registry API, Cloud Build
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com



# Authentification

### See existents authentification
gcloud auth list

### create an authentification
gcloud auth application-default login
gcloud auth login

### Verify valid authentification
gcloud config list account





# Projects

### Projects with my account ###
gcloud projects list

### Create a project ###
-> Créer un projet GCP
gcloud projects create <PROJECT_ID> --name="<Nom lisible>"

### Make active a project ###
gcloud config set project <PROJECT_ID>

### Information de facturations du projet ###
gcloud beta billing projects describe PROJECT_ID
    Comptes de facturation : https://console.cloud.google.com/billing?hl=fr&inv=1&invt=AbygGg

### Initialize APP Engine ###
gcloud app create --region=europe-west1







# Deploy application with Google Cloud Run
For AppEngine
    gcloud app deploy
For Cloud Run with Docker

    docker build -t gcr.io/<PROJECT_ID>/my-app .
    docker push gcr.io/<PROJECT_ID>/my-app

    gcloud run deploy <SERVICE_NAME> \
        --image=gcr.io/<PROJECT_ID>/<IMAGE_NAME> \
        --region=europe-west1 \
        --platform=managed \
        --allow-unauthenticated

For Cloud Run with source code
    gcloud run deploy <SERVICE_NAME> \
        --source=. \
        --region=europe-west1 \
        --platform=managed \
        --allow-unauthenticated

For Cloud build (deployment from Github, not clone locally)



# Reinitialise gcloud environment #
gcloud auth revoke                            # deconnect user connected
gcloud config configurations delete my_config
gcloud auth application-default revoke
gcloud init













gcloud artifacts repositories create atonrithme-fastapi --repository-format=docker --location=europe-west1 --description="Repository for FastAPI Docker images"

gcloud run deploy fastapi-service --source . --region europe-west1 --platform managed --allow-unauthenticated --port 8080
SI "MISSING REQUIRED IAM PERMISSION":
    # manuellement : https://console.cloud.google.com/iam-admin/iam   :  Rôle → Projet → Éditeur (Editor)
    gcloud projects get-iam-policy atonrythme-fastapi --filter="bindings.members:cloudbuild.gserviceaccount.com"
    NUMBER = gcloud projects describe atonrythme-fastapi --format="value(projectNumber)"
    gcloud projects add-iam-policy-binding atonrythme-fastapi --member="serviceAccount:NUMBER@cloudbuild.gserviceaccount.com" --role="roles/run.developer"
    gcloud projects add-iam-policy-binding atonrythme-fastapi --member="serviceAccount:NUMBER@cloudbuild.gserviceaccount.com" --role="roles/run.admin"
#    gcloud projects add-iam-policy-binding atonrythme-fastapi --member="serviceAccount:NUMBER@cloudbuild.gserviceaccount.com" --role="roles/artifactregistry.writer"
#    gcloud projects add-iam-policy-binding atonrythme-fastapi --member="serviceAccount:NUMBER@cloudbuild.gserviceaccount.com" --role="roles/cloudbuild.builds.editor"
    gcloud projects add-iam-policy-binding atonrythme-fastapi --member="serviceAccount:NUMBER@cloudbuild.gserviceaccount.com" --role="roles/iam.serviceAccountUser"


https://fastapi-service-967220139356.europe-west1.run.app



gcloud run services delete fastapi-service --region europe-west1
gcloud artifacts repositories delete [REPOSITORY_NAME] --location=[LOCATION]

gcloud builds triggers delete [TRIGGER_NAME]
gsutil rm -r gs://[BUCKET_NAME]
gcloud services disable [API_NAME]
gcloud projects delete [PROJECT_ID]




#!/bin/bash

PROJECT_ID="atonrythme-fastapi"
REGION="europe-west1"
SERVICE_NAME="fastapi-service"

PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CLOUDBUILD_SA="$PROJECT_NUMBER@cloudbuild.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$CLOUDBUILD_SA" \
  --role="roles/run.developer"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$CLOUDBUILD_SA" \
  --role="roles/artifactregistry.writer"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$CLOUDBUILD_SA" \
  --role="roles/iam.serviceAccountUser"

gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
#  --port 8080 \
#  --project $PROJECT_ID

