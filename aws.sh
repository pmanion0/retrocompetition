#!/bin/bash

AWS_SSH_KEY=~/.ssh/bigbuddha.pem
AWS_INSTANCE_KEY=~/.ssh/flamingbuddha.pem
GITHUB_KEY=~/.ssh/github_rsa
AWS_CREDENTIALS=~/.aws/credentials

ACTION=$1

if [[ -z "$ACTION" ]]; then
  echo "ERROR: Run by providing [launch|setup|connect]"
  echo "EXAMPLE: ./aws.sh launch"
  exit 1
fi

if [[ $ACTION == "launch" ]]; then

  echo "LAUNCHING..."
  #ansible-playbook -i ansible/inventory/hosts ansible/ansible-aws.yml --private-key=$AWS_SSH_KEY

elif [[ $ACTION == "setup" ]]; then

  echo "SETTING UP AWS INSTANCE..."
  #sftp -i $AWS_INSTANCE_KEY ubuntu@$1 << 'EOF'
  #  cd .ssh
  #  put $GITHUB_KEY
  #  put $GITHUB_KEY.pub
  #  put ansible/remote_files/config
  #  cd ..
  #  mkdir .aws
  #  cd .aws
  #  put $AWS_CREDENTIALS
  #
  #  # Mount the EBS data with stored X-ray images
  #  #sudo mkdir /user
  #  #sudo mount /dev/xvdf /user
  #  #cd /user
  #
  #  # Clone the X-ray project repository
  #  git clone git@github.com:theforager/retrocompetition.git
  #
  #  # Turn off stupid Anaconda presentation plugin
  #  jupyter-nbextension disable nbpresent --py --sys-prefix
  #  jupyter-serverextension disable nbpresent --py --sys-prefix
  #EOF

elif [[ $ACTION == "connect" ]]; then

  echo "CONNECTING TO AWS..."
  #ssh -i $AWS_INSTANCE_KEY -L 7777:127.0.0.1:8888 ubuntu@$1

fi
