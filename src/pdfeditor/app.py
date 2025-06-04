# Set indexing base, e.g., zero-based indexing, one-based indexing, etc...
OFFSET = 1
        

class App:
    def __init__(self, app_name="", init_page=None):
        self.app_name = app_name
        self.set_page(init_page)
        self.set_command_loop()

    def set_page(self, page):
        if page is None:
            page = Page()
        self.curr_page = page
    
    def set_command_loop(self):
        self.command_loop = Loop(convert=int)

        convert_fail_msg = "Please select a command by entering its corresponding number (e.g. \"1\")."
        self.command_loop.set_convert_fail_msgs(after=convert_fail_msg)

        wrong_range_msg = "Please enter a number from the list above."
        self.command_loop.set_wrong_range_msgs(after=wrong_range_msg)

    def run_menu(self):
        self.command_loop.set_expected_range(0+OFFSET, self.curr_page.get_nav_len()+OFFSET)
        self.command_loop.set_convert_fail_msgs(before=self.get_tui())
        self.command_loop.set_wrong_range_msgs(before=self.get_tui())

        print(self.get_tui())
        user_command = self.command_loop.run()

        self.execute_action(user_command)

    def get_tui(self):
        page = self.curr_page
        tui = f"\n{self.app_name} - {page.title}\n\n"

        if page.details is not None:
            tui += f"{page.details}\n\n"

        for i, action in enumerate(page.navigation):
            tui += f"\t[{i+OFFSET}] {action.label}\n"

        return tui

    def execute_action(self, command):
        return self.curr_page.navigation[command-OFFSET].execute()


class Page:
    """
    App page for organizing commands/actions.
    
    Attributes:
        nagivation: list of Action objects
    """
    def __init__(self, title="", details=None, navigation=[]):
        self.title = title
        self.details = details
        self.navigation = navigation
    
    def get_nav_len(self):
        return len(self.navigation)
    
    def get_commands(self):
        return [i+OFFSET for i in range(self.get_nav_len())]
    
    def append_to_nav(self, action):
        self.navigation.append(action)

    def clear_nav(self):
        self.navigation.clear()

    
class Action:
    def __init__(self, label="", func=lambda: None):
        self.label = label
        self.func = func

    def set_action(self, func):
        self.func = func

    def execute(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class Loop:
    def __init__(self, prompt=None, convert=lambda x: x,
                 expected_range=(None, None), expected_responses=None):
        self.convert = convert
        self.set_prompt(prompt)
        self.set_expected_range(*expected_range)
        self.set_expected_response(expected_responses)
        self.convert_fail_msg = InvalidMessage()
        self.wrong_range_msg = InvalidMessage()
        self.wrong_response_msg = InvalidMessage()

    def set_prompt(self, prompt):
        self.prompt = prompt

    def set_expected_range(self, lower, upper):
        self.expected_range = (lower, upper)

    def set_expected_response(self, expected_responses):
        self.expected_responses = expected_responses

    def set_convert_fail_msgs(self, before=None, after=None):
        if before:
            self.convert_fail_msg.before = before
        if after:
            self.convert_fail_msg.after = after

    def set_wrong_range_msgs(self, before=None, after=None):
        if before:
            self.wrong_range_msg.before = before
        if after:
            self.wrong_range_msg.after = after

    def set_wrong_response_msgs(self, before=None, after=None):
        if before:
            self.wrong_response_msg.before = before
        if after:
            self.wrong_response_msg.after = after
    
    def input(self):
        if self.prompt is not None:
            print(self.prompt)
        user_input = input("> ")
        print()
        return user_input

    def in_expected_range(self, user_input):
        return user_input >= self.expected_range[0] and user_input < self.expected_range[1]
        
    def in_expected_responses(self, user_input):
        return user_input in self.expected_responses

    def run(self):
        while True:
            user_input = self.input()
            user_input_str = user_input

            try:
                converted_input = self.convert(user_input)
            except ValueError:
                self.convert_fail_msg.print_msg(user_input_str)
                continue
            else:
                user_input = converted_input

            # Condition order allows input to pass if it's in either expected responses or range.
            if ((self.expected_responses is not None and self.in_expected_responses(user_input)) or 
                (self.expected_range != (None, None) and self.in_expected_range(user_input))):
                break

            if self.expected_range != (None, None) and not self.in_expected_range(user_input):
                self.wrong_range_msg.print_msg(user_input_str)
                continue

            # Note: Expected range error message takes priority over expected responses error message, 
            # i.e., the condition below will never be reached if expected range is set.
            if self.expected_responses is not None and not self.in_expected_responses(user_input):
                self.wrong_response_msg.print_msg(user_input_str)
                continue

            break

        return user_input


class InvalidMessage:
    def __init__(self, before=None, after=None):
        self.before = before
        self.after = after

    def get_main_msg(self, user_input):
        return f"\"{user_input}\" is an invalid input."

    def print_msg(self, user_input):
        if self.before is not None:
            print(self.before)

        print(self.get_main_msg(user_input))

        if self.after is not None:
            print(self.after)

        print()