# UdaConnect
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

**TODO: add a section about kind-based setup.**
**TODO: local dev/debug setup**: docker-compose mongo and kafka

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

**TODO: switch to python-poetry**
**TODO: switch to MongoDB**
**TODO: docker-compose**

### New Services
New services can be created inside of the `modules/` subfolder. You can choose to write something new with Flask, copy and rework the `modules/api` service into something new, or just create a very simple Python application.

As a reminder, each module should have:
1. `Dockerfile`
2. Its own corresponding DockerHub repository
3. `requirements.txt` for `pip` packages
4. `__init__.py`

### Docker Images
`udaconnect-app` and `udaconnect-api` use docker images from `udacity/nd064-udaconnect-app` and `udacity/nd064-udaconnect-api`. To make changes to the application, build your own Docker image and push it to your own DockerHub repository. Replace the existing container registry path with your own.

## Configs and Secrets
In `deployment/db-secret.yaml`, the secret variable is `d293aW1zb3NlY3VyZQ==`. The value is simply encoded and not encrypted -- this is ***not*** secure! Anyone can decode it to see what it is.
```bash
# Decodes the value into plaintext
echo "d293aW1zb3NlY3VyZQ==" | base64 -d

# Encodes the value to base64 encoding. K8s expects your secrets passed in with base64
echo "hotdogsfordinner" | base64
```
This is okay for development against an exclusively local environment and we want to keep the setup simple so that you can focus on the project tasks. However, in practice we should not commit our code with secret values into our repository. A CI/CD pipeline can help prevent that.

## PostgreSQL Database
The database uses a plug-in named PostGIS that supports geographic queries. It introduces `GEOMETRY` types and functions that we leverage to calculate distance between `ST_POINT`'s which represent latitude and longitude.

_You may find it helpful to be able to connect to the database_. In general, most of the database complexity is abstracted from you. The Docker container in the starter should be configured with PostGIS. Seed scripts are provided to set up the database table and some rows.
### Database Connection
While the Kubernetes service for `postgres` is running (you can use `kubectl get services` to check), you can expose the service to connect locally:
```bash
kubectl port-forward svc/postgres 5432:5432
```
This will enable you to connect to the database at `localhost`. You should then be able to connect to `postgresql://localhost:5432/geoconnections`. This is assuming you use the built-in values in the deployment config map.
### Software
To manually connect to the database, you will need software compatible with PostgreSQL.
* CLI users will find [psql](http://postgresguide.com/utilities/psql.html) to be the industry standard.
* GUI users will find [pgAdmin](https://www.pgadmin.org/) to be a popular open-source solution.

## Architecture Diagrams
Your architecture diagram should focus on the services and how they talk to one another. For our project, we want the diagram in a `.png` format. Some popular free software and tools to create architecture diagrams:
1. [Lucidchart](https://www.lucidchart.com/pages/)
2. [Google Docs](docs.google.com) Drawings (In a Google Doc, _Insert_ - _Drawing_ - _+ New_)
3. [Diagrams.net](https://app.diagrams.net/)

## Tips
* We can access a running Docker container using `kubectl exec -it <pod_id> sh`. From there, we can `curl` an endpoint to debug network issues.
