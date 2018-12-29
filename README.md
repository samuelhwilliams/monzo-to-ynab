# Sync Monzo transactions to YNAB

A basic Google Cloud Function (GCF) that can be hooked up to a Monzo account and a YNAB Account in order to post transactions from the former to the latter.


# Installation
1) Have a Monzo account, a YNAB account, and a Google Cloud account.
2) Generate the function archive with `./make_function.sh`.
3) Create a Python 3.7 GCF; upload `function.zip` as the source.
4) Attach the following environment variables:
   1) `YNAB_TOKEN`: A personal access token from YNAB (https://app.youneedabudget.com/settings/developer)
   2) `YNAB_BUDGET_ID`: The ID of your YNAB Budget (is a uuid; can be found in the web app budget URL)
   3) `YNAB_ACCOUNT_ID`: The account id of your Monzo account in YNAB (is a uuid; can also be found via the web app URL)
   5) `MONZO_TOKEN`: A token sent by Monzo in the `token` query parameter of its webhook URL.
   4) `MONZO_ACCOUNT_ID`: Your Monzo account id (can be found from the 'List accounts' endpoint at https://developers.monzo.com/api/playground)
5) Publish the function.
6) Register a webhook with Monzo at https://developers.monzo.com/api/playground. The URL is the address of your GCF, including the `token` query parameter as specified above.


# Updating the function
1) Re-run `./make_function.sh` after making any code changes.
2) Edit your function and upload the new archive.
3) Save and wait for it to deploy.


# Todo
* Tests, ofc.
* Update transactions in YNAB when Monzo posts an update to say it's been settled.
* Update GCF code on merge to master.
