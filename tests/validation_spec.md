# Validation Specification

This task validates ingress drift recovery using two layers:

## 1. Visible Tests (grader.py)

The grader directly validates:

- ingress backend service name
- ingress backend service port
- TLS secret configuration
- cluster pod readiness

## 2. External Nebula Tests

Additional platform tests are executed from:

    /root/tests/test_suite.sh

These verify:

- DNS routing
- MinIO UI loading
- static asset delivery
- API health
- observability stack health

External tests are embedded in the base image to prevent tampering.