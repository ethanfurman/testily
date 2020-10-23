from antipathy import Path
from compileall import compile_file
from unittest import TestCase, main
from tempfile import mkdtemp
from textwrap import dedent
import sys

import testily
from testily import Ersatz, Patch, import_script

TEMPDIR = Path(mkdtemp())
TEMPDIR.rmtree(ignore_errors=True)


class TestErsatz(TestCase):
 
    def test_basics(self):
        huh = Ersatz('print')
        self.assertTrue(huh() is None)
        huh._return_ = 'yup indeed'
        self.assertEqual(huh(), 'yup indeed')
        self.assertEqual(
                huh._called_kwds_,
                [{}, {}],
                )
        self.assertEqual(
                huh._called_args_,
                [(), ()],
                )
        huh('this', that='there')
        self.assertEqual(
                huh._called_args_,
                [(), (), ('this',)],
                )
        self.assertEqual(
                huh._called_kwds_,
                [{}, {}, {'that': 'there'}],
                )
        self.assertEqual(huh._called_, 3)


class TestPatch(TestCase):
 
    def test_basics(self):
        with Patch(testily, 'Ersatz') as p:
            self.assertFalse(Ersatz == testily.Ersatz)
            self.assertTrue(isinstance(testily.Ersatz, Ersatz))
            self.assertTrue(isinstance(p.Ersatz, Ersatz))
            self.assertTrue(p.Ersatz is testily.Ersatz)
            self.assertTrue(p._original_objs_['Ersatz'] is Ersatz)
        self.assertTrue(Ersatz == testily.Ersatz)

    def test_init_failure(self):
        class UnBreakableType(type):
            @property
            def immovable(cls):
                pass
            def movable(cls):
                pass
        UnBreakable = UnBreakableType('UnBreakable', (object, ), {})
        original_movable = UnBreakable.movable
        original_immovable = UnBreakable.immovable
        #
        UnBreakable.movable = 'okay'
        self.assertEqual(UnBreakable.movable, 'okay')
        UnBreakable.movable = original_movable
        self.assertTrue(getattr(UnBreakable, 'immovable') is UnBreakable.immovable)
        #
        with self.assertRaises(AttributeError):
            UnBreakable.immovable = 'nope!'
        #
        with Patch(UnBreakable, 'movable') as p:
            self.assertTrue(isinstance(UnBreakable.movable, Ersatz))
        self.assertTrue(original_movable is UnBreakable.movable)
        #
        try:
            with Patch(UnBreakable, 'movable', 'immovable') as p:
                self.assertFalse('Patch succeeded')
        except AttributeError:
            self.assertTrue(original_movable is UnBreakable.movable)

    def test_metaclass_property(self):
        class UnBreakableType(type):
            @property
            def immovable(cls):
                pass
            def movable(cls):
                pass
        UnBreakable = UnBreakableType('UnBreakable', (object, ), {})
        original_movable = UnBreakable.movable
        original_immovable = UnBreakable.immovable
        #
        with Patch(UnBreakableType, 'immovable') as mp:
            with Patch(UnBreakable, 'immovable') as p:
                self.assertTrue(isinstance(UnBreakable.immovable, Ersatz))
            self.assertEqual(UnBreakable.__dict__.get('immovable', 'gone'), 'gone')
            self.assertTrue(isinstance(getattr(UnBreakable, 'immovable'), Ersatz))
        self.assertTrue(UnBreakable.immovable is original_immovable)

    def test_attr_patch(self):
        class Stuff(object):
            theirs = lambda s, x: x + 9
            def __init__(self):
                self.this = 'that'
                self.these = 9
        stuff = Stuff()
        # test unpatched
        self.assertEqual(stuff.this, 'that')
        self.assertEqual(stuff.these, 9)
        self.assertEqual(stuff.theirs(3), 12)
        # test patched
        with Patch(stuff, this='what?', these=1, theirs=lambda: 7) as p:
            # test instance attrs
            self.assertEqual(stuff.this, 'what?')
            self.assertEqual(p.this, 'what?')
            self.assertEqual(stuff.these, 1)
            self.assertEqual(p.these, 1)
            self.assertEqual(stuff.theirs(), 7)
            self.assertEqual(p.theirs(), 7)
        # test unpatched
        self.assertEqual(stuff.this, 'that')
        self.assertEqual(stuff.these, 9)
        self.assertEqual(stuff.theirs(4), 13)


class TestImportScript(TestCase):

    def setUp(self):
        TEMPDIR.rmtree(ignore_errors=True)
        TEMPDIR.mkdir()

    def test_error(self):
        self.assertRaises(TypeError, import_script, 'hello.py')

    def test_simple_import(self):
        script = TEMPDIR / 'hah'
        with script.open('w') as fh:
            fh.write(dedent("""\
                    def hello():
                        return 'hello'
                    """))
        huh = import_script(script)
        self.assertEqual(huh.__file__, script)
        import hah
        self.assertTrue(huh is hah)
        self.assertEqual(hah.hello(), 'hello')

    def test_shadowed_import(self):
        script = TEMPDIR / 'woa'
        with script.open('w') as fh:
            fh.write(dedent("""\
                    def hello():
                        return 'hello'
                    """))
        shadow_script = script + '.py'
        with shadow_script.open('w') as fh:
            fh.write(dedent("""\
                    def hello():
                        return 'goodbye'
                    """))
        compile_file(str(shadow_script))
        wah = import_script(script)
        self.assertEqual(wah.__file__, script)
        import woa
        self.assertTrue(wah is woa)
        self.assertEqual(woa.hello(), 'hello')

    def test_module_name(self):
        script = TEMPDIR / 'hah'
        with script.open('w') as fh:
            fh.write(dedent("""\
                    def hello():
                        return 'hello'
                    """))
        huh = import_script(script, 'yup')
        self.assertEqual(huh.__file__, script)
        import yup
        self.assertTrue(huh is yup)
        self.assertEqual(yup.hello(), 'hello')
        with self.assertRaises(ImportError):
            import hah

    def test_import_from_other_directory(self):
        subdir = TEMPDIR / 'hah'
        subdir.mkdir()
        tools = subdir / 'tools.py'
        with tools.open('w') as fh:
            fh.write(dedent("""\
                    def sigma(text):
                        return text + 'oid'
                    """))
        script = subdir / 'heh'
        with script.open('w') as fh:
            fh.write(dedent("""\
                    from tools import sigma
                    def hello():
                        return sigma('hello')
                    """))
        heh = import_script(script)
        self.assertEqual(heh.hello(), 'hellooid')

if __name__ == '__main__':
    try:
        main()
    finally:
        TEMPDIR.rmtree(ignore_errors=True)
