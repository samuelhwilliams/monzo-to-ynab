# Sync Monzo transactions to YNAB

A basic Google Cloud Function (GCF) that can be hooked up to a Monzo account and a YNAB Account in order to post transactions from the former to the latter.


# Installation
1) Have a Monzo account, a YNAB account, and a Google Cloud account.
2) Create a Python 3.7 GCF (see [deploy-to-gcp workflow](.github/workflows/main.yml) for steps/commands)
3) Attach the following environment variables:
   1) `BASE64_KMS_ENCRYPTED_YNAB_TOKEN`: A personal access token from YNAB (https://app.youneedabudget.com/settings/developer). This is encrypted with Google Cloud's KMS and then base64 encoded.
   2) `YNAB_BUDGET_ID`: The ID of your YNAB Budget (is a uuid; can be found in the web app budget URL)
   3) `YNAB_ACCOUNT_ID`: The account id of your Monzo account in YNAB (is a uuid; can also be found via the web app URL)
   4) `MONZO_TOKEN`: A token sent by Monzo in the `token` query parameter of its webhook URL.
   5) `MONZO_ACCOUNT_ID`: Your Monzo account id (can be found from the 'List accounts' endpoint at https://developers.monzo.com/api/playground)
   6) `KMS_SECRET_RESOURCE_NAME`: The URI for the cryptographic key used to encrypt the YNAB token above.
4) Publish the function.
5) Register a webhook with Monzo at https://developers.monzo.com/api/playground. The URL is the address of your GCF, including the `token` query parameter as specified above.


# Updating the function
This function auto-deploys using [GitHub Actions](https://github.com/features/actions)

You'll need to provide some base64-encoded 'secrets':
* `GCLOUD_AUTH`: JSON service account credentials to allow GitHub to deploy the function
* `GCP_PROJECT_ID`: The project to deploy your function into.
* `GCP_REGION`: The GCP region to deploy your function into.


# Todo
Tests, ofc.
