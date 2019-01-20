import logging
import os

class _PluginFolder:
    ''' Dynamic object carrying for objects to hold extensions '''

    def __init__(self, folder, exclusions=None):
        self.folder = folder
        self.modules = set()
        self._exclusions = exclusions or []

    def _find_files(self):
        for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), self.folder)):
            for x in files:
                if not x.startswith('_') and x.endswith('.py') and x not in self._exclusions \
                        and not x.split('.', -1)[0] in self._exclusions:
                    yield x.split('.')[0]

            if not '__init__.py' in files:
                with open(os.path.join(root, '__init__.py'), 'w') as f:
                    f.write('pass')
            break

    def reload(self):
        loaded = [x.__name__ for x in self.modules]
        for f in self._find_files():
            capture = False
            if f in loaded:
                mod = [x for x in self.modules if x.__name__ == f][0]
            else:
                capture = True
                mod = __import__(self.folder + '.' + f).__dict__[f]

            if capture:
                self.modules.add(mod)

    def load(self):
        for mod in self._find_files():
            try:
                _mod = __import__(self.folder + '.' + mod).__dict__[mod]
                self.modules.add(_mod)
                yield _mod

            except Exception as e:
                logging.exception(
                    str(mod) + '{} Has failed to load due to [{}' + e.__class__.__name__ + '] Being raised.')
                continue


class PluginManager:
    ''' manages + plugins/__init__ functionality'''
    _Scanner = _PluginFolder

    def __init__(self, folder, excluded_files=None, setup_hook='setup', module_requirements=tuple()):
        self._exec_setup = setup_hook
        self._plugin_mgr = self._Scanner(folder, excluded_files or [])
        self._requirements = [self._exec_setup]
        self._requirements.extend(module_requirements)

    @property
    def plugins(self):
      return self._plugin_mgr.modules

    def load(self, loader):
        for module in self._plugin_mgr.load():
            try:
                getattr(module, self._exec_setup)(loader)
            except Exception as e:
                logging.exception('Hook failed to load due to {}'.format(e.__class__.__name__))

    def add(self, *modules):
        for x in modules:
            if all(hasattr(x, essential) for essential in self._requirements):
                self._plugin_mgr.modules.add(x)

    def rm(self, *modules):
        for x in modules:
            module = self.get(x)
            if module:
                self._plugin_mgr.modules.discard(module)

    def get(self, plugin):
        if isinstance(plugin, str):
            for x in self._plugins:
                if x.__class__.__name__ == plugin:
                    return x
                elif x.module.__name__ == plugin:
                    return x.module

        elif isinstance(plugin, type(os)):
            return [x for x in self._plugins if x.module]

    def reload(self, loader):
        self._plugin_mgr.reload()
        self._plugins = set()

        for module in self._plugin_mgr.modules:
            try:
                getattr(module, self._exec_setup)(loader)
            except Exception as e:
                logging.exception('Hook failed to load due to {}'.format(e.__class__.__name__))


slots = ['PluginManager']
