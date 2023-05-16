kind-init:
	kind create cluster --name kind --config=kind/config.yaml

kind-clean:
	kind delete cluster --name kind

kube-events:
	kubectl get events --all-namespaces --sort-by='.lastTimestamp'

docker-build:
	docker compose build

docker-run: docker-build
	docker compose up

docker-run-mongo:
	docker compose up -d mongo

docker-run-kafka:
	docker compose up -d kafka

kind-udaconnect: docker-build kind-udaconnect-clean
	# push docker images into kind cluster
	kind load docker-image udaconnect-api:latest
	kind load docker-image udaconnect-app:latest

	## apply kubernetes manifests
	# DB-config for pods
	kubectl apply --wait=true -f deployment/db-configmap.yaml
	kubectl apply --wait=true -f deployment/db-secret.yaml

	## Deploy MongoDB
	kubectl apply --wait=true -f deployment/mongo.yaml

	# Set up the service and deployment for the API
	#  - set FLASK_ENV to dev (sets richer logging)
	#  - replace image names with local defaults
	#  - replace image pull policy. For kind deployments, we already loaded
	#   the images to the cluster. If imagePullPolicy hints to check for
	#   more recent image version, kind would try to find the package
	#   in public Container Registries, which we don't want to use
	#   for fully local dev-setup.)

	# Backend microservices:
	cat deployment/person-api.yaml | \
		sed 's/value: "prod"/value: "dev"/' | \
		sed 's/imagePullPolicy: Always/imagePullPolicy: Never/' | \
		sed 's@image: udacity/nd064-udaconnect-api:latest@image: docker.io/library/udaconnect-api:latest@' | \
		kubectl apply --wait=true -f -
	cat deployment/location-api.yaml | \
		sed 's/value: "prod"/value: "dev"/' | \
		sed 's/imagePullPolicy: Always/imagePullPolicy: Never/' | \
		sed 's@image: udacity/nd064-udaconnect-api:latest@image: docker.io/library/udaconnect-api:latest@' | \
		kubectl apply --wait=true -f -
	cat deployment/connection-api.yaml | \
		sed 's/value: "prod"/value: "dev"/' | \
		sed 's/imagePullPolicy: Always/imagePullPolicy: Never/' | \
		sed 's@image: udacity/nd064-udaconnect-api:latest@image: docker.io/library/udaconnect-api:latest@' | \
		kubectl apply --wait=true -f -
	
	# Frontend:
	cat deployment/udaconnect-app.yaml | \
		sed 's/imagePullPolicy: Always/imagePullPolicy: Never/' | \
		sed 's@image: udacity/nd064-udaconnect-app:latest@image: docker.io/library/udaconnect-app:latest@' | \
		kubectl apply --wait=true -f -

	## Populate database with initial data:
	# wait for Mongo & API to be ready:
	kubectl wait deployment location-api --for condition=Available=True --timeout=300s
	kubectl wait deployment mongo --for condition=Available=True --timeout=300s

	# PoC-phase has data and init-db script inside API container.
	# TODO: before moving to production, split the init-db script
	# to proper location.
	kubectl exec service/location-api poetry run python /api/init_db.py


make kind-udaconnect-clean:
	kubectl delete --ignore-not-found=true --wait=true \
		service/person-api  \
		service/location-api  \
		service/connection-api  \
		service/udaconnect-app  \
		service/mongo \
		deployment.apps/person-api  \
		deployment.apps/location-api  \
		deployment.apps/connection-api  \
		deployment.apps/udaconnect-app \
		deployment.apps/mongo
	
	docker exec kind-worker rm -rf '/mnt/data/*'

	
