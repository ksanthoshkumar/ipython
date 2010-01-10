"""Tests for various magic functions.

Needs to be run by nose (to make ipython session available).
"""
from __future__ import absolute_import

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# stdlib
import os
import sys
import tempfile
import types
from cStringIO import StringIO

# third-party
import nose.tools as nt

# our own
from IPython.utils import genutils
from IPython.utils.platutils import find_cmd, get_long_path_name
from IPython.testing import decorators as dec
from IPython.testing import tools as tt

#-----------------------------------------------------------------------------
# Test functions begin
#-----------------------------------------------------------------------------
def test_rehashx():
    # clear up everything
    _ip = get_ipython()
    _ip.alias_manager.alias_table.clear()
    del _ip.db['syscmdlist']
    
    _ip.magic('rehashx')
    # Practically ALL ipython development systems will have more than 10 aliases

    yield (nt.assert_true, len(_ip.alias_manager.alias_table) > 10)
    for key, val in _ip.alias_manager.alias_table.items():
        # we must strip dots from alias names
        nt.assert_true('.' not in key)

    # rehashx must fill up syscmdlist
    scoms = _ip.db['syscmdlist']
    yield (nt.assert_true, len(scoms) > 10)


def doctest_hist_f():
    """Test %hist -f with temporary filename.

    In [9]: import tempfile

    In [10]: tfile = tempfile.mktemp('.py','tmp-ipython-')

    In [11]: %hist -n -f $tfile 3
    """


def doctest_hist_r():
    """Test %hist -r

    XXX - This test is not recording the output correctly.  Not sure why...

    In [20]: 'hist' in _ip.lsmagic()
    Out[20]: True

    In [6]: x=1

    In [7]: %hist -n -r 2
    x=1  # random
    hist -n -r 2  # random
    """


def test_shist():
    # Simple tests of ShadowHist class - test generator.
    import os, shutil, tempfile

    from IPython.utils import pickleshare
    from IPython.core.history import ShadowHist
    
    tfile = tempfile.mktemp('','tmp-ipython-')
    
    db = pickleshare.PickleShareDB(tfile)
    s = ShadowHist(db)
    s.add('hello')
    s.add('world')
    s.add('hello')
    s.add('hello')
    s.add('karhu')

    yield nt.assert_equals,s.all(),[(1, 'hello'), (2, 'world'), (3, 'karhu')]
    
    yield nt.assert_equal,s.get(2),'world'
    
    shutil.rmtree(tfile)

    
# XXX failing for now, until we get clearcmd out of quarantine.  But we should
# fix this and revert the skip to happen only if numpy is not around.
#@dec.skipif_not_numpy
@dec.skipknownfailure
def test_numpy_clear_array_undec():
    from IPython.extensions import clearcmd

    _ip.ex('import numpy as np')
    _ip.ex('a = np.empty(2)')
    yield (nt.assert_true, 'a' in _ip.user_ns)
    _ip.magic('clear array')
    yield (nt.assert_false, 'a' in _ip.user_ns)
    

# Multiple tests for clipboard pasting
@dec.parametric
def test_paste():
    _ip = get_ipython()
    def paste(txt, flags='-q'):
        """Paste input text, by default in quiet mode"""
        hooks.clipboard_get = lambda : txt
        _ip.magic('paste '+flags)

    # Inject fake clipboard hook but save original so we can restore it later
    hooks = _ip.hooks
    user_ns = _ip.user_ns
    original_clip = hooks.clipboard_get

    try:
        # This try/except with an emtpy except clause is here only because
        # try/yield/finally is invalid syntax in Python 2.4.  This will be
        # removed when we drop 2.4-compatibility, and the emtpy except below
        # will be changed to a finally.

        # Run tests with fake clipboard function
        user_ns.pop('x', None)
        paste('x=1')
        yield nt.assert_equal(user_ns['x'], 1)

        user_ns.pop('x', None)
        paste('>>> x=2')
        yield nt.assert_equal(user_ns['x'], 2)

        paste("""
        >>> x = [1,2,3]
        >>> y = []
        >>> for i in x:
        ...     y.append(i**2)
        ...
        """)
        yield nt.assert_equal(user_ns['x'], [1,2,3])
        yield nt.assert_equal(user_ns['y'], [1,4,9])

        # Now, test that paste -r works
        user_ns.pop('x', None)
        yield nt.assert_false('x' in user_ns)
        _ip.magic('paste -r')
        yield nt.assert_equal(user_ns['x'], [1,2,3])

        # Also test paste echoing, by temporarily faking the writer
        w = StringIO()
        writer = _ip.write
        _ip.write = w.write
        code = """
        a = 100
        b = 200"""
        try:
            paste(code,'')
            out = w.getvalue()
        finally:
            _ip.write = writer
        yield nt.assert_equal(user_ns['a'], 100)
        yield nt.assert_equal(user_ns['b'], 200)
        yield nt.assert_equal(out, code+"\n## -- End pasted text --\n")
        
    finally:
        # This should be in a finally clause, instead of the bare except above.
        # Restore original hook
        hooks.clipboard_get = original_clip


def test_time():
    _ip.magic('time None')


def doctest_time():
    """
    In [10]: %time None
    CPU times: user 0.00 s, sys: 0.00 s, total: 0.00 s
    Wall time: 0.00 s
    """

def test_doctest_mode():
    "Toggle doctest_mode twice, it should be a no-op and run without error"
    _ip.magic('doctest_mode')
    _ip.magic('doctest_mode')
    
