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

kind-udaconnect: docker-build kind-udaconnect-clean
	# push docker images into kind cluster
	kind load docker-image udaconnect-api:latest
	kind load docker-image udaconnect-app:latest

	## apply kubernetes manifests
	# DB-config for pods
	kubectl apply --wait=true -f deployment/db-configmap.yaml
	kubectl apply --wait=true -f deployment/db-secret.yaml

	## Deploy PostgreSQL
	kubectl apply --wait=true -f deployment/mongo.yaml

	# Set up the service and deployment for the API
	#  - set FLASK_ENV to dev (sets richer logging)
	#  - replace image names with local defaults
	#  - replace image pull policy. For kind deployments, we already loaded
	#   the images to the cluster. If imagePullPolicy hints to check for
	#   more recent image version, kind would try to find the package
	#   in public Container Registries, which we don't want to use
	#   for fully local dev-setup.)
	cat deployment/udaconnect-api.yaml | \
		sed 's/value: "prod"/value: "dev"/' | \
		sed 's/imagePullPolicy: Always/imagePullPolicy: Never/' | \
		sed 's@image: udacity/nd064-udaconnect-api:latest@image: docker.io/library/udaconnect-api:latest@' | \
		kubectl apply --wait=true -f -
	cat deployment/udaconnect-app.yaml | \
		sed 's/imagePullPolicy: Always/imagePullPolicy: Never/' | \
		sed 's@image: udacity/nd064-udaconnect-app:latest@image: docker.io/library/udaconnect-app:latest@' | \
		kubectl apply --wait=true -f -

	## Populate database with initial data:
	# TODO: switch to Mongo
	# wait for PSQL to be ready:
	kubectl wait deployment mongo --for condition=Available=True --timeout=300s

	# sh scripts/run_db_command.sh $$(kubectl get pods --selector=app=postgres --output=name)


make kind-udaconnect-clean:
	kubectl delete --ignore-not-found=true --wait=true \
		service/udaconnect-api  \
		service/udaconnect-app  \
		service/mongo \
		deployment.apps/udaconnect-api  \
		deployment.apps/udaconnect-app \
		deployment.apps/mongo
	
	docker exec kind-worker rm -rf '/mnt/data/*'

	
