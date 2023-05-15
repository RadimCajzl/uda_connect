grpc-python: connection_tracker_api/connection_pb2.py

%_pb2.py: %.proto
	poetry run python -m  grpc_tools.protoc -I./ --python_out=./ --grpc_python_out=./ $<