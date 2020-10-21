from antipathy import Path
from compileall import compile_file
from unittest import TestCase, main
from tempfile import mkdtemp
from textwrap import dedent
import sys

import testily
from testily import MockFunction, Patch, import_script

TEMPDIR = Path(mkdtemp())
TEMPDIR.rmtree(ignore_errors=True)


class TestMockFunction(TestCase):
    #
    def test_basics(self):
        huh = MockFunction('print')
        self.assertTrue(huh() is None)
        huh.return_value = 'yup indeed'
        self.assertEqual(huh(), 'yup indeed')
        self.assertEqual(
                huh.called_kwds,
                [{}, {}],
                )
        self.assertEqual(
                huh.called_args,
                [(), ()],
                )
        huh('this', that='there')
        self.assertEqual(
                huh.called_args,
                [(), (), ('this',)],
                )
        self.assertEqual(
                huh.called_kwds,
                [{}, {}, {'that': 'there'}],
                )
        self.assertEqual(huh.called, 3)


class TestPatch(TestCase):
    #
    def test_basics(self):
        with Patch(testily, 'MockFunction') as p:
            self.assertFalse(MockFunction == testily.MockFunction)
            self.assertTrue(isinstance(testily.MockFunction, MockFunction))
            self.assertTrue(isinstance(p.MockFunction, MockFunction))
            self.assertTrue(p.MockFunction is testily.MockFunction)
            self.assertTrue(p.original_objs['MockFunction'] is MockFunction)
        self.assertTrue(MockFunction == testily.MockFunction)


class TestImportScript(TestCase):
    #
    def setUp(self):
        TEMPDIR.rmtree(ignore_errors=True)
        TEMPDIR.mkdir()
    #
    def test_error(self):
        self.assertRaises(TypeError, import_script, 'hello.py')
    #
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
    #
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


if __name__ == '__main__':
    try:
        main()
    finally:
        TEMPDIR.rmtree(ignore_errors=True)
