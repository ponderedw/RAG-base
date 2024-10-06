#!/usr/bin/env bash


# Install dependencies
sudo apt -y update
sudo apt -y upgrade
sudo apt install -y \
    python3.12-venv \
    s3fs \
    docker.io

# Add the current user to the docker group
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker

# Install docker compose
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.29.1/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

# Create Python venv and make sure it's activated automatically.
mkdir -p venvs/search-doc-poc
python3 -m venv venvs/search-doc-poc
source venvs/search-doc-poc/bin/activate
sed -i '$ a\\n# Automatically activate Python venv\nif [ -f "/home/ubuntu/venvs/search-doc-poc/bin/activate" ]; then\n    source /home/ubuntu/venvs/search-doc-poc/bin/activate\nfi' ~/.bashrc

# Make sure that the S3 bucket is automatically mounted on boot.
# Options include:
# - `iam_role=auto` to use the instance's IAM role to access the bucket.
# - `uid=1000,gid=1000` to set the owner and group of the mounted files to the user `ubuntu`.
# - `umask=0022` to set the permissions of the mounted files to `755`. This means that everyone can read the files, but only the owner can write to them.
sudo sed -i '$ a\s3fs#doc-search-poc /mnt/s3bucket fuse _netdev,allow_other,iam_role=auto,uid=1000,gid=1000,umask=0022 0 0' /etc/fstab

# Create GitLab read key and add it to the SSH agent
mkdir private
ssh-keygen -t rsa -b 4096 -C "deploy-key" -f private/deploy_key -N ""
eval "$(ssh-agent -s)"
touch ~/.ssh/config
sed -i '/^Host gitlab.com$/,/^$/d' ~/.ssh/config && echo -e "\nHost gitlab.com\n    IdentityFile /home/ubuntu/private/deploy_key\n    IdentitiesOnly yes\n" >> ~/.ssh/config
# Add the public key to the repository as a deploy key: Settings -> Repository -> Deploy Keys.

# Clone the repository
mkdir source && cd source
ssh-keyscan -H gitlab.com >> ~/.ssh/known_hosts
git clone git@github.com:your-user/your-project.git .

# Create `.env` file
cp .env-template .env
sed -i "s/SECRET_KEY='.*$/SECRET_KEY='$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')'/" .env
sed -i "s/FAST_API_ACCESS_SECRET_TOKEN='.*$/FAST_API_ACCESS_SECRET_TOKEN='$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')'/" .env
sed -i "s/AWS_ACCESS_KEY_ID=/# AWS_ACCESS_KEY_ID=/" .env
sed -i "s/AWS_SECRET_ACCESS_KEY=/# AWS_SECRET_ACCESS_KEY=/" .env
sed -i "s/JUPYTER_BASE_URL=.*$/JUPYTER_BASE_URL='jupyter'/" .env

# Setup systemd
sudo cp prod/systemd/docker-compose-app.service /etc/systemd/system/docker-compose-app.service
sudo systemctl daemon-reload
sudo systemctl enable docker-compose-app

# Test the S3 mount (Optional)
# ############################

# Install AWS CLI
pip3 install awscli --upgrade

# List files in the bucket `doc-search-poc`
aws s3 ls s3://doc-search-poc
