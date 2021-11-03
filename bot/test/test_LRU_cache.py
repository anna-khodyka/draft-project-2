"""
Testing LRU_cache module
"""
#pylint: disable=W0614
#pylint: disable=W0603
#pylint: disable=C0103
#pylint: disable=W0401
#pylint: disable=C0103

from LRU_cache import *
TEST_LRU_COUNTER = 0

@LRU_cache(max_len=5)
def up_char(a, b, c='d', d='e'):
    """
    Test function for testing LRU_cache
    :param a:
    :param b:
    :param c:
    :param d:
    :return:
    """
    global TEST_LRU_COUNTER
    TEST_LRU_COUNTER +=1
    return (a+b+c+d).upper()

@LRU_cache_invalidate('up_char')
def foo_bar():
    """
    Prepare for test LRU_cache_invalidation
    :return:
    """

def test_lru():
    """
    Test LRU_cache
    :return:
    """
    flush_cache()
    res1 = up_char('a','b','c','d')
    res2 = up_char('a', 'b', c='c', d='d')
    res3 = up_char('a', 'b', d='d', c='c')
    assert res1 == res2
    assert res1 == res3
    assert TEST_LRU_COUNTER == 1

    flush_cache()
    res1 = up_char('a','b','c','d')
    assert TEST_LRU_COUNTER == 2

    foo_bar()
    res1 = up_char('a', 'b', 'c', 'd')
    assert TEST_LRU_COUNTER == 3
