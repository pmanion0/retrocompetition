

def parse_local(args):
    """ Return whether the job should run in local or remote mode """
    if len(args) > 1 and args[1] == "local":
        return True
    else:
        return False

def get_environment(is_local):
    """ Return a local or remote environment as requested """
    if is_local:
        from retro_contest.local import make
        env = make(game='SonicTheHedgehog-Genesis', state='LabyrinthZone.Act1')
    else:
        import gym_remote.exceptions as gre
        import gym_remote.client as grc
        env = grc.RemoteEnv('tmp/sock')
    return env

def get_action(in_tensor):
    ''' TODO: '''
    all = [0]*12
    all[7] = 1
    return all
