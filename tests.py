import pluginframe
from os import mkdir, rmdir, path, remove
from string import ascii_letters
from random import choice
import unittest


class PluginFrameTestCase(unittest.TestCase):
    def setUp(self):
        self.plugin_dir = ''.join(choice(ascii_letters) for _ in range(12))
        self.plugin = ''

        mkdir(self.plugin_dir)
        with open(path.join(self.plugin_dir, self.plugin), 'w') as f:
            f.write('def work(): return 1;def setup(handler): handler.add(work)')

        self.manager = pluginframe.PluginManager(self.plugin_dir)
        self.handler = list()

    def dynamic_load(self):
        self.manager.load(self.handler)
        self.assertEqual(len(self.handler), 1)
        self.assertEqual(self.handler[0](), 1)

    def tearDown(self):
        remove(path.join(self.plugin_dir, self.plugin))
        rmdir(self.plugin_dir)

