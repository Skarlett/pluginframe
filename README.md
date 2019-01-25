# pluginframe
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/25ee5ce995ec48a7b70269dd43189517)](https://app.codacy.com/app/Skarlett/pluginframe?utm_source=github.com&utm_medium=referral&utm_content=Skarlett/pluginframe&utm_campaign=Badge_Grade_Dashboard)
[![Build Status](https://travis-ci.org/Skarlett/pluginframe.svg?branch=master)](https://travis-ci.org/Skarlett/pluginframe)

This project aims to simplify loading modular dependencies in python. 

## Notes

This project loads a single directory, and assumes the python files in the project are both labeled with the python extension, and that they all have a "setup" hook (function). The idea of the setup hook is that there is one point of entry for a file to be loaded, and all files are expected to have it. That setup hook will take an object, and pass it to the hook, allowing the hook to configure precisely how it's determined functionality will be.

The general practice is that your plugin folder will hold most of the dependency code in your project. You can store the code in `__init__.py`, or make libraries in the plugin folder to call code from. Anything outside of the plugin folder should be considered part of the main application, and everything in the plugin folder should be considered features of the application. 

This project lays down the foundations needed for building a lot of high-level frameworks, which may include features based on if they're installed. Other ideas assciotated heavily with a project like this - is it allows you to begin building a repository of plugins which can be interchanged, and linked to a global repository similar to linux packages. This project does not aim to complete any of those ideas, only to settle a common foundation for people who need it in their own applications. By no means this is an "all-included" package.

## Usage
        .
    |-- manager.py
    `-- plugins
        |-- __init__.py
        |-- plugin_1.py
        `-- plugin_2.py
assuming the project structure looks like so, than we can easily call `PluginManager('plugins')` to dynamically load all the plugins. Each plugin needs a `setup` function/hook. The setup function is given a handler on runtime, which links back the application we called `PluginManager` from. The setup function looks like so...
    
    def setup(handler):
      ...

The handler can be **anything** - it is up to the plugin, and main application to decide how it will be handled. In our main application example - it works like this...

    from pluginframe import PluginManager
    class Manager:
        def __init__(self):
            self.plugin_mgr = PluginManager('plugins')
            self.work = set()
            self.plugin_mgr.load(self.work)

        def process(self):
            for func in self.work:
                func()
    
    mgr = Manager()
    mgr.process()

So in this example - we're actually expecting the handler to be a [set](https://docs.python.org/3/tutorial/datastructures.html#sets) object. With that in mind, we can write a plugin fairly easily by appending a function onto the set.
    
    def do_work():
      for x in range(3):
        print(x)

    def setup(handler):
      return handler.add(do_work)

Now after running the project - We can see the work was appended on and done.

## Super scary big projects
Some projects are absolutely jaw dropping at how many local files in the project are needed in dependencies. If you're attempting to implement a plugin system based on a large number of local dependencies - it is advised to follow this filesystem structure.

        |-- manager.py
        `-- plugins
            |-- __init__.py
            |-- local
            |   |-- lib1
            |   `-- lib2
            `-- plugin_example.py