# Benchmarks

Measurements below were produced from this repository on 22 September 2026.

| Measurement | Result | Command |
| --- | ---: | --- |
| Training rows | 4000 | `wc -l data/nasih_training.csv` |
| Model artifact size | 1631 bytes | `stat -c%s artifacts/nasih_model.joblib` |
| Full test suite time | 7.10 seconds | `pytest -q` |
| Core branch coverage | 100% | `pytest -q` |
| Docker image size | Not measured here | `docker image inspect naish:local --format='{{.Size}}'` |
| Docker build time | Not measured here | `time docker build -t naish:local .` |

The current execution environment does not provide a Docker daemon, so Docker size and build-time values are intentionally not fabricated. The CI pipeline enforces the required 500 MB maximum and the commands above produce the two remaining real measurements on any machine with Docker available.
