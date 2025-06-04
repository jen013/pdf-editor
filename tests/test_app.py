import pytest
from app import App, Page, Action, OFFSET

@pytest.fixture
def num_args():
    def _num_args(*args):
        if len(args) == 0:
            return "no args"
        elif len(args) == 1:
            return f"one args: {args}"
        else:
            return f"many args: {args}"
    return _num_args

@pytest.fixture
def dict_to_pairs():
    def _dict_to_pairs(**kwargs):
        pairs = []
        for k, v in kwargs.items():
            pairs.append((k, v))
        return pairs
    return _dict_to_pairs

@pytest.fixture
def sum_args():
    def _sum_args(*args):
        sum = 0
        for arg in args:
            sum += arg
        return sum
    return _sum_args

def custom_func(num):
    def _custom_func():
        return num
    return _custom_func

@pytest.fixture
def num_args_label():
    return "Number of Args"

@pytest.fixture
def dict_pair_label():
    return "Dict to Pair"

@pytest.fixture
def one_arg():
    return "A"

@pytest.fixture
def many_args():
    return [1, 2, 3, 4]

@pytest.fixture 
def kwargs():
    return {"a": 1, "b": 2, "c":3}

@pytest.fixture
def empty_action():
    return Action("")

@pytest.fixture
def num_args_action(num_args_label, num_args):
    return Action(num_args_label, num_args)

@pytest.fixture
def dict_pair_action(dict_pair_label, dict_to_pairs):
    return Action(dict_pair_label, dict_to_pairs)

@pytest.fixture
def custom_actions():
    return [Action(f"Action {i+OFFSET}", custom_func(i+OFFSET)) for i in range(25)]

@pytest.fixture
def empty_page():
    yield Page("")

@pytest.fixture
def filled_page(custom_actions):
    navigation = custom_actions
    filled_page = Page("Page Title", "Page Details", navigation)
    return filled_page

@pytest.fixture
def empty_app(empty_page):
    return App("", empty_page)

@pytest.fixture
def filled_app(filled_page):
    return App("App Name", filled_page)

class TestApp:
    def test_set_page(self, empty_app, empty_page, filled_page):
        assert empty_app.curr_page == empty_page
        empty_app.set_page(filled_page)
        assert empty_app.curr_page == filled_page

    def test_execute_action(self, filled_app, custom_actions):
        for i, action in enumerate(custom_actions):
            assert filled_app.execute_action(i+OFFSET) == action.execute()


class TestPage:
    def test_get_nav_len(self, empty_page, filled_page):
        assert empty_page.get_nav_len() == 0
        assert empty_page.get_nav_len() == len(empty_page.navigation)
        assert filled_page.get_nav_len() == 25
        assert filled_page.get_nav_len() == len(filled_page.navigation)

    def test_get_commands(self, empty_page, filled_page):
        assert empty_page.get_commands() == []

        list_1_to_25 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,
                        15,16,17,18,19,20,21,22,23,24,25]
        assert filled_page.get_commands() == list_1_to_25

    def test_append_to_nav(self, empty_page):
        og_empty_page = empty_page
        for i in range(25):
            assert empty_page.get_nav_len() == i
            empty_page.append_to_nav(i)

        assert empty_page.get_nav_len() == 25
        assert all(empty_page.navigation[i] == i for i in range(25))
        empty_page = og_empty_page

    def test_clear_nav(self, filled_page):
        assert filled_page.get_nav_len() == 25
        filled_page.clear_nav()
        assert filled_page.get_nav_len() == 0
        assert filled_page.navigation == []


class TestAction:
    def test_execute(self, custom_actions):
        for i, action in enumerate(custom_actions):
            assert action.execute() == i + OFFSET

    def test_execute_empty(self, empty_action):
        assert empty_action.execute() == None

    def test_execute_no_args(self, num_args_action, num_args):
        assert num_args_action.execute() == num_args()

    def test_execute_one_arg(self, num_args_action, num_args, one_arg):
        assert num_args_action.execute(one_arg) == num_args(one_arg)

    def test_execute_many_args(self, num_args_action, num_args, many_args):
        assert num_args_action.execute(*many_args) == num_args(*many_args)

    def test_execute_kwargs(self, dict_pair_action, dict_to_pairs, kwargs):
        assert dict_pair_action.execute(**kwargs) == dict_to_pairs(**kwargs)

    def test_label(self, empty_action, num_args_action, num_args_label, dict_pair_action, dict_pair_label):
        assert empty_action.label == ""
        assert num_args_action.label == num_args_label
        assert dict_pair_action.label == dict_pair_label

    def test_set_action(self, num_args_action, sum_args, many_args):
        num_args_action.set_action(sum_args)
        assert num_args_action.execute(*many_args) == sum_args(*many_args)