import tkinter as tk
from tkinter import filedialog
from app import App, Page, Action, Loop, OFFSET
from pdf import PdfManager
import os, sys

YES_RESPONSES = ["Y", "YES"]
NO_RESPONSES = ["N", "NO"]
PDF_FILETYPE = ("PDF Files", '*.pdf')

class PdfEditor:
    def __init__(self):
        self.manager = PdfManager()
        self.setup_app()

    
    def __enter__(self):
        return self
    

    def __exit__(self, *exc):
        self.manager.close()
        self.start_page = None
        self.edit_page = None
        self.app = None


    # TODO: Add cancel options to edit actions.
    def setup_app(self):
        exit_action = Action(
            label="Exit", 
            func=self.exit)
        
        add_action = Action(
            label="Add Files",
            func=self.add_files)

        crop_action = Action(
            label="Crop Page", 
            func=self.crop_page)
        
        scale_action = Action(
            label="Scale Page",
            func=self.scale_page)
        
        reset_action = Action(
            label="Reset Page",
            func=self.reset_page)
        
        remove_action = Action(
            label="Remove Pages",
            func=self.remove_pages)
        
        preview_action = Action(
            label="Preview PDF",
            func=self.preview_pdf)
        
        save_action = Action(
            label="Save As",
            func=self.save_as)

        start_nav = [
            add_action, 
            exit_action
            ]
        
        edit_nav = [
            add_action,
            crop_action,
            scale_action,
            reset_action,
            remove_action,
            preview_action,
            save_action,
            exit_action
            ]

        self.start_page = Page(
            title="Start Menu", 
            navigation=start_nav)

        self.edit_page = Page(
            title="Edit Menu",
            navigation=edit_nav)
        
        self.app = App(
            app_name="PDF Editor",
            init_page=self.start_page)
        

    def run(self):
        root = tk.Tk()
        root.after(100, lambda: root.withdraw())
        while True:
            self.update_menu()
            self.app.run_menu()
            self.prompt_continue()


    def update_menu(self):
        if self.manager.pages:
            self._update_edit_page_details()
            self.app.set_page(self.edit_page)
        else:
            self.app.set_page(self.start_page)


    def _update_edit_page_details(self):
        self.edit_page.details = f"Current Pages:{self.get_pages_as_list_tui()}"


    def exit(self):
        sys.exit()


    def add_files(self):
        """
        Let user select pdf files [and their pages] and add them to ``manager``.
        """
        custom_pages_prompt = "Choose which pages to add? (Y/N)"
        custom_pages = self.prompt_yes_no(custom_pages_prompt)
        pagerange_indices = None

        # TODO: Refocus back to terminal after adding files.
        paths = filedialog.askopenfilenames(filetypes=[PDF_FILETYPE])

        # Set up Loop object for custom page range
        if custom_pages:
            pagerange_loop = PageRangeLoop(convert=str_to_pagerange)

            failure_msg = "FAILED TO ADD PAGES."
            wrong_range_msg = "Selected page[s] are out of range."
            pagerange_loop.set_wrong_range_msgs(before=failure_msg, after=wrong_range_msg)
            pagerange_loop.set_convert_fail_msgs(before=failure_msg)

        for path in paths:
            if custom_pages:
                pdf_num_pages = self.manager.get_pdf_num_pages(path)
                pagerange_prompt = ("CUSTOMIZING PAGES TO ADD FROM\n"
                    f"'{path}'\n"
                    f"\tTotal pages: {pdf_num_pages}\n\n"

                    "To select all pages enter an empty input or \"all\".\n"
                    "Example: \"1-4, 6, 10-12\"\n")
                pagerange_loop.set_prompt(pagerange_prompt)
                pagerange_loop.set_expected_range(OFFSET, pdf_num_pages+OFFSET)

                pagerange = pagerange_loop.run()

                if pagerange is not None:
                    pagerange_indices = [page-OFFSET for page in pagerange]
                else:
                    pagerange_indices = None

            self.manager.add_pdf(path, pagerange_indices)
            print(f"SUCCESSFULLY ADDED PAGES FROM '{path_to_filename(path)}'.\n")
        if not paths:
            print("ADD FILES CANCELED.\n")


    def remove_pages(self):
        if not self.manager.pages:
            print("There are no pages to remove.")
            return

        pagerange_prompt = (f"Select pages to remove.\n Example: \"1-4, 6, 10-12\"")
        pagerange_loop = PageRangeLoop(prompt=pagerange_prompt, convert=str_to_pagerange)

        failure_msg = f"{self.edit_page.details}\n\nFAILED TO REMOVE PAGES."
        wrong_range_msg = "Selected page[s] are out of range."
        pagerange_loop.set_wrong_range_msgs(before=failure_msg, after=wrong_range_msg)
        pagerange_loop.set_convert_fail_msgs(before=failure_msg)

        pagerange_loop.set_prompt(pagerange_prompt)
        pagerange_loop.set_expected_range(OFFSET, len(self.manager.pages)+OFFSET)

        print(f"Current Pages:{self.get_pages_as_list_tui()}\n")
        pagerange = list(set(pagerange_loop.run()))

        if pagerange is not None:
            pagerange_indices = [page-OFFSET for page in pagerange]
        else:
            pagerange_indices = None


        confirmation_prompt = (f"REMOVING PAGES"
            f"{self.get_pages_as_list_tui(pagerange_indices)}\n\n"

            "Are you sure you want to remove these pages. (Y/N)\n"
            "\"Y\" to REMOVE.\n"
            "\"N\" to CANCEL.")
        confirm = self.prompt_yes_no(confirmation_prompt)

        if confirm:
            self.manager.pop_pages(pagerange_indices)
            print(f"PAGES {strip_ends(pagerange)} REMOVED.\n")
        else:
            print(f"REMOVE CANCELED.\n")


    def crop_page(self):
        if not self.manager.pages:
            print("There are no pages to crop.")
            return

        page_select_prompt = "Select a page to crop."
        page_num, page_index, page = self.prompt_page_select(page_select_prompt)
        
        crop_prompt = (f"CROPPING PAGE {page_num}.\n"
            "\tInformation: "
            f"'{path_to_filename(page.path)}' (pg.{page.page_number+OFFSET})\n"
            "\tCurrent Dimensions: "
            f"{self.manager.get_page_dims(page_index)}\n\n"

            "Enter the amount to crop from each side (\"left, bottom, right, top\").\n"
            "Example: \"50, 100, 50, 0\"")
        
        crop_loop = Loop(prompt=crop_prompt, convert=str_to_margin)
        crop_margin = crop_loop.run()
        self.manager.crop(page_index, crop_margin)

        # TODO: Include a check to see if page was cropped to appropriate size before printing.
        print(f"SUCCESSFULLY CROPPED PAGE {page_num}.\n"
            f"\tNew Dimensions: {self.manager.get_page_dims(page_index)}\n")


    def scale_page(self):
        if not self.manager.pages:
            print("There are no pages to scale.")
            return

        page_select_prompt = "Select a page to scale."
        page_num, page_index, page = self.prompt_page_select(page_select_prompt)
        
        scale_prompt = (f"SCALING PAGE {page_num}.\n"
            "\tInformation: "
            f"'{path_to_filename(page.path)}' (pg.{page.page_number+OFFSET})\n"
            "\tCurrent Dimensions: "
            f"{self.manager.get_page_dims(page_index)}\n\n"

            "Enter the dimension to scale page to (\"width, height\").\n"
            "Note: \"_\" automatically scales dimension to lock aspect ratio.\n"
            "Examples: \"100, 150\", \"_, 500\", \"123, _\"")
        
        scale_loop = Loop(prompt=scale_prompt, convert=str_to_dims)
        scale_dims = scale_loop.run()
        self.manager.scale_to(page_index, scale_dims)

        # TODO: Include a check to see if page was scaled to appropriate size before printing.
        print(f"SUCCESSFULLY SCALED PAGE {page_num}.\n"
            f"\tNew Dimensions: {self.manager.get_page_dims(page_index)}\n")


    def reset_page(self):
        if not self.manager.pages:
            print("There are no pages to reset.")
            return

        page_select_prompt = "Select a page to reset."
        page_num, page_index, page = self.prompt_page_select(page_select_prompt)

        confirmation_prompt = (f"RESETTING PAGE {page_num}.\n"
            "\tInformation: "
            f"'{path_to_filename(page.path)}' (pg.{page.page_number+OFFSET})\n\n"

            "Are you sure you want to reset all changes done to this page. (Y/N)\n"
            "\"Y\" to RESET.\n"
            "\"N\" to CANCEL.")
        confirm = self.prompt_yes_no(confirmation_prompt)

        if confirm:
            self.manager.reset_page(page_index)
            # TODO: Include a check to see if page was reset to appropriate size before printing.
            print(f"SUCCESSFULLY RESET PAGE {page_num}.\n"
                f"\tRestored Dimensions: {self.manager.get_page_dims(page_index)}\n")
        else:
            print(f"RESET CANCELED.\n")


    def preview_pdf(self):
        self.manager.preview()
        print(f"PREVIEW OPENED.\n")


    def save_as(self):
        path = filedialog.asksaveasfilename(filetypes=[PDF_FILETYPE], defaultextension='.pdf')
        if path:
            self.manager.save_as(path)

            open_ans = self.prompt_yes_no("Open created PDF? (Y/N)")
            if open_ans:
                os.startfile(path)
                print(f"{path_to_filename(path)} OPENED.\n")

            self.manager.reset()
        else:
            print("SAVE CANCELED.\n")


    def prompt_page_select(self, prompt):
        pages_cmd = f"Current Pages:\n{self.get_pages_as_cmd_tui()}\n"
        pages_loop = Loop(prompt=prompt, convert=int)
        pages_loop.set_expected_range(0+OFFSET, len(self.manager.pages)+OFFSET)

        convert_fail_msg = "Please select a page by entering its page number (e.g. \"1\")."
        pages_loop.set_convert_fail_msgs(before=pages_cmd, after=convert_fail_msg)

        wrong_range_msg = "Please enter a number from the list above."
        pages_loop.set_wrong_range_msgs(before=pages_cmd, after=wrong_range_msg)

        print(pages_cmd)
        page_num = pages_loop.run()
        page_index = page_num-OFFSET
        page = self.manager.pages[page_index]

        return page_num, page_index, page


    def prompt_yes_no(self, question):        
        custom_pages_loop = Loop(
            prompt=question, 
            expected_responses=YES_RESPONSES+NO_RESPONSES, 
            convert=str.upper)
        
        answer = custom_pages_loop.run()
        return answer in YES_RESPONSES
    

    def _prompt_preview(self, pages=None, custom_prompt=None):
        """
        Previews PDF pages if user answers yes to prompt.

        Args:
            pages: List of user inputted page numbers to preview. (1-based index)
                Defaults to None. If None, all pages will preview.
            custom_prompt: Message to prompt user with. Defaults to None.
                If None, default messages will be used based on ``pages`` value.
        """
        if custom_prompt:
            preview_prompt = custom_prompt
        elif custom_prompt is None and pages is None:
            preview_prompt = f"Preview PDF? (Y/N)"
        elif custom_prompt is None and pages:
            preview_prompt = f"Preview page[s] {strip_ends(pages)} first? (Y/N)"

        if pages is None:
            preview_indices = None
        else:
            preview_indices = [page-OFFSET for page in pages]

        preview_page = self.prompt_yes_no(preview_prompt)
        if not preview_page:
            return
        
        self.manager.preview(preview_indices)
        if pages is None:
            print(f"PREVIEW OPENED.\n\n")
        else:
            print(f"PREVIEW OF PAGES {strip_ends(pages)} OPENED.\n")


    def prompt_continue(self):
        input("Press <Enter> to continue\n> ")
        print()


    def get_pages_as_cmd_tui(self):
        tui = ""
        for i, page in enumerate(self.manager.pages):
            tui += (f"\t[{i+OFFSET}] '{path_to_filename(page.path)}'"
                    f" (pg.{page.page_number+OFFSET})\n")
        return tui
    

    def get_pages_as_list_tui(self, pagerange=None):
        tui = ""

        if pagerange is None:
             pagerange = range(len(self.manager.pages))

        for i in pagerange:
            page = self.manager.pages[i]
            tui += (f"\n{i+OFFSET}. ['{path_to_filename(page.path)}'"
                    f" (pg.{page.page_number+OFFSET})]")
            
        return tui
    

