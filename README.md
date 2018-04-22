# retrocompetition
Contender for the OpenAI Retro Competition!

# Environment Scripts

`aws.sh`: this script helps manage the AWS environment including spinning up an instance, setting the instance up, and connecting

`docker.sh`: this script helps manage the Docker environment including building a new Docker for submission to OpenAI and pushing the Docker

# Abbreviated Setup Instructions

Here are simplified instructions to get up and runnning with the Gym environment

1. **Buy Sonic on Steam:** I just bought Sonic the Hedgehog 1 on Steam for now - it's $5

2. **Install Lua 5.1:** see [these instructions](https://github.com/openai/retro) for the Homebrew version or below if you want to skip Homebrew

3. **Install gym-retro:** `pip install gym-retro`

4. **Clone Retro Competition Repo:** `git clone --recursive https://github.com/openai/retro-contest.git`

5. **Install Retro Competition:** `pip install -e "retro-contest/support[docker,rest]"`

4. **Download Sega Games from Steam:** `python -m retro.import.sega_classics`

5. **SteamGuard:** I just left this blank, and it worked fine

6. **Create Random Agent Script:** use the script [a little down this page](https://contest.openai.com/details) above the rings, but I had to change the import from `from retro_contest.local import make` to `from retro import make`

7. **Run It:** with `python random-agent-contest.py`



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
