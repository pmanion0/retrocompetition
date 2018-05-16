# retrocompetition
Contender for the OpenAI Retro Competition!

# Environment Scripts

`aws.sh`: this script helps manage the AWS environment including spinning up an instance, setting the instance up, and connecting

`docker.sh`: this script helps manage the Docker environment including building a new Docker for submission to OpenAI and pushing the Docker

# Abbreviated Setup Instructions

Here are simplified instructions to get up and runnning with the Gym environment

## Install Software

1. **Install Lua 5.1:** see [these instructions](https://github.com/openai/retro) for the Homebrew version or below if you want to skip Homebrew

2. **Install Docker:** simply install the app [for Mac](https://www.docker.com/docker-mac)

3. **Install Steam:** download the installer [here](https://store.steampowered.com/about/)

4. **Install PyTorch:** run with `pip install torch torchvision` (make sure you have torch 0.40 or some code may not run)

## Download Packages / Code

1. **Clone Our Repo:** `git pull git@github.com:theforager/retrocompetition.git`

2. **Install gym-retro:** `pip install gym-retro`

3. **Clone Retro Competition Repo:** `git clone --recursive https://github.com/openai/retro-contest.git`

4. **Install Retro Competition:** `pip install -e "retro-contest/support[docker,rest]"` (you can remove the brackets to also install the gym_remote package, which I think is preferable but isn't stated in instructions for some reason)

## Buy Sonic on Steam and Import

1. **Buy Sonic on Steam:** Sonic the Hedgehog 1 is $5 on Steam

2. **Import Sonic into Retro Gym:** run this code `python -m retro.import.sega_classics` (you can leave the SteamGuard field empty if you're already logged in on this computer)

## Setup Dockers

1. **Pull Remote Environment for Testing:** pull the Docker `docker pull openai/retro-env` and then tag it `docker tag openai/retro-env remote-env`

2. **Login to Remote Docker:** run `docker login retrocontestajvidhoekmrcpqzt.azurecr.io --username retrocontestajvidhoekmrcpqzt  --password 9zqhOlFc=EohEXrXfWi6mKbR9wMAXTB4` to connect to our remote docker environment using our team username and password

## Test It Out!

1. **Run It Locally:** with `python random-agent/random-agent-contest.py local`

2. **Test Building the Docker:** with `./docker.sh build random-agent v1`

3. **Test Run the Docker:** with `./docker.sh test random-agent v1`

## Set up AWS EC2 pipeline (Skip if Not Using AWS)

1. **Create AWS keys** 

Three keys are required to set up AWS as below

    `AWS_ACCESS_KEY_ID`: secret access ID from EC2 console

    `AWS_SECRET_ACCESS_KEY` : secret key password from EC2 console

    `AWS_KEY_NAME`: name of SSH key(EC2 key pairs) without .pem (located at `~/.ssh/**$AWS_KEY_NAME**.pem`)

**Note**: make sure your region is set as `US East (N. Virginia)`. The SSH key is specific for each region.


You need to create these keys first if you haven't have them yet:
    
   - [See instruction](https://docs.aws.amazon.com/general/latest/gr/managing-aws-access-keys.html) to create both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

   - [See instruction](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair) to create EC2 key pairs and obtain `**$AWS_KEY_NAME**.pem`. Then move it to `~/.ssh/**$AWS_KEY_NAME**.pem` and set the permission `chmod 400 ~/.ssh/**$AWS_KEY_NAME**.pem`


2. **Export Environment Variables:** add the following lines to your shell setup script of choice, e.g. `~/.bash_profile` on Mac, to define environment variables needed for AWS in the `aws.sh` script and Ansible:

`export AWS_ACCESS_KEY_ID=...`  

`export AWS_SECRET_ACCESS_KEY=...` 

`export AWS_KEY_NAME=...` 


3. **Install Python packages**

Install Ansible: [use instruction](http://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) by picking the corresponding operation system. If you use MAC, you can check [this instruction](http://docs.ansible.com/ansible/latest/installation_guide/inEC2_ip**tro_installation.html#latest-releases-via-pip) directly.

 Install Boto3 with `pip install boto3` or `sudo pip install boto3`


4. **Apply for access to Amazon GPU instances** if you need GPU for your project



5. **Test Run aws.sh**

We can run `aws.sh` to launch, setup and connect to EC2 instance:

- Launch an EC2 instance: type `./aws.sh launch **instance_type**` with the default instance type = `p2.xlarge` to launch an EC2 instance, and 

- Set up the EC2 instance: type `./aws.sh setup **EC2_ip**`  with your EC2 instance ip address. This will automatically install all the software/packages described above for the retro project. If you want to upload the game ROM to EC2 as well, simply copy them to the local directory 

- Connect to the EC2 instace: type `./aws.sh setup **EC2_ip**` with the EC2 ip address. 


**Note:** If you have Anaconda and/or more than one python versions installed in your computer, you may run into the error  message like "Boto3 doesn't exist" though you already installed it.  In this case, you could add one extra argument to `aws.sh` to specify ansible_python_interpreter when running ansible-playbook, e.g.

    `ansible-playbook ansible/ansible-aws.yml \
        --private-key=$AWS_SSH_KEY \
        --extra-vars "ssh_key_name=$AWS_KEY_NAME instance_type=$INSTANCE_TYPE ansible_python_interpreter=~/anaconda3/bin/python"`

## Skipping Homebrew
I don't like Homebrew because of all the permissions changes, so I worked around the dynamic library thing with this code:

```
sudo make macosx install
```

Then add this code to the bottom of the `src/Makefile`:

```
liblua.5.1.dylib: $(CORE_O) $(LIB_O)
        $(CC) -dynamiclib -o $@ $^ $(LIBS) -arch x86_64 -compatibility_version 5.1.5 -current_version 5.1.5 -install_name @rpath/$@
```

Remaining commands:

```
make -C src liblua.5.1.dylib
sudo mv src/liblua.5.1.dylib /usr/local/lib/
sudo mkdir -p /usr/local/opt/lua@5.1/lib/

sudo ln -s /usr/local/lib/liblua.5.1.dylib /usr/local/opt/lua@5.1/lib/liblua.5.1.dylib
```
