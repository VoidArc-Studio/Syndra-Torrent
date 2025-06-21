#!/bin/bash
python -m grpc_tools.protoc -I ../core/proto --python_out=../gui/src --grpc_python_out=../gui/src ../core/proto/torrent.proto
