#!/usr/bin/env sh
set -eu

start=$(date +%s)
docker build -t naish:benchmark .
end=$(date +%s)
size=$(docker image inspect naish:benchmark --format='{{.Size}}')

echo "docker_build_seconds=$((end - start))"
echo "docker_image_bytes=$size"
