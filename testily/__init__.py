version = 0, 0, 2, 1

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
    with disk_name.open('rb') as fh:
        fh.seek(0)
        module = imp.load_source(module_name, str(file))
    sys.modules[module_name] = module
    return module
    

class MockFunction(object):
    #
    def __init__(self, name, return_value=None):
        self.name = name
        self.return_value = return_value
        self.called_args = []
        self.called_kwds = []
    #
    def __repr__(self):
        return "MockFunction_%s" % self.name
    #
    def __call__(self, *args, **kwds):
        self.called_args.append(args)
        self.called_kwds.append(kwds)
        return self.return_value
    #
    @property
    def called(self):
        return len(self.called_args)


class Patch(object):
    #
    def __init__(self, namespace, *names):
        self.namespace = namespace
        self.original_objs = {}
        try:
            for name in names:
                obj = namespace.__dict__.get(name, Null)
                patch = MockFunction(name)
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