class PageRangeLoop(Loop):
    def in_expected_range(self, user_input):
        if user_input is None:
            return True

        if self.expected_range != (None, None):
            return all(x >= self.expected_range[0] and 
                       x < self.expected_range[1] 
                       for x in user_input)
        return True


def str_to_pagerange(string):
    """Convert string to list. If ``string`` argument is 'all' or '' return None."""
    if not string or string.lower() == "all":
        return None

    str_segments = string.replace(" ", "").split(",")
    pagerange = []

    for segment in str_segments:
        if not segment:
            continue

        bounds = [int(x) for x in segment.split("-")]
        if len(bounds) == 2:
            bounds = [*range(bounds[0], bounds[1]+1)]
        elif len(bounds) != 1:
            raise ValueError

        pagerange += bounds

    return pagerange


def str_to_margin(string):
    """Convert string to tuple with length of 4."""
    str_segments = string.replace(" ", "").split(",")
    margin = tuple(int(x) for x in str_segments)

    if len(margin) != 4:
        raise ValueError
    
    return margin


def str_to_dims(string):
    """Convert string to tuple with length of 2."""
    str_segments = string.replace(" ", "").split(",")
    dims = tuple(None if x == "_" else int(x) for x in str_segments)

    if len(dims) != 2:
        raise ValueError

    return dims
    

def path_to_filename(path):
    """Get filename from specified path."""
    return path.split("/")[-1]


def strip_ends(string):
    """Return specified string without the first and last characters."""
    return str(string)[1:-1]