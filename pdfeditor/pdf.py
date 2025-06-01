import os, tempfile
from pypdf import PdfReader, PdfWriter

LEFT, BOTTOM, RIGHT, TOP = (0, 1, 2, 3)

class PdfManager:
    """
    Manager that combines and edits pdfs.

    Attributes:
        pages: A list of PageObject objects representing the pages of a pdf.
        reader: A PdfReader object used to add pdf pages and get information.
        writer: A PdfWriter object used to preview edits and write final pdf file.
    """

    def __init__(self, pdf_paths=[]):
        """
        Initializes PdfManager object and fills ``pages`` based on ``pdf_paths``.

        Args:
            pdf_paths: A path to a pdf file with pages to be added to ``pages``.
        """
        self.reader = None
        self.pages = []
        self.pages_original = []
        for path in pdf_paths:
            self.add_pdf(path)
        self.preview_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)


    def __enter__(self):
        return self
    

    def __exit__(self, *exc):
        self.close()
    

    def close(self):
        """Close streams and clear memory."""
        self.reset()
        self.preview_file.close()
        try:
            os.unlink(self.preview_file.name)
        except FileNotFoundError:
            pass
        finally:
            self.preview_file = None


    def reset(self):
        self.pages = []
        self.pages_original = []
        if self.reader is not None:
            self.reader.close()
            self.reader = None


    def get_pdf_num_pages(self, path):
        """Get number of pages of specified pdf path."""
        self.reader = PdfReader(path)
        return self.reader.get_num_pages()
            

    def add_pdf(self, path, indices=None):
        """
        Append specified pdf pages to ``pages`` and ``pages_original``.
        
        Args:
            path: A path to read pdf from.
            indices: A list of indices of pages to add. Defaults to None. 
                If None, all pages in pdf will be added.
        
        """
        self._append_pdf_pages(self.pages, path, indices)
        self._append_pdf_pages(self.pages_original, path, indices)
    

    def _append_pdf_pages(self, pages_list, path, indices=None):
        self.reader = PdfReader(path)
            
        if indices is None:
            reader_pages = self.reader.pages
        else:
            reader_pages = [self.reader.pages[i] for i in indices]

        for page in reader_pages:
            setattr(page, "path", path)
            pages_list.append(page)


    def pop_pages(self, indices=None):
        """Pop pages at specified indices."""
        if indices is None:
            return
        
        indices = set(indices)

        for i in range(len(self.pages)-1, -1, -1):
            if i in indices:
                self.pages_original.pop(i)
                self.pages.pop(i)


    def rearrange_pages(self, order):
        """Return ``pages`` after rearranging based on specified order."""
        assert len(self.pages) == len(order)
        assert len(set(order)) == len(order)

        self.pages = [self.pages[i] for i in order]
        self.pages_original = [self.pages_original[i] for i in order]
        return self.pages
    

    def reset_page(self, index):
        """Resets state of specified page to when it was initially added."""
        self.pages[index] = self.pages_original[index]
    

    def get_page_dims(self, index):
        """Return dimension of specified page in the format: (width, height)."""
        box = self.pages[index].mediabox
        return box.width, box.height


    def preview(self, indices=None):
        """
        Open pdf of specified pages in default pdf viewer program.

        Args:
            indices: A list of indices of pages to preview. Defaults to None. 
                If None, all pages will be previewed.
        
        Returns:
            The tempfile object used create the preview pdf.

        Warning:
            This method is currently only compatible with Windows OS.
        """
        if indices == None:
            indices = range(len(self.pages))

        with PdfWriter() as writer:
            for i in indices:
                writer.add_page(self.pages[i])
            
            writer.write(self.preview_file)
            os.startfile(self.preview_file.name)

        return self.preview_file


    def save_as(self, new_file):
        """
        Combine ``pages`` and save as new file.

        Args:
            new_file: A path to write new pdf file to.
        """
        with PdfWriter() as writer:
            for page in self.pages:
                writer.add_page(page)
            writer.write(new_file)
    

    def crop(self, index, margin):
        """
        Crop specified page by given margin.

        Args:
            index: The position of page in ``pages`` to crop from.
            margin: A tuple of values to crop each side by in the format:
                (left, bottom, right, top).

        Returns:
            A tuple that contains the additive inverse of each value in ``margin``.
            Passing the return value as ``margin`` argument will undo the initial crop.

        >>> pdf_manager.crop(0, pdf_manager.crop(0, (10, 10, 10, 10)))
        # Example: This will result in no cropping to occur.
        """
        assert len(margin) == 4

        box = self.pages[index].mediabox

        box.left += margin[LEFT]
        box.bottom += margin[BOTTOM]
        box.right -= margin[RIGHT]
        box.top -= margin[TOP]

        return -margin[0], -margin[1], -margin[2], -margin[3]


    def scale_to(self, index, target):
        """
        Scale specified page to given target.

        Args:
            index: The position of page in ``pages`` to crop from.
            target: A tuple of dimensions to stretch/shrink the page to in the format:
                (width, height). 
                
                If width is None, X axis will automatically scale to keep aspect ratio.
                If height is None, Y axis will automatically scale to keep aspect ratio.

        Returns:
            A tuple of page dimensions prior to scaling.
            Passing the return value as ``target`` argument will undo the initial scaling.
        
        Note: Scaling a page with a 0 dimension will raise a ZeroDivisionError.

        >>> pdf_manager.scale_to(0, pdf_manager.scale_to(0, (200, 200)))
        # Example: This will result in no scaling to occur.
        """
        assert len(target) == 2

        page = self.pages[index]
        init_dims = self.get_page_dims(index)

        if target[0] is None:
            factor = target[1] / init_dims[1]
            page.scale_by(factor)
        elif target[1] is None:
            factor = target[0] / init_dims[0]
            page.scale_by(factor)
        else:
            page.scale_to(*target)

        return init_dims
    