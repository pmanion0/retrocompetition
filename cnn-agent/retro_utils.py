def parse_local(args):
    """ Return whether the job should run in local or remote mode """
    if len(args) > 1 and (args[1] == "local" or args[1] == "aws"):
        return True
    else:
        return False

def parse_aws(args):
    """ Return whether the job is running on AWS (to skip rendering) """
    if len(args) > 1 and args[1] == "aws":
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

def clone_checkpoint_nn(old_network):
    """ Create a clone of the given network with the same parameters """
    new_network = type(old_network)()
    new_network.load_state_dict(old_network.state_dict())
    new_network.eval()
    return new_network
