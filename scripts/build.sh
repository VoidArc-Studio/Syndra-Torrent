#!/bin/bash
set -ex

# Build Rust core
cd core
cargo build --release

# Generate gRPC stubs
cd ../scripts
./generate_protoc.sh

# Install Python dependencies
cd ../gui
pip install -r requirements.txt
