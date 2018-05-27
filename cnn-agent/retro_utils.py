import io

def get_environment(environment):
    """ Return a local or remote environment as requested """
    if environment in ['aws','local']:
        from retro_contest.local import make
        env = make(game='SonicTheHedgehog-Genesis', state='LabyrinthZone.Act1')
    else:
        import gym_remote.exceptions as gre
        import gym_remote.client as grc
        env = grc.RemoteEnv('tmp/sock')
    return env

def clone_checkpoint_nn(old_network):
    """ Create a clone of the given network with the same parameters """
    new_network_buffer = io.BytesIO()
    old_network.save(new_network_buffer)
    new_network_buffer.seek(0)

    new_network = type(old_network)()
    new_network.load(new_network_buffer)
    new_network.eval()

    return new_network
