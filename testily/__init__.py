version = 0, 0, 2, 1

from antipathy import Path
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
        self.names = names
        self.original_objs = {}
        for f in names:
            orig = getattr(namespace, f)
            patch = MockFunction(f)
            self.original_objs[f] = orig
            setattr(self, f, patch)
            setattr(namespace, f, patch)
    #
    def __enter__(self):
        return self
    #
    def __exit__(self, *exc):
        for f in self.names:
            setattr(self.namespace, f, self.original_objs[f])


