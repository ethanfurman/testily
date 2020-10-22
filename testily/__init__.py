version = 0, 0, 2, 4

from antipathy import Path
from scription import Sentinel
import imp
import os
import sys
import tempfile

def import_script(file, module_name=None):
    """
    import a python script (.py extension not allowed)
    """
    disk_name = file = Path(file)
    if disk_name.endswith('.py'):
        raise TypeError('cannot load .py files (use `import` instead')
    # docs suggest the following is necessary, but doesn't appear to be (at least,
    # not under cPython)
    shadow_file = disk_name + '.py'
    if shadow_file.exists():
        # do some fancy footwork and copy file to a tempfile so we
        # can import it, otherwise the .py version will get imported instead
        while shadow_file.exists():
            with tempfile.NamedTemporaryFile(delete=False) as df:
                disk_name = Path(df.name)
            shadow_file = disk_name + '.py'
        file.copy(disk_name)
    module_name = module_name or file.filename
    sys.path.insert(0, disk_name.dirname)
    with disk_name.open('rb') as fh:
        fh.seek(0)
        module = imp.load_source(module_name, str(file))
    sys.modules[module_name] = module
    sys.path.pop(0)
    return module
    

class Ersatz(object):
    #
    __slots__ = '_called_args_', '_called_kwds_', '__dict__', '_return_',
    #
    def __init__(self, name=None):
        self._name_ = name
        self._called_args_ = []
        self._called_kwds_ = []
        self._return_ = None
    #
    def __repr__(self):
        if self._name_ is None:
            return "Ersatz()"
        else:
            return "Ersatz(%r)" % (self.name, )
    #
    def __call__(self, *args, **kwds):
        self._called_args_.append(args)
        self._called_kwds_.append(kwds)
        return self._return_
    #
    def __getattr__(self, name):
        if name[:2] == name[-2:] == '__':
            return super(Ersatz, self).__getattribute__(name)
        return self.__class__(name)
    #
    @property
    def _called_(self):
        return len(self._called_args_)



class Patch(object):
    #
    def __init__(self, namespace, *names):
        self.namespace = namespace
        self.original_objs = {}
        try:
            for name in names:
                obj = namespace.__dict__.get(name, Null)
                patch = Ersatz(name)
                setattr(self, name, patch)
                setattr(namespace, name, patch)
                self.original_objs[name] = obj
        except Exception:
            for name, obj in self.original_objs.items():
                if obj is not Null:
                    setattr(namespace, name, obj)
                else:
                    delattr(namespace, name)
            raise
    #
    def __enter__(self):
        return self
    #
    def __exit__(self, *exc):
        for name, obj in self.original_objs.items():
            if obj is not Null:
                setattr(self.namespace, name, obj)
            else:
                delattr(self.namespace, name)

Null = Sentinel('Null', boolean=False)
