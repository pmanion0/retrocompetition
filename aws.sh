#!/bin/bash
# --------------------------------------- #
#  This script helps control the launch,
#  setup, and connection to an AWS EC2
#  instance for the retro contest.
#
#  Make sure you have SSH keys for AWS
#  and GitHub in the locations below.
#
#  !!! YOU ALSO NEED THREE ENVIRONMENT VARS
#  TO BE SET FOR YOUR AWS CREDENTIALS !!
#     - $AWS_ACCESS_KEY_ID
#     - $AWS_SECRET_ACCESS_KEY
#     - $AWS_KEY_NAME
#
# --------------------------------------- #

GITHUB_KEY=~/.ssh/github_rsa
#AWS_CREDENTIALS=~/.aws/credentials # Needed for S3 access

# --------------------------------------- #
#         RUN PARAMETER CHECKS            #
# --------------------------------------- #

ACTION=$1
OPTION=$2

if [[ -z "$ACTION" ]]; then
  echo "ERROR: Run by providing [launch|setup|connect]"
  echo "EXAMPLE: ./aws.sh launch"
  exit 1
fi

if [[ $ACTION == "launch" && -z "$OPTION" ]]; then
  echo "NOTE: No instance type provided - assuming p2.xlarge"
  echo "EXAMPLE: ./aws.sh launch p3.8xlarge"
  OPTION="p2.xlarge"
fi

if [[ $ACTION != "launch" && -z "$OPTION" ]]; then
  echo "ERROR: Please provide EC2 IP after setup command"
  echo "EXAMPLE: ./aws.sh connect 12.32.46.83"
  exit 1
fi

if [[ -z "$AWS_ACCESS_KEY_ID" || -z "$AWS_SECRET_ACCESS_KEY" || -z "$AWS_KEY_NAME" ]]; then
  echo "ERROR: You must set 3 environment variables for AWS credentials:"
  echo "  - \$AWS_ACCESS_KEY_ID: secret access ID from EC2 console"
  echo "  - \$AWS_SECRET_ACCESS_KEY: secret key password from EC2 console"
  echo "  - \$AWS_KEY_NAME: name of SSH key without .pem (located at ~/.ssh/$AWS_KEY_NAME.pem)"
  exit 1
fi

# --------------------------------------- #
#  CREATE GITHUB RSA KEY CHECK TO UPLOAD  #
# --------------------------------------- #

# If checks whether known_hosts file already exists (this file is personalzied and NOT in the repo!)
if [[ ! -f ansible/remote_files/known_hosts ]]; then
  echo "NOTE: ansible/remote_files/known_hosts not found! This is needed for AWS automation."
  echo "  Would you like to create it?"
  select yn in "Yes" "No"; do
    case $yn in
        Yes )
            echo "Adding Github.com to ansible/remote_files/known_hosts"
            ssh-keyscan github.com >> ansible/remote_files/known_hosts
            break;;
        No )
            break;;
    esac
  done
fi


# --------------------------------------- #
#  RUN AWS LAUNCH / SETUP / CONNECT       #
# --------------------------------------- #

AWS_SSH_KEY=~/.ssh/$AWS_KEY_NAME.pem

if [[ $ACTION == "launch" ]]; then
  INSTANCE_TYPE=$OPTION

  echo "LAUNCHING..."
  ansible-playbook ansible/ansible-aws.yml \
    --private-key=$AWS_SSH_KEY \
    --extra-vars "ssh_key_name=$AWS_KEY_NAME instance_type=$INSTANCE_TYPE"

elif [[ $ACTION == "setup" ]]; then
  EC2_IP_ADDRESS=$OPTION

  if [[ -z "$EC2_IP_ADDRESS" ]]; then
    echo "ERROR: Please provide EC2 IP after setup command"
    exit 1
  fi

  echo "SETTING UP AWS INSTANCE..."
  sftp -i $AWS_SSH_KEY ubuntu@$EC2_IP_ADDRESS << EOF
    cd .ssh
    put $GITHUB_KEY
    put $GITHUB_KEY.pub
    put ansible/remote_files/known_hosts
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
      # This is broken with the latest AMI
      #jupyter-nbextension disable nbpresent --py --sys-prefix
      #jupyter-serverextension disable nbpresent --py --sys-prefix
EOF

elif [[ $ACTION == "connect" ]]; then
  EC2_IP_ADDRESS=$OPTION

  echo "CONNECTING TO AWS..."
  ssh -i $AWS_SSH_KEY -L 7777:127.0.0.1:8888 ubuntu@$EC2_IP_ADDRESS

fi
