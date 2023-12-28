## OpenSearch Benchmark Workloads

This repository contains a number of workloads that are used by OpenSearch Benchmark. The workloads have been generated from rally tracks. The primary objective of these workloads is to facilitate the comparison of metrics between Elasticsearch and OpenSearch.

### How to run the test_procedures of a workload

```
opensearch-benchmark execute-test \
--target-hosts="OPENSEARCH_ENDPOINT" --pipeline=benchmark-only --workload-path=/Users/saikatsarkar/Documents/elastic/opensearch-benchmark-workloads/wikipedia --client-options=timeout:120,amazon_aws_log_in:client_option,aws_access_key_id:<AWS_ACCESS_KEY>,aws_secret_access_key:<AWS_SECRET_ACCESS_KEY>,region:us-east-1,service:aoss,aws_session_token:<AWS_SESSION_TOKEN> --distribution-version=2.11.0 --kill-running-processes --on-error=abort --include-tasks="delete-index,create-index,standalone-query-string-search" --workload-params="initial_indexing_ingest_percentage:1" --test-mode
```
