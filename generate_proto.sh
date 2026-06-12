#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p proto_gen
python -m grpc_tools.protoc \
  -I./proto \
  --python_out=./proto_gen \
  --grpc_python_out=./proto_gen \
  proto/started_service.proto
touch proto_gen/__init__.py
echo "Proto stubs generated in proto_gen/"
