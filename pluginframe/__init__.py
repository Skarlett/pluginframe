import logging
import os
import sys
import importlib

logging = logging.getLogger(__name__)


def _load_module(relpath):
    ''' loads module via relative path. E.g folder.module '''
    name = relpath.split('.')[-1]
    return __import__(relpath).__dict__[name]


class DynamicImport:
    '''
    Loads modules based on os.walk
    '''

    def __init__(self, folder, exclusions=None):
        self._folder = folder
        self._modules = set()
        self._exclusions = exclusions or []

    def _find_modules(self):
        for root, _dirs, files in os.walk(os.path.join(os.path.dirname(__file__), self._folder)):
            for x in files:
                if not x.startswith('__') and x.endswith('.py') and x not in self._exclusions \
                        and not x.split('.', -1)[0] in self._exclusions:
                    yield x.split('.')[0]

            if not '__init__.py' in files:
                with open(os.path.join(root, '__init__.py'), 'w') as f:
                    f.write('pass')
                logging.info("created __init__.py in {}".format(root))
            break

    def reload(self):
        loaded = [x.__name__ for x in self._modules]
        for f in self._find_modules():
            capture = False
            if f in loaded:     # <- Already loaded
                mod = [x for x in self._modules if x.__name__ == f][0]
                importlib.reload(mod)
            else:               # <- Never seen before
                capture = True
                mod = _load_module(self._folder + '.' + f)

            if capture:
                self._modules.add(mod)

    def load(self):
        for mod in self._find_modules():
            try:
                self._modules.add(_load_module(self._folder + '.' + mod))
            except Exception as e:
                logging.exception('{} Has failed to load due to [{}] Being raised.'.format(mod, e.__class__.__name__))
                continue

    @property
    def modules(self):
        return self._modules

    @property
    def folder(self):
        return self._folder

    @property
    def exclusions(self):
        return self._exclusions


class HookManager(DynamicImport):
    '''
    Takes the modules loaded from `DynamicImport`,
    then aggregates them into a single "load" function
    
    '''
    def __init__(self, folder, excluded_files=None, setup_hook='setup'):
        super().__init__(folder, excluded_files)
        self._exec_setup = setup_hook

    def load(self, *args, **kwargs):
        
        super().load()
        for module in self._modules:
            try:
                getattr(module, self._exec_setup)(*args, **kwargs)
            except Exception as e:
                logging.exception('Hook failed to load due to {}'.format(e.__class__.__name__))

    def reload(self, *args, **kwargs):
        super().reload()
        for module in self._modules:
            try:
                getattr(module, self._exec_setup)(*args, **kwargs)
            except Exception as e:
                logging.exception('Hook failed to load due to {}'.format(e.__class__.__name__))


__slots__ = ['DynamicImport', 'HookManager']
__author__ = 'https://github.com/Skarlett'
__version__ = '0.1.1'
