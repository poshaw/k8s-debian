#! /usr/bin/env python3
# coding: utf-8

import unittest
import myutils
from subprocess import PIPE

class TestMyutils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.string = "abcdefghijklmnopqrstuvwxyz0123456789"

    def tearDown(self):
        pass

    def test_bash_write_to_stdout(self):
        print("\nTesting writing to stdout:")
        twoLines = "  This line should print twice!"
        print(twoLines)
        myutils.bash(f'/usr/bin/echo "{twoLines}"')

    def test_bash_write_to_pipe(self):
        print("\nTesting writing to pipe:")
        output = myutils.bash(f'/usr/bin/echo "{self.string}"', stdout=PIPE)
        self.assertEqual(self.string, output)

    def test_bash_input_from_stdin(self):
        print("\nTesting input from pipe:")
        self.sb = bytes(self.string, 'utf-8')
        output = myutils.bash('/usr/bin/cat', input=self.sb, stdout=PIPE)
        self.assertEqual(self.string, output)


        with self.assertRaises(TypeError):
            myutils.bash('/usr/bin/cat', input=self.string)
        

if __name__ == '__main__':
    unittest.main()
