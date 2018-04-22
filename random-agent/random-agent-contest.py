import sys

is_local = False

if len(sys.argv) > 1 and sys.argv[1] == "local":
    is_local = True

# Import 
def get_environment():
    if is_local:
        from retro_contest.local import make
        env = make(game='SonicTheHedgehog-Genesis', state='LabyrinthZone.Act1')
    else:
        import gym_remote.exceptions as gre
        import gym_remote.client as grc
        env = grc.RemoteEnv('tmp/sock')
    return env


def main():
    env = get_environment()
    obs = env.reset()
    while True:
        action = env.action_space.sample()
        action[7] = 1 # Always run right
        obs, rew, done, info = env.step(action)
        if is_local:
            env.render()
        if done:
            obs = env.reset()

if __name__ == '__main__':
    main()
