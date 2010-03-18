
enemy = {}

enemy['base'] = None

enemy['ball'] = {'size': 1, 'lives': 2, 'speed': 6.0,
                 'sprite_file': 'enemy_2.png',
                 'reward': 1}

enemy['hard_ball'] = {'size': 1, 'lives': 10, 'speed': 1.0,
                      'sprite_file': 'boss_ruby.png',
                      'reward': 5, 'rotate': False}

enemy['bad_cannon'] = {'size': 1, 'lives': 20, 'speed': 1.0,
                      'sprite_file': 'Tower.png',
                      'reward': 15, 'rotate': False}
