import pytest
from pdf import PdfManager

@pytest.fixture
def alphabet_4():
    return ['a', 'b', 'c', 'd']

@pytest.fixture
def alphabet_4_reverse():
    return ['d', 'c', 'b', 'a']


def test_reordered_reverse(alphabet_4, alphabet_4_reverse):
    reverse_order = range(len(alphabet_4))[::-1]

    manager = PdfManager()
    manager.pages = alphabet_4
    manager.pages_original = alphabet_4

    assert manager.rearrange_pages(reverse_order) == alphabet_4_reverse
    assert manager.pages == alphabet_4_reverse
    assert manager.pages_original == alphabet_4_reverse