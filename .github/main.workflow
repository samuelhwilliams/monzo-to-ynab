workflow "deploy-to-gcp" {
  resolves = ["deploy-function"]
  on = "push"
}

action "only-master" {
  uses = "actions/bin/filter@25b7b846d5027eac3315b50a8055ea675e2abd89"
  args = "branch master"
}

action "gcp-auth" {
  uses = "actions/gcloud/auth@dc2b6c3bc6efde1869a9d4c21fcad5c125d19b81"
  needs = ["only-master"]
  secrets = ["GCLOUD_AUTH"]
}

action "deploy-function" {
  uses = "actions/gcloud/cli@dc2b6c3bc6efde1869a9d4c21fcad5c125d19b81"
  needs = ["gcp-auth"]
  args = "functions deploy monzo-to-ynab --region ${GCP_REGION} --project ${GCP_PROJECT_ID} --trigger-http --runtime python37 --source ."
  secrets = [
    "GCLOUD_AUTH",
    "GCP_PROJECT_ID",
    "GCP_REGION",
  ]
}
