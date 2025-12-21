
$env:FLINK_API_KEY='YCZKAWZVDHIIFYLI'
$env:FLINK_API_SECRET='cfltV3lagHObhxUYc7aZObnOqvPCNJ4IbZoZ/ernvKKXEuR9BEqaQ75T+sOLASeA'
$env:FLINK_REST_ENDPOINT='https://flink.us-east1.gcp.confluent.cloud'
$env:FLINK_ORGANIZATION_ID='15ba519e-1d72-4d31-a99b-9ad8162935db'
$env:FLINK_ENVIRONMENT_ID='env-znxp3y'
$env:FLINK_COMPUTE_POOL_ID='lfcp-wd2or9'
$env:FLINK_PRINCIPAL_ID='u-k8ok5r6'

..\terraform.exe import -var-file="terraform.tfvars" "confluent_flink_statement.googleai_connection" "env-znxp3y/lfcp-wd2or9/tf-2025-12-20-191809-a8e46773-faf6-47ba-8860-cb0ebcf9364c"
