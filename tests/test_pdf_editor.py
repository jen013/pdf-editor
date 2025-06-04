import pytest
from pdf_editor import *

@pytest.fixture
def basic_pr_str():
    return "1-4, 6, 10-12"

@pytest.fixture
def basic_pr_expected():
    return [1,2,3,4,6,10,11,12]

@pytest.fixture
def messy_format_pr_str():
    return "   1,4,5  , 8-10,, ,  "

@pytest.fixture
def messy_format_pr_expected():
    return [1,4,5,8,9,10]

@pytest.fixture
def non_int_pr_str():
    return "1, 5-6, a, 10"

@pytest.fixture
def extra_hyphens_pr_str():
    return "1-2-3"

@pytest.fixture
def missing_bound_pr_str():
    return "2, 4-, 14"

@pytest.fixture
def em_dash_pr_str():
    return "3, 6, 9—10"

@pytest.fixture
def other_delimiters_pr_str():
    return "1. 4; 5"


def test_str_to_page_range_basic(basic_pr_str, basic_pr_expected):
    assert str_to_pagerange(basic_pr_str) == basic_pr_expected

def test_str_to_page_range_messy_format(messy_format_pr_str, messy_format_pr_expected):
    assert str_to_pagerange(messy_format_pr_str) == messy_format_pr_expected

def test_str_to_page_range_non_int(non_int_pr_str):
    with pytest.raises(ValueError):
        str_to_pagerange(non_int_pr_str)

def test_str_to_page_range_extra_hyphens(extra_hyphens_pr_str):
    with pytest.raises(ValueError):
        str_to_pagerange(extra_hyphens_pr_str)

def test_str_to_page_range_missing_bound(missing_bound_pr_str):
    with pytest.raises(ValueError):
        str_to_pagerange(missing_bound_pr_str)

def test_str_to_page_range_em_dash(em_dash_pr_str):
    with pytest.raises(ValueError):
        str_to_pagerange(em_dash_pr_str)

def test_str_to_page_range_other_delimiters(other_delimiters_pr_str):
    with pytest.raises(ValueError):
        str_to_pagerange(other_delimiters_pr_str)