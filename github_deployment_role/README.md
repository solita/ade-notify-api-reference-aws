## Deployment role for Github Actions

This stack will create deployment role for Github Actions.

If you have existing Github provider in AWS Identity providers, use aws_github_provider_arn parameter to import existing one based on ARN.

```
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

cdk synth
cdk deploy
```

Use this deployment role ARN in your Github Actions to deploy Notify API solution to AWS.