#!/bin/bash
# --------------------------------------- #
#  This script helps control the launch,
#  setup, and connection to an AWS EC2
#  instance for the retro contest.
#
#  Make sure you have SSH keys for AWS
#  and GitHub in the locations below.
#
#  !!! YOU ALSO NEED TWO ENVIRONMENT VARS
#  TO BE SET FOR YOUR AWS CREDENTIALS !!
#     - $AWS_ACCESS_KEY_ID
#     - $AWS_SECRET_ACCESS_KEY
#
# --------------------------------------- #

AWS_KEY_NAME=flaming_buddha
GITHUB_KEY=~/.ssh/github_rsa
#AWS_CREDENTIALS=~/.aws/credentials # Needed for S3 access
AWS_SSH_KEY=~/.ssh/$AWS_KEY_NAME.pem

# --------------------------------------- #
#         RUN PARAMETER CHECKS            #
# --------------------------------------- #

ACTION=$1
EC2_IP_ADDRESS=$2

if [[ -z "$ACTION" ]]; then
  echo "ERROR: Run by providing [launch|setup|connect]"
  echo "EXAMPLE: ./aws.sh launch"
  exit 1
fi

if [[ $ACTION != "launch" && -z "$EC2_IP_ADDRESS" ]]; then
  echo "ERROR: Please provide EC2 IP after setup command"
  echo "EXAMPLE: ./aws.sh connect 12.32.46.83"
  exit 1
fi

if [[ -z "$AWS_ACCESS_KEY_ID" || -z "$AWS_SECRET_ACCESS_KEY" ]]; then
  echo "ERROR: You must set 2 environment variables for AWS credentials:"
  echo "  - \$AWS_ACCESS_KEY_ID"
  echo "  - \$AWS_SECRET_ACCESS_KEY"
fi

# --------------------------------------- #
#  RUN AWS LAUNCH / SETUP / CONNECT       #
# --------------------------------------- #

if [[ $ACTION == "launch" ]]; then

  echo "LAUNCHING..."
  ansible-playbook ansible/ansible-aws.yml \
    --private-key=$AWS_SSH_KEY \
    --extra-vars "ssh_key_name=$AWS_KEY_NAME"

elif [[ $ACTION == "setup" ]]; then

  if [[ -z "$EC2_IP_ADDRESS" ]]; then
    echo "ERROR: Please provide EC2 IP after setup command"
    exit 1
  fi

  echo "SETTING UP AWS INSTANCE..."
  sftp -i $AWS_SSH_KEY ubuntu@$EC2_IP_ADDRESS << EOF
    cd .ssh
    put $GITHUB_KEY
    put $GITHUB_KEY.pub
    put ansible/remote_files/config
    cd ..
      #mkdir .aws
      #cd .aws
      #put $AWS_CREDENTIALS
EOF

  ssh -i $AWS_SSH_KEY ubuntu@$EC2_IP_ADDRESS << EOF
    # Mount the EBS data with stored X-ray images
      #sudo mkdir /user
      #sudo mount /dev/xvdf /user
      #cd /user

    # Clone the Retro Competition repository
    git clone git@github.com:theforager/retrocompetition.git

    # Turn off stupid Anaconda presentation plugin
    jupyter-nbextension disable nbpresent --py --sys-prefix
    jupyter-serverextension disable nbpresent --py --sys-prefix
EOF

elif [[ $ACTION == "connect" ]]; then

  echo "CONNECTING TO AWS..."
  ssh -i $AWS_SSH_KEY -L 7777:127.0.0.1:8888 ubuntu@$EC2_IP_ADDRESS

fi
