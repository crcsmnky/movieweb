# MovieLens Data

See [MovieLens Data Export](https://github.com/crcsmnky/movielens-data-exports) for information on how to restore data for MongoDB, Cloud SQL, and Cloud Firestore backends.

## MongoDB Instance

First open [mongodb-instance.yaml](mongodb-instance.yaml) and update the following variables:

* `bucketPath`: the Cloud Storage bucket path to the MongoDB `mongodump` files
* `databaseName`: the name for the database within MongoDB

Next use `gcloud` to deploy the instance:

```bash
gcloud deployment-manager deployments create \
  mongodb-instance \
  --config=mongodb-instance.yaml \
  --template=mongodb-instance.jinja
```
