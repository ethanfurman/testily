import testily
from testily import MockFunction, Patch
from unittest import TestCase, main

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


main()
