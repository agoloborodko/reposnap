# src/reposnap/tests/test_path_utils.py

import pytest  # noqa
from reposnap.utils.path_utils import format_tree

def test_format_tree():
    tree = {
        'dir1': {
            'file1.py': 'file1.py'
        },
        'file2.py': 'file2.py'
    }
    formatted = ''.join(format_tree(tree))
    expected = 'dir1/\n    file1.py\nfile2.py\n'
    assert formatted == expected
