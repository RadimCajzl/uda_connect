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

docker-push: docker-build
	docker push radimcajzl/udaconnect-person-api:latest
	docker push radimcajzl/udaconnect-location-api:latest
	docker push radimcajzl/udaconnect-location-processor:latest
	docker push radimcajzl/udaconnect-connection-api:latest
	docker push radimcajzl/udaconnect-connection-tracker:latest
	docker push radimcajzl/udaconnect-udaconnect-app:latest

kind-udaconnect: docker-build kind-udaconnect-clean
	# # push docker images into kind cluster
	# # (To be used if you wish to use locally built images without upload to DockerHub.)
	# kind load docker-image radimcajzl/udaconnect-person-api:latest
	# kind load docker-image radimcajzl/udaconnect-location-api:latest
	# kind load docker-image radimcajzl/udaconnect-location-processor:latest
	# kind load docker-image radimcajzl/udaconnect-connection-api:latest
	# kind load docker-image radimcajzl/udaconnect-connection-tracker:latest
	# kind load docker-image radimcajzl/udaconnect-udaconnect-app:latest

	## apply kubernetes manifests
	# DB-config for pods
	kubectl apply --wait=true -f deployment/db-configmap.yaml
	kubectl apply --wait=true -f deployment/db-secret.yaml

	## Deploy MongoDB && Kafka
	kubectl apply --wait=true -f deployment/mongo.yaml
	kubectl apply --wait=true -f deployment/kafka.yaml
	
	# Wait for Kafka to start
	# (microservices require Kafka on start-time already.)
	kubectl wait deployment kafka --for condition=Available=True --timeout=900s

	# Set up the service and deployment for the API
	#  - replace image pull policy. For kind deployments, we already loaded
	#   the images to the cluster. If imagePullPolicy hints to check for
	#   more recent image version, kind would try to find the package
	#   in public Container Registries, which we don't want to use
	#   for fully local dev-setup.)

	## Deploy Backend microservices & frontend:
	for manifest in person-api connection-api connection-tracker location-api location-processor udaconnect-app; do\
		echo ; \
		echo deploying $$manifest.; \
		cat deployment/$$manifest.yaml | \
			# sed 's/imagePullPolicy: Always/imagePullPolicy: Never/' | \
			kubectl apply --wait=true -f -; \
	done

	## Populate database with initial data:
	# wait for Mongo & API to be ready:
	kubectl wait deployment person-api --for condition=Available=True --timeout=900s
	kubectl wait deployment mongo --for condition=Available=True --timeout=900s

	# PoC-phase has data and init-db script inside API container.
	# TODO: in production, this should be a separate job.
	kubectl exec service/person-api -- poetry run python /api/init_db.py


make kind-udaconnect-clean:
	for manifest in person-api connection-api connection-tracker location-api location-processor udaconnect-app kafka mongo; do\
		kubectl delete --ignore-not-found=true --wait=true service/$$manifest deployment.apps/$$manifest; \
	done
	
	docker exec kind-worker rm -rf '/mnt/data/*'

	
