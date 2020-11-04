version = 0, 0, 2, 9

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

    def __init__(self, name=None):
        self._name_ = name
        self._called_args_ = []
        self._called_kwds_ = []
        self._return_ = None

    def __repr__(self):
        if self._name_ is None:
            return "Ersatz()"
        else:
            return "Ersatz(%r)" % (self._name_, )

    def __call__(self, *args, **kwds):
        self._called_args_.append(args)
        self._called_kwds_.append(kwds)
        return self._return_

    @property
    def _called_(self):
        return len(self._called_args_)


_patch_attrs = '_namespace_', '_original_objs_', '_original_attrs_'
class Patch(object):

    def __init__(self, namespace, *names, **attrs):
        self._namespace_ = namespace
        self._original_objs_ = {}
        self._original_attrs_ = {}
        try:
            for name in names:
                obj = namespace.__dict__.get(name, Null)
                if obj is Null:
                    # verify that it is somewhere in the mro()
                    if not hasattr(namespace, name):
                        raise Exception('%s: %r not found' % (namespace, name))
                patch = Ersatz(name)
                setattr(self, name, patch)
                setattr(namespace, name, patch)
                self._original_objs_[name] = obj
            for name, new_obj in attrs.items():
                orig_obj = namespace.__dict__.get(name, Null)
                setattr(self, name, new_obj)
                setattr(namespace, name, new_obj)
                self._original_attrs_[name] = orig_obj
        except Exception:
            for name, obj in (
                    list(self._original_objs_.items()) + list(self._original_attrs_.items())
                ):
                if obj is not Null:
                    setattr(namespace, name, obj)
                else:
                    delattr(namespace, name)
            raise

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        for name, obj in (
                list(self._original_objs_.items()) + list(self._original_attrs_.items())
            ):
            if obj is not Null:
                setattr(self._namespace_, name, obj)
            else:
                delattr(self._namespace_, name)

    def __setattr__(self, name, value):
        if name in _patch_attrs:
            pass
        elif name in self._original_objs_:
            self._original_objs_[name] = value
            return
        elif name in self._original_attrs_:
            self._original_attrs_[name] = value
            return
        object.__setattr__(self, name, value)


Null = Sentinel('Null', boolean=False)
