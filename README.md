# retrocompetition
Contender for the OpenAI Retro Competition!

# Environment Scripts

`aws.sh`: this script helps manage the AWS environment including spinning up an instance, setting the instance up, and connecting

`docker.sh`: this script helps manage the Docker environment including building a new Docker for submission to OpenAI and pushing the Docker

# Abbreviated Setup Instructions

Here are simplified instructions to get up and runnning with the Gym environment

1. **Buy Sonic on Steam:** I just bought Sonic the Hedgehog 1 on Steam for now - it's $5

2. **Install Lua:** see [these instructions](https://github.com/openai/retro) for the Homebrew version or below if you want to skip Homebrew

3. **pip Install gym-retro:** `pip3 install gym-retro`

4. **Run Install Command:** `python -m retro.import.sega_classics`

5. **SteamGuard:** I just left this blank, and it worked fine

6. **Create Random Agent Script:** use the script [a little down this page](https://contest.openai.com/details) above the rings, but I had to change the import from `from retro_contest.local import make` to `from retro import make`

7. **Run It:** with `python random-agent-contest.py`

