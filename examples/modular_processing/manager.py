from pluginframe import PluginManager


class Manager:
    def __init__(self):
        self.plugin_mgr = PluginManager('plugins')
        self.work = set()
        self.plugin_mgr.load(self.work)

    def process(self):
        for func in self.work:
            func()


if __name__ == '__main__':
    mgr = Manager()
    mgr.process()
