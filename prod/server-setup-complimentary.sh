#!/usr/bin/env bash

# These are things that should be run on the local developer machine in order
# to set up the CI/CD pipeline.

# Create a new SSH key pair for the CI/CD pipeline
ssh-keygen -t rsa -b 4096 -C "gitlab-ci-key" -f gitlab_ci_deploy_key
scp -i <personal-key.pem> gitlab_ci_deploy_key.pub ubuntu@ec2-3-87-6-34.compute-1.amazonaws.com:/home/ubuntu/gitlab_ci_deploy_key.pub
ssh -i <personal-key.pem> ubuntu@ec2-3-87-6-34.compute-1.amazonaws.com "cat ~/gitlab_ci_deploy_key.pub >> ~/.ssh/authorized_keys && rm ~/gitlab_ci_deploy_key.pub"
cat ../private/gitlab_ci_deploy_key | base64 | pbcopy
# Paste to GitLab CI/CD variable (Settings -> CI/CD -> Variables -> Add variable)
# Don't forget to mask the variable.

# Copy the public key to the repository
# Add it as a deploy key in GitLab (Settings -> Repository -> Deploy Keys)
ssh -i <personal-key.pem> ubuntu@ec2-3-87-6-34.compute-1.amazonaws.com "cat /home/ubuntu/private/deploy_key.pub" | pbcopy

