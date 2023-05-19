# UdaConnect

This repository was created as part of Udacity [Cloud Native Application Architecture](https://www.udacity.com/course/cloud-native-application-architecture-nanodegree--nd064) nanodegree.
It is based on [project-starter files created by Udacity](https://github.com/udacity/nd064-c2-message-passing-projects-starter).

## Overview
### Background
Conferences and conventions are hotspots for making connections. Professionals in attendance often share the same interests and can make valuable business and personal connections with one another. At the same time, these events draw a large crowd and it's often hard to make these connections in the midst of all of these events' excitement and energy. To help attendees make connections, we are building the infrastructure for a service that can inform attendees if they have attended the same booths and presentations at an event.

### Goal
You work for a company that is building a app that uses location data from mobile devices. Your company has built a [POC](https://en.wikipedia.org/wiki/Proof_of_concept) application to ingest location data named UdaTracker. This POC was built with the core functionality of ingesting location and identifying individuals who have shared a close geographic proximity.

Management loved the POC so now that there is buy-in, we want to enhance this application. You have been tasked to enhance the POC application into a [MVP](https://en.wikipedia.org/wiki/Minimum_viable_product) to handle the large volume of location data that will be ingested.

To do so, ***you will refactor this application into a microservice architecture using message passing techniques that you have learned in this course***. It’s easy to get lost in the countless optimizations and changes that can be made: your priority should be to approach the task as an architect and refactor the application into microservices. File organization, code linting -- these are important but don’t affect the core functionality and can possibly be tagged as TODO’s for now!

### Technologies
* [Python Poetry](https://python-poetry.org/) - holistic venv management for Python
* [FastAPI](https://fastapi.tiangolo.com/lo/) - async REST framework for Python
* [MongoDB](https://www.mongodb.com/) - cloud native NoSQL database
* [Kind](https://kind.sigs.k8s.io/) - Kubernetes-in-Docker, "small" Kubernetes cluster suitable for development.
* [GNU Make](https://www.gnu.org/software/make/) - file generation flow control.

## Running the app
The project has been set up such that you should be able to have the project up and running with Kubernetes.

### Prerequisites

We will be installing the tools that we'll need to use for getting our environment set up properly.
**It is highly recommended to use Unix-based system - e. g. Linux, Mac or Windows Subsystem for Linux.** 
**Native-Windows setup was not tested and is not supported.**

1. [Install Docker](https://docs.docker.com/get-docker/). Various options are available, from Docker
   Desktop to raw docker-deamon installation.
2. [Install kind](https://kind.sigs.k8s.io/docs/user/quick-start).
3. [Set up `kubectl`](https://rancher.com/docs/rancher/v2.x/en/cluster-admin/cluster-access/kubectl/).
4. Install GNU Make. Please refer to your system's package manager. (E. g., on Ubuntu/Debian based
   Linux distributions, use `apt install make`.) On Windows, either install Ubuntu in Windows Subsystem
   for linux, or check the following Stack Overflow question:
   [How to install and use "make" in Windows](https://stackoverflow.com/questions/32127524/how-to-install-and-use-make-in-windows).
   Native-Windows setup has not been tested and is not supported.
5. (Optional for debugging/development.) Install Python3.10. Please refer to your system's package manager. (E. g., on Ubuntu 22.04 3.10 is the
   default Python version, so it is sufficient to `apt install python3`. On other versions, please scroll
   down to "Use Deadsnakes PPA to Install Python 3 on Ubuntu" in
   [How to Install Python in Ubuntu](https://www.makeuseof.com/install-python-ubuntu/) and follow the
   instructions. Then `apt install python3.10`.)
6. (Optional for debugging/development.) [Install Python Poetry](https://python-poetry.org/docs/#installation).

Steps 5. and 6. are required only if you want to run the code outside Docker/Kubernetes (e. g.
for interactive code debugging in some IDE.)

### Steps
1. `cd` into project directory.
2. Make sure docker daemon is running. (E. g. start Docker desktop.)
3. `make kind-init` - initialize Kind-Kubernetes cluster.
4. `make kind-udaconnect` - deploy all services to Kind cluster.
   **This command may take up to 15-30min to finish, depending on your network speed.**
   
   Feel free to check `kind-udaconnect` target in Makefile to see what commands
   are executed. The following actions are done:
    - Docker images for frontend and backends are built. This includes downloading
      all dependencies.
    - MongoDB and Kafka services are deployed to Kind cluster. This includes
      downloading MongoDB and Kafka Docker images.
    - Waiting for MongoDB and Kafka to be ready.
    - All Kubernetes manifests for UdaConnect (services & frontend) are applied.
    - Waiting for `person-api` to be ready and populating the database with initial
      data.

### Verifying it Works
Once the project is up and running, you should be able to see 8 deployments and 8 services in Kubernetes:
`kubectl get pods` and `kubectl get services` - should both return `udaconnect-app`; `person-api`, `location-api`,
`connection-api`, `connection-tracker`, `location-processor`; `mongo` and `kafka`.

These pages should also load on your web browser:
* `http://localhost:30001/docs` - OpenAPI Documentation for PersonAPI
* `http://localhost:30002/docs` - OpenAPI Documentation for LocationAPI
* `http://localhost:30003/docs` - OpenAPI Documentation for ConnectionAPI
* `http://localhost:30000/` - Frontend ReactJS Application

#### Deployment Note
You may notice the odd port numbers being served to `localhost`.
[By default, Kubernetes services are only exposed to one another in an internal network](https://kubernetes.io/docs/concepts/services-networking/service/).
This means that `udaconnect-app` and `*-api` can talk to one another. For us to connect to the cluster as an "outsider",
we need to a way to expose these services to `localhost`.

Connections to the Kubernetes services have been set up through a [NodePort](https://kubernetes.io/docs/concepts/services-networking/service/#nodeport). (While we would use a technology like an [Ingress Controller](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/) to expose our Kubernetes services in deployment, a NodePort will suffice for development.)

Moreover, you may notice we exposed MongoDB and Kafka as completely insecured services, e. g. with neither authentication
nor firewall rules to protect it from attackers. This is acceptable only for local development. If deployed online,
I would expect to use infrastructure-provider-native Kafka and Mongo deployments, which would also integrate proper
authentication mechanism native for given provider. (E. g. Azure Active Domain in MS Azure cloud.)

## Development

### Environment variables
The microservices expect the following environemnt variables to be present:
```
MONGO_CONNECTION_URI=mongodb://udaconnect_root:tinydogonaleash@localhost:27017/?authMechanism=DEFAULT
MONGO_DB_NAME=geoconnections

CONNECTION_TRACKER_HOST=localhost
CONNECTION_TRACKER_PORT=8004

KAFKA_SERVER=localhost:9094

DEBUG=False
```
The values are set up to work with prepared docker-compose deployments. If you wish
to connect to Kind-deployed services, please change the MongoDB connection url,
Connection tracker port and Kafka server port accordingly.

### Backend services
All backend services are currently present in `modules/api` subfolder, use a single Python virtual environment
and a multiple Docker images. Each service has it's own Dockerfile, which copies relevant source code parts
from the single virtual environment

For production, this should be fixed - each microservice should have its own virtual environment, possibly
even separate repository plus one shared Python package with the base app and gRPC service definitions.
We went for the single-folder approach only due to lack of time.

## Configs and Secrets
In `deployment/db-secret.yaml`, we have MongoDB connection string, which would typically contain credentials.
This is base64-encoded and not encrypted -- this is ***not*** secure! Anyone can decode it to see what it is.
```bash
# Decodes the value into plaintext
echo "d293aW1zb3NlY3VyZQ==" | base64 -d

# Encodes the value to base64 encoding. K8s expects your secrets passed in with base64
echo "hotdogsfordinner" | base64
```
This is okay for development against an exclusively local environment and we want to keep the setup simple so that you can focus on the project tasks. However, in practice we should not commit our code with secret values into our repository. A CI/CD pipeline can help prevent that.

## MongoDB & Kafka for local development

Backend microservices need MongoDB to store people-location data. It also uses Kafka to transfer new
location data to DB. For local development, you will need to run these services.
While it is possible to connect to Kubernetes/Kind deployed Kafka and Mongo, it is far from handy
(mainly due to long startup times). We recommend running Mongo and Kafka using docker compose,
for which we have Makefile targets.

**To bring MongoDB and Kafka up for local development, run the following command:**
`make docker-run-mongo docker-run-kafka`

It may take some time before the services boot up, due to Docker image download.

### Database client
To manually connect to the database, we recommend [MongoDB Compass](https://www.mongodb.com/products/compass)

## Tips
* We can access a running Docker container using `kubectl exec -it <pod_id> sh`. From there, we can `curl` an endpoint to debug network issues.
