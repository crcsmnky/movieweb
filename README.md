# Hello and Welcome to MovieWeb

MovieWeb is a project meant to demonstrate some of the particulars of [Istio](http://istio.io). 

## Data

This sample uses data from [MovieLens](https://grouplens.org/datasets/movielens/), specifically the ["latest small"](http://files.grouplens.org/datasets/movielens/ml-latest-small.zip) dataset. The dataset is available as exports for Cloud SQL/MySQL, Cloud Firestore, and MongoDB. For more information check out [dataset/README](dataset/README.md).

## Prerequisites

* [`gcloud`](https://cloud.google.com/sdk)
* [`skaffold`](https://skaffold.dev)

## Setup

### Kubernetes Engine and Istio Add-On

```bash
gcloud beta container clusters create [CLUSTER-NAME] \
--addons=Istio --istio-config=auth=MTLS_PERMISSIVE \
--cluster-version=latest \
--machine-type=n1-standard-2 \
--num-nodes=4

gcloud container clusters get-credentials [CLUSTER-NAME]

kubectl create namespace movieweb
kubectl label namespace movieweb istio-injection=enabled
```

### Service accounts

Cloud SQL

```bash
gcloud iam service-accounts create cloudsql-client --display-name "cloudsql-client"

gcloud projects add-iam-policy-binding [PROJECT-ID] \
--member serviceAccount:cloudsql-client@[PROJET-ID].iam.gserviceaccount.com \
--role roles/cloudsql.client

gcloud iam service-accounts keys create backend/cloudsql/cloudsql-credentials.json \
--iam-account cloudsql-client@[PROJECT-ID].iam.gserviceaccount.com
```

Cloud Firestore

```bash
gcloud iam service-accounts create cloudfirestore-user --display-name "cloudfirestore-user"

gcloud projects add-iam-policy-binding [PROJECT-ID] \
--member serviceAccount:cloudfirestore-user@[PROJET-ID].iam.gserviceaccount.com \
--role roles/datastore.user

gcloud iam service-accounts keys create backend/firestore/cloudfirestore-credentials.json \
--iam-account cloudfirestore-user@[PROJECT-ID].iam.gserviceaccount.com
```

### Secrets

Cloud SQL

```bash
kubectl create secret generic cloudsql-credentials \
--from-file=backend/cloudsql/cloudsql-credentials.json \
-n movieweb
```

Cloud Firestore

```bash
kubectl create secret generic cloudfirestore-credentials \
--from-file=backend/firestore/cloudfirestore-credentials.json \
-n movieweb
```

### MongoDB

```
gcloud deployment-manager deployments create mongodb-instance \
--config=dataset/mongodb-instance.yaml \
--template=dataset/mongodb-instance.jinja
```

### Building images

```
skaffold build
```

### Deploying microservices

```
skaffold deploy
```

## Cleanup

* Delete GKE cluster
* Delete MongoDB instance
* Delete service accounts
