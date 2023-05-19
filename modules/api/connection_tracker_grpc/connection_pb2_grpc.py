# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from connection_tracker_grpc import \
    connection_pb2 as connection__tracker__api_dot_connection__pb2


class ConnectionTrackerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Get = channel.unary_stream(
            "/ConnectionTracker/Get",
            request_serializer=connection__tracker__api_dot_connection__pb2.ConnectionRequest.SerializeToString,
            response_deserializer=connection__tracker__api_dot_connection__pb2.Connection.FromString,
        )


class ConnectionTrackerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Get(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_ConnectionTrackerServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "Get": grpc.unary_stream_rpc_method_handler(
            servicer.Get,
            request_deserializer=connection__tracker__api_dot_connection__pb2.ConnectionRequest.FromString,
            response_serializer=connection__tracker__api_dot_connection__pb2.Connection.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "ConnectionTracker", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class ConnectionTracker(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Get(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_stream(
            request,
            target,
            "/ConnectionTracker/Get",
            connection__tracker__api_dot_connection__pb2.ConnectionRequest.SerializeToString,
            connection__tracker__api_dot_connection__pb2.Connection.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
