version = 0, 0, 1


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


