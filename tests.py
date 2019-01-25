from pluginframe import HookManager
from os import mkdir, rmdir, path, remove
import unittest


def write_plugin(fp, data=None):
    with open(fp, 'w') as f:
        f.write(data or 'def work(): return 1\ndef setup(handler): \n\thandler.append(work)\n')


class PluginFrameTestCase(unittest.TestCase):
    def setUp(self):
        self.plugin_dir = '_tests_plugin'
        self.plugins = (    # Some raw code to generate plugins
            ('plugin2.py', None), ('plugin1.py', None), ('__init__.py', 'pass'),
            ('slots_plugin.py', 'def work(): return 1\ndef setup(handler):\n\thandler.append(work)'
                                '\n__slots__=[\'setup\']')
        )

        mkdir(self.plugin_dir)
        for name, data in self.plugins:
            write_plugin(path.join(self.plugin_dir, name), data=data)

        self.manager = HookManager(self.plugin_dir, excluded_files=[self.plugins[0][0], self.plugins[-1][0]])
        self.handler = list()

    def test_load(self):
        self.manager.load(self.handler)
        self.assertEqual(len(self.handler), 1)
        self.assertEqual(self.handler[0](), 1)

    def test_reload(self):
        setattr(self.manager, '_exclusions', set(['slots_plugin.py']))  # Override exclusions
        self.manager.reload(self.handler)
        self.assertGreater(len(self.manager.modules), 0)

    def test_slots(self):
        self.handler = list() # reset this
        setattr(self.manager, '_exclusions', set(x for x, _ in self.plugins[:-1]))
        self.manager.reload(self.handler)
        self.assertEqual(len(self.handler), 1)
        self.assertEqual(self.handler[0](), 1)

    def tearDown(self):
        for plug, _ in self.plugins:
            remove(path.join(self.plugin_dir, plug))
        rmdir(self.plugin_dir)

