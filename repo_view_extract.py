import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import string
import random
import re
from pathlib import Path
import threading
from typing import List, Dict, Optional, Any, Set

class JSONCodeViewer(tk.Tk):
    """Professional JSON Code Repository Viewer with bug fixes and improvements."""

    # Class constants
    RECORDS_PER_PAGE = 50
    DEFAULT_GEOMETRY = "1400x900"
    MIN_SIZE = (1000, 600)
    MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB limit
    MAX_FILENAME_LENGTH = 255  # Windows filename limit
    RANDOM_FILENAME_LENGTH = 12

    # Python keywords for syntax highlighting
    PYTHON_KEYWORDS = {
        'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
        'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
        'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
        'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
        'while', 'with', 'yield'
    }

    # Code type detection patterns
    CODE_TYPE_PATTERNS = {
        'GUI': {
            'imports': ['tkinter', 'PyQt', 'PySide', 'wx', 'kivy', 'pygame', 'gtk', 'ttk', 'customtkinter'],
            'path_keywords': ['gui', 'ui', 'interface', 'window', 'dialog', 'widget']
        },
        'AI/ML': {
            'imports': ['tensorflow', 'keras', 'torch', 'pytorch', 'sklearn', 'scikit-learn', 'xgboost',
                        'lightgbm', 'catboost', 'transformers', 'huggingface', 'openai', 'langchain'],
            'path_keywords': ['ai', 'ml', 'machine_learning', 'deep_learning', 'neural', 'model', 'training']
        },
        'Data Processing': {
            'imports': ['pandas', 'numpy', 'scipy', 'dask', 'polars', 'vaex', 'csv', 'json', 'xml',
                        'openpyxl', 'xlrd', 'pyarrow', 'parquet'],
            'path_keywords': ['data', 'etl', 'pipeline', 'processing', 'transform', 'clean']
        },
        'Image Processing': {
            'imports': ['PIL', 'pillow', 'cv2', 'opencv', 'skimage', 'imageio', 'mahotas',
                        'SimpleITK', 'scikit-image'],
            'path_keywords': ['image', 'img', 'vision', 'photo', 'picture', 'pixel']
        },
        'Web/API': {
            'imports': ['flask', 'django', 'fastapi', 'requests', 'aiohttp', 'httpx', 'bottle',
                        'tornado', 'starlette', 'uvicorn', 'gunicorn'],
            'path_keywords': ['web', 'api', 'server', 'http', 'rest', 'endpoint', 'route']
        },
        'Database': {
            'imports': ['sqlite3', 'sqlalchemy', 'pymongo', 'redis', 'psycopg2', 'mysql',
                        'pymysql', 'mongoengine', 'peewee', 'tortoise'],
            'path_keywords': ['database', 'db', 'sql', 'mongo', 'storage', 'repository']
        },
        'Algorithm': {
            'imports': ['collections', 'heapq', 'bisect', 'itertools', 'functools', 'operator'],
            'path_keywords': ['algorithm', 'algo', 'sort', 'search', 'graph', 'tree', 'dp', 'dynamic']
        },
        'Testing': {
            'imports': ['pytest', 'unittest', 'nose', 'mock', 'hypothesis', 'coverage', 'tox'],
            'path_keywords': ['test', 'spec', 'unittest', 'pytest', 'mock']
        },
        'Networking': {
            'imports': ['socket', 'asyncio', 'twisted', 'paramiko', 'fabric', 'netmiko', 'scapy'],
            'path_keywords': ['network', 'socket', 'tcp', 'udp', 'protocol', 'packet']
        },
        'Automation/Scripting': {
            'imports': ['subprocess', 'shutil', 'glob', 'pathlib', 'argparse', 'click', 'typer',
                        'schedule', 'watchdog', 'pyautogui', 'selenium'],
            'path_keywords': ['script', 'automation', 'bot', 'task', 'cron', 'job']
        }
    }

    # Size filter options (in bytes)
    SIZE_OPTIONS = [
        ('1 KB', 1024),
        ('5 KB', 5 * 1024),
        ('10 KB', 10 * 1024),
        ('20 KB', 20 * 1024),
        ('30 KB', 30 * 1024),
        ('50 KB', 10 * 1024),
        ('75 KB', 75* 1024),
        ('100 KB', 100 * 1024),
        ('200 KB', 200 * 1024),
        ('300 KB', 300 * 1024),
        ('500 KB', 500 * 1024),
        ('1 MB', 1024 * 1024),
        ('2 MB', 2 * 1024 * 1024),
        ('5 MB', 5 * 1024 * 1024),
        ('10 MB', 10 * 1024 * 1024),
        ('100 MB', 100 * 1024 * 1024)
    ]
    # Quality score weights
    QUALITY_WEIGHTS = {
        'has_docstring': 10,
        'has_type_hints': 8,
        'good_comment_ratio': 7,
        'reasonable_line_length': 5,
        'no_wildcard_imports': 5,
        'has_functions_or_classes': 5,
        'good_naming': 5,
        'no_bare_except': 4,
        'no_eval_exec': 4,
        'reasonable_complexity': 4,
        'has_exception_handling': 3,
        'no_magic_numbers': 2,
    }
    MAX_QUALITY_SCORE = sum(QUALITY_WEIGHTS.values())
    def __init__(self):
        super().__init__()

        self.title("JSON Code Repository Viewer")
        self.geometry(self.DEFAULT_GEOMETRY)
        self.minsize(*self.MIN_SIZE)

        # Data storage
        self.records: List[Dict[str, Any]] = []
        self.filtered_indices: List[int] = []
        self.current_record_index: int = 0
        self.current_page: int = 0
        self.total_pages: int = 1
        self.file_path: Optional[str] = None
        self.loading_cancelled: bool = False
        self.is_filtered: bool = False  # Track if filter is active
        self.current_search_term: str = ""  # Track current search term
        self.filter_types: Set[str] = set()
        self.filter_size_enabled: bool = False
        self.filter_min_size: str = "1 KB"
        self.filter_max_size: str = "100 MB"
        self.record_cache: Dict[int, Dict[str, Any]] = {}
        self.background_scan_active: bool = False
        self.background_scan_cancel: bool = False


        # Setup GUI
        self.setup_styles()
        self.create_menu()
        self.create_widgets()
        self.create_status_bar()

        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Bind platform-specific mouse wheel
        self._bind_mousewheel()

    def setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        style.configure('TFrame', background='#f0f0f0')
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'),
                        background='#e0e0e0', padding=5)
        style.configure('TButton', padding=5)
        style.configure('Accent.TButton', foreground='#0066cc')
        style.configure('Warning.TButton', foreground='#cc6600')
        style.configure('Filter.TLabel', foreground='#cc6600',
                        font=('Arial', 9, 'bold'))

    def create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open JSON File", command=self.open_file,
                              accelerator="Ctrl+O")
        file_menu.add_command(label="Open Folder", command=self.open_folder,
                              accelerator="Ctrl+Shift+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit,
                              accelerator="Ctrl+Q")

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy Code", command=self.copy_code,
                              accelerator="Ctrl+Shift+C")
        edit_menu.add_command(label="Find", command=self.show_search,
                              accelerator="Ctrl+F")
        edit_menu.add_command(label="Clear Filter", command=self.clear_filter,
                              accelerator="Ctrl+R")
        edit_menu.add_command(label="Filter by Type/Size", command=self.show_type_filter,
                              accelerator="Ctrl+T")

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Extract Code", command=self.extract_code)
        tools_menu.add_command(label="Export All Codes", command=self.export_all_codes)
        tools_menu.add_separator()
        tools_menu.add_command(label="Statistics", command=self.show_statistics)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        # Keyboard shortcuts
        self.bind('<Control-Shift-O>', lambda e: self.open_folder())
        self.bind('<Control-Shift-o>', lambda e: self.open_folder())
        self.bind('<Control-q>', lambda e: self.quit())
        self.bind('<Control-f>', lambda e: self.show_search())
        self.bind('<Control-r>', lambda e: self.clear_filter())
        self.bind('<Control-Shift-C>', lambda e: self.copy_code())
        self.bind('<Control-Shift-c>', lambda e: self.copy_code())
        self.bind('<Escape>', lambda e: self.clear_filter())
        self.bind('<Control-t>', lambda e: self.show_type_filter())

    def create_widgets(self):
        """Create main GUI widgets."""

        # Top toolbar frame
        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # File info label
        self.file_label = ttk.Label(toolbar, text="No file loaded",
                                    font=('Arial', 9))
        self.file_label.pack(side='left', padx=5)

        # Buttons
        ttk.Button(toolbar, text="📁 Open JSON",
                   command=self.open_file).pack(side='left', padx=2)
        ttk.Button(toolbar, text="📂 Open Folder",
                   command=self.open_folder).pack(side='left', padx=2)
        ttk.Button(toolbar, text="🔍 Search",
                   command=self.show_search).pack(side='left', padx=2)
        ttk.Button(toolbar, text="🏷️ Filter Type/Size",
                   command=self.show_type_filter).pack(side='left', padx=2)

        # Clear filter button (hidden by default)
        self.clear_filter_btn = ttk.Button(toolbar, text="✖ Clear Filter",
                                           command=self.clear_filter,
                                           style='Warning.TButton')

        # Filter indicator label (hidden by default)
        self.filter_indicator = ttk.Label(toolbar, text="",
                                          style='Filter.TLabel')

        # Progress bar (hidden by default)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(toolbar, variable=self.progress_var,
                                            maximum=100, length=200)
        self.progress_bar.pack(side='right', padx=5)
        self.progress_bar.pack_forget()

        # Main container
        main_container = ttk.PanedWindow(self, orient='horizontal')
        main_container.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        # Left panel - Records list
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)

        # Records list header frame
        header_frame = ttk.Frame(left_panel)
        header_frame.pack(fill='x')

        ttk.Label(header_frame, text="RECORDS LIST",
                  style='Header.TLabel').pack(side='left', fill='x', expand=True)

        # Treeview with scrollbars
        tree_frame = ttk.Frame(left_panel)
        tree_frame.pack(fill='both', expand=True, pady=5)

        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side='right', fill='y')

        tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
        tree_scroll_x.pack(side='bottom', fill='x')

        self.records_tree = ttk.Treeview(
            tree_frame,
            columns=('name', 'size', 'loc', 'type', 'quality'),
            show='headings',
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode='browse'
        )

        self.records_tree.heading('name', text='Name', command=lambda: self.sort_tree('name'))
        self.records_tree.heading('size', text='Size', command=lambda: self.sort_tree('size'))
        self.records_tree.heading('loc', text='LOC', command=lambda: self.sort_tree('loc'))
        self.records_tree.heading('type', text='Type', command=lambda: self.sort_tree('type'))
        self.records_tree.heading('quality', text='Quality', command=lambda: self.sort_tree('quality'))

        self.records_tree.column('name', width=150, minwidth=100)
        self.records_tree.column('size', width=70, minwidth=50, anchor='e')
        self.records_tree.column('loc', width=50, minwidth=40, anchor='e')
        self.records_tree.column('type', width=100, minwidth=60)
        self.records_tree.column('quality', width=60, minwidth=50, anchor='center')

        self.records_tree.pack(side='left', fill='both', expand=True)

        tree_scroll_y.config(command=self.records_tree.yview)
        tree_scroll_x.config(command=self.records_tree.xview)

        self.records_tree.bind('<<TreeviewSelect>>', self.on_record_select)
        self.records_tree.bind('<Double-Button-1>', self.on_listbox_double_click)

        self.sort_column = 'name'
        self.sort_reverse = False

        # Pagination controls
        page_frame = ttk.Frame(left_panel)
        page_frame.pack(fill='x', pady=5)

        self.page_label = ttk.Label(page_frame, text="Page: 0 / 0")
        self.page_label.pack(side='top', pady=2)

        btn_frame = ttk.Frame(page_frame)
        btn_frame.pack()

        ttk.Button(btn_frame, text="⏮", width=3,
                   command=self.first_page).pack(side='left', padx=1)
        ttk.Button(btn_frame, text="◄", width=3,
                   command=self.prev_page).pack(side='left', padx=1)
        ttk.Button(btn_frame, text="►", width=3,
                   command=self.next_page).pack(side='left', padx=1)
        ttk.Button(btn_frame, text="⏭", width=3,
                   command=self.last_page).pack(side='left', padx=1)

        # Right panel - Details
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=3)

        # Metadata section
        ttk.Label(right_panel, text="METADATA",
                  style='Header.TLabel').pack(fill='x')

        metadata_frame = ttk.Frame(right_panel, relief='sunken', borderwidth=1)
        metadata_frame.pack(fill='x', padx=5, pady=5)

        self.metadata_text = scrolledtext.ScrolledText(metadata_frame,
                                                       height=12,
                                                       font=('Arial', 9),
                                                       wrap='word',
                                                       state='disabled')
        self.metadata_text.pack(fill='x', padx=5, pady=5)

        # Code content section
        ttk.Label(right_panel, text="CODE CONTENT",
                  style='Header.TLabel').pack(fill='x')

        code_frame = ttk.Frame(right_panel, relief='sunken', borderwidth=1)
        code_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Create a frame for line numbers and code with shared scrollbar
        text_container = ttk.Frame(code_frame)
        text_container.pack(fill='both', expand=True)

        # Line numbers
        self.line_numbers = tk.Text(text_container, width=5,
                                    font=('Consolas', 9),
                                    state='disabled',
                                    background='#f0f0f0',
                                    foreground='#666666',
                                    takefocus=0,
                                    bd=0,
                                    wrap='none')
        self.line_numbers.pack(side='left', fill='y')

        # Vertical scrollbar
        scrollbar_y = ttk.Scrollbar(text_container, orient='vertical')
        scrollbar_y.pack(side='right', fill='y')

        # Horizontal scrollbar
        scrollbar_x = ttk.Scrollbar(code_frame, orient='horizontal')
        scrollbar_x.pack(side='bottom', fill='x')

        # Code text
        self.code_text = tk.Text(text_container,
                                 font=('Consolas', 9),
                                 wrap='none',
                                 state='disabled',
                                 yscrollcommand=scrollbar_y.set,
                                 xscrollcommand=scrollbar_x.set)
        self.code_text.pack(side='left', fill='both', expand=True)

        # Configure scrollbars
        scrollbar_y.config(command=self.on_text_scroll)
        scrollbar_x.config(command=self.code_text.xview)

        # Disable editing in line numbers
        self.line_numbers.bind('<Key>', lambda e: 'break')

        # Configure syntax highlighting tags
        self.code_text.tag_config('keyword', foreground='#0000FF')
        self.code_text.tag_config('string', foreground='#008000')
        self.code_text.tag_config('comment', foreground='#808080',
                                  font=('Consolas', 9, 'italic'))
        self.code_text.tag_config('decorator', foreground='#AA22FF')
        self.code_text.tag_config('number', foreground='#FF6600')
        self.code_text.tag_config('builtin', foreground='#900090')

        # Action buttons
        action_frame = ttk.Frame(right_panel)
        action_frame.pack(fill='x', pady=5)

        ttk.Button(action_frame, text="💾 Extract Code",
                   command=self.extract_code,
                   style='Accent.TButton').pack(side='left', padx=2)
        ttk.Button(action_frame, text="📋 Copy",
                   command=self.copy_code).pack(side='left', padx=2)
        ttk.Button(action_frame, text="💾 Save As...",
                   command=self.save_code_as).pack(side='left', padx=2)

        # Syntax highlighting checkbox
        self.syntax_highlight_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(action_frame, text="Syntax Highlighting",
                        variable=self.syntax_highlight_var,
                        command=self.refresh_current_code).pack(side='right', padx=5)

    def _bind_mousewheel(self):
        """Bind mouse wheel events for all platforms."""
        self.bind_all('<MouseWheel>', self.on_mousewheel)
        self.bind_all('<Button-4>', self.on_mousewheel)
        self.bind_all('<Button-5>', self.on_mousewheel)

    def on_text_scroll(self, *args):
        """Synchronize scrolling between code text and line numbers."""
        self.code_text.yview(*args)
        self.line_numbers.yview(*args)

    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling - cross platform."""
        widget = event.widget
        if widget not in (self.code_text, self.line_numbers):
            try:
                parent = str(widget)
                if 'code_text' not in parent and 'line_numbers' not in parent:
                    return
            except:
                return

        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        elif event.delta:
            delta = -1 if event.delta > 0 else 1
        else:
            return

        self.code_text.yview_scroll(delta * 3, "units")
        self.line_numbers.yview_scroll(delta * 3, "units")
        return 'break'

    def create_status_bar(self):
        """Create status bar."""
        self.status_bar = ttk.Label(self, text="Ready",
                                    relief='sunken',
                                    anchor='w',
                                    font=('Arial', 8))
        self.status_bar.grid(row=2, column=0, sticky='ew')

    def show_filter_indicator(self, search_term: str, result_count: int):
        """Show filter indicator and clear button."""
        self.is_filtered = True
        self.current_search_term = search_term

        # Update and show filter indicator
        self.filter_indicator.config(
            text=f"🔍 Filter: '{search_term}' ({result_count} results)"
        )
        self.filter_indicator.pack(side='left', padx=10)

        # Show clear filter button
        self.clear_filter_btn.pack(side='left', padx=2)

    def hide_filter_indicator(self):
        """Hide filter indicator and clear button."""
        self.is_filtered = False
        self.current_search_term = ""

        # Hide widgets
        self.filter_indicator.pack_forget()
        self.clear_filter_btn.pack_forget()

    def clear_filter(self):
        """Clear the current filter and show all records."""
        if not self.records:
            return

        self.filtered_indices = list(range(len(self.records)))
        self.current_page = 0
        self.update_pagination()
        self.load_page()
        self.hide_filter_indicator()
        self.update_status(f"Filter cleared. Showing all {len(self.records)} records")

    def on_listbox_double_click(self, event):
        """Handle double-click on treeview."""
        if self.is_filtered and not self.filtered_indices:
            self.clear_filter()

    @staticmethod
    def generate_random_filename(length: int = 12, extension: str = ".py") -> str:
        """Generate a random filename with specified length and extension."""
        chars = string.ascii_lowercase + string.digits
        random_name = ''.join(random.choice(chars) for _ in range(length))
        return f"{random_name}{extension}"

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Remove or replace invalid characters from filename."""
        invalid_chars = r'<>:"/\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        filename = ''.join(c for c in filename if ord(c) >= 32)
        filename = filename.strip('. ')
        return filename

    def create_safe_filename(self, original_path: str, index: int = 0) -> str:
        """Create a safe filename from the original path."""
        filename = os.path.basename(original_path)

        if not filename:
            filename = f"code_{index}.py"

        filename = self.sanitize_filename(filename)

        if not os.path.splitext(filename)[1]:
            filename += ".py"

        if len(filename) > self.MAX_FILENAME_LENGTH:
            _, ext = os.path.splitext(filename)
            if not ext or len(ext) > 10:
                ext = ".py"
            random_name = self.generate_random_filename(
                self.RANDOM_FILENAME_LENGTH, ext
            )
            return random_name

        return filename

    def create_safe_export_path(self, folder: str, original_path: str,
                                index: int, used_names: Set[str]) -> str:
        """Create a safe, unique export path for a file."""
        safe_name = self.create_safe_filename(original_path, index)

        base_name, ext = os.path.splitext(safe_name)
        final_name = safe_name
        counter = 1

        while final_name.lower() in used_names:
            new_name = f"{base_name}_{counter}{ext}"
            if len(new_name) > self.MAX_FILENAME_LENGTH:
                final_name = self.generate_random_filename(
                    self.RANDOM_FILENAME_LENGTH, ext
                )
            else:
                final_name = new_name
            counter += 1

        used_names.add(final_name.lower())
        return os.path.join(folder, final_name)

    def open_file(self):
        """Open and load JSON file."""
        file_path = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            file_size = os.path.getsize(file_path)
            if file_size > self.MAX_FILE_SIZE:
                messagebox.showerror("Error",
                                     f"File too large! Maximum size is "
                                     f"{self.MAX_FILE_SIZE / (1024 ** 3):.1f} GB")
                return
        except OSError as e:
            messagebox.showerror("Error", f"Cannot access file:\n{str(e)}")
            return

        self.file_path = file_path
        self.loading_cancelled = False
        self.update_status("Loading file...")
        self.show_progress_bar()
        self.hide_filter_indicator()  # Clear any existing filter

        thread = threading.Thread(target=self.load_json_file, args=(file_path,))
        thread.daemon = True
        thread.start()

    def open_folder(self):
        """Open and scan a folder for Python files."""
        folder_path = filedialog.askdirectory(title="Select Folder to Scan")

        if not folder_path:
            return

        self.file_path = folder_path
        self.loading_cancelled = False
        self.update_status("Scanning folder...")
        self.show_progress_bar()
        self.hide_filter_indicator()

        thread = threading.Thread(target=self.load_folder, args=(folder_path,))
        thread.daemon = True
        thread.start()

    def load_folder(self, folder_path: str):
        """Load Python files from folder recursively (runs in background thread)."""
        try:
            self.records = []
            repo_name = os.path.basename(folder_path)

            py_files = []
            for root, dirs, files in os.walk(folder_path):
                if self.loading_cancelled:
                    self.after(0, lambda: self.update_status("Scanning cancelled"))
                    self.after(0, self.hide_progress_bar)
                    return

                dirs[:] = [d for d in dirs if
                           not d.startswith('.') and d not in ('__pycache__', 'venv', 'env', '.git', 'node_modules')]

                for file in files:
                    if file.endswith('.py'):
                        py_files.append(os.path.join(root, file))

            total_files = len(py_files)
            self.update_status(f"Found {total_files} Python files. Loading...")

            for i, file_path in enumerate(py_files):
                if self.loading_cancelled:
                    self.after(0, lambda: self.update_status("Loading cancelled"))
                    self.after(0, self.hide_progress_bar)
                    return

                try:
                    file_size = os.path.getsize(file_path)

                    if file_size > 10 * 1024 * 1024:
                        continue

                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    rel_path = os.path.relpath(file_path, folder_path)

                    record = {
                        'repo_name': repo_name,
                        'path': rel_path,
                        'size': file_size,
                        'content': content,
                        'license': 'N/A',
                        'copies': 1,
                        'hash': '',
                        'line_mean': 0,
                        'line_max': 0,
                        'alpha_frac': 0,
                        'autogenerated': False
                    }

                    self.records.append(record)

                except (IOError, OSError, UnicodeDecodeError) as e:
                    print(f"Error reading {file_path}: {e}")
                    continue

                if i % 50 == 0:
                    progress = (i / total_files) * 100
                    self.after(0, lambda p=progress: self.progress_var.set(p))
                    self.update_status(f"Loading... {i}/{total_files} files")

            self.after(0, self.on_file_loaded)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to scan folder:\n{str(e)}"))
            self.after(0, lambda: self.update_status("Error scanning folder"))
            self.after(0, self.hide_progress_bar)


    def show_progress_bar(self):
        """Show the progress bar."""
        self.progress_var.set(0)
        self.progress_bar.pack(side='right', padx=5)

    def hide_progress_bar(self):
        """Hide the progress bar."""
        self.progress_bar.pack_forget()

    def load_json_file(self, file_path: str):
        """Load JSON file (runs in background thread)."""
        try:
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)

            self.update_status(f"Loading {file_size_mb:.2f} MB file...")

            self.records = []

            with open(file_path, 'r', encoding='utf-8') as f:
                first_char = f.read(1)
                f.seek(0)

                if first_char == '[':
                    data = json.load(f)
                    self.records = data if isinstance(data, list) else [data]
                else:
                    f.seek(0, 2)
                    total_size = f.tell()
                    f.seek(0)

                    bytes_read = 0
                    for line_num, line in enumerate(f, 1):
                        if self.loading_cancelled:
                            self.after(0, lambda: self.update_status("Loading cancelled"))
                            return

                        bytes_read += len(line.encode('utf-8'))
                        line = line.strip()

                        if line:
                            try:
                                record = json.loads(line)
                                self.records.append(record)
                            except json.JSONDecodeError as e:
                                print(f"Error parsing line {line_num}: {e}")

                        if line_num % 500 == 0:
                            progress = (bytes_read / total_size) * 100
                            self.after(0, lambda p=progress: self.progress_var.set(p))
                            self.update_status(f"Loading... {line_num} records")

            self.after(0, self.on_file_loaded)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error",
                                                       f"Failed to load file:\n{str(e)}"))
            self.after(0, lambda: self.update_status("Error loading file"))
            self.after(0, self.hide_progress_bar)

    def on_file_loaded(self):
        """Called after file is loaded."""
        self.hide_progress_bar()

        self.filtered_indices = list(range(len(self.records)))
        self.update_pagination()

        # file_name = os.path.basename(self.file_path) if self.file_path else "Unknown"
        # self.file_label.config(text=f"File: {file_name}")
        if self.file_path:
            if os.path.isdir(self.file_path):
                name = os.path.basename(self.file_path)
                self.file_label.config(text=f"Folder: {name}")
            else:
                name = os.path.basename(self.file_path)
                self.file_label.config(text=f"File: {name}")
        else:
            self.file_label.config(text="No file loaded")

        self.load_page()
        self.update_status(f"Loaded {len(self.records)} records successfully")
        self.record_cache.clear()
        self.start_background_scan()

    def update_pagination(self):
        """Update pagination values safely."""
        total = len(self.filtered_indices)
        if total == 0:
            self.total_pages = 1
            self.current_page = 0
        else:
            self.total_pages = (total - 1) // self.RECORDS_PER_PAGE + 1
            self.current_page = min(self.current_page, self.total_pages - 1)
            self.current_page = max(0, self.current_page)

    def load_page(self):
        """Load current page of records into treeview."""
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)

        if not self.filtered_indices:
            if self.is_filtered:
                self.records_tree.insert('', 'end', values=(
                    f"No results for '{self.current_search_term}'",
                    '', '', '', ''
                ))
            else:
                self.records_tree.insert('', 'end', values=(
                    'No records loaded', '', '', '', ''
                ))
            self.page_label.config(text="Page: 0 / 0 (No records)")
            self.clear_display()
            return

        start_idx = self.current_page * self.RECORDS_PER_PAGE
        end_idx = min(start_idx + self.RECORDS_PER_PAGE, len(self.filtered_indices))

        for i in range(start_idx, end_idx):
            record_idx = self.filtered_indices[i]
            record = self.records[record_idx]
            cache = self.get_cached_metrics(record_idx)

            name = cache.get('name', 'Unknown')
            size_str = cache.get('size_str', '?')
            loc = cache.get('loc', '?')
            code_type = cache.get('type_str', '...')
            quality = cache.get('quality_str', '...')

            self.records_tree.insert('', 'end', iid=str(record_idx), values=(
                name, size_str, loc, code_type, quality
            ))

        filter_info = ""
        if self.is_filtered:
            filter_info = " [Filtered]"

        self.page_label.config(
            text=f"Page: {self.current_page + 1} / {self.total_pages} "
                 f"({len(self.filtered_indices)}/{len(self.records)} records){filter_info}"
        )

        children = self.records_tree.get_children()
        if children:
            self.records_tree.selection_set(children[0])
            self.on_record_select(None)

    def clear_display(self):
        """Clear the metadata and code display."""
        self.set_text_widget(self.metadata_text, "")
        self.set_text_widget(self.code_text, "")
        self.set_text_widget(self.line_numbers, "")

    def set_text_widget(self, widget: tk.Text, content: str,
                        editable: bool = False):
        """Helper to set content in text widgets."""
        widget.config(state='normal')
        widget.delete('1.0', 'end')
        if content:
            widget.insert('1.0', content)
        if not editable:
            widget.config(state='disabled')

    def on_record_select(self, event):
        """Handle record selection."""
        selection = self.records_tree.selection()
        if not selection:
            return

        item_id = selection[0]

        try:
            record_idx = int(item_id)
        except ValueError:
            return

        if record_idx >= len(self.records):
            return

        self.current_record_index = self.filtered_indices.index(
            record_idx) if record_idx in self.filtered_indices else 0
        record = self.records[record_idx]

        cache = self.get_cached_metrics(record_idx)
        if cache.get('tier', 0) < 3:
            self.calculate_t3_metrics(record_idx)
            cache = self.get_cached_metrics(record_idx)

        quality_details = cache.get('quality_details', {})
        quality_breakdown = "\n".join(
            f"  {'✓' if v else '✗'} {k.replace('_', ' ').title()}"
            for k, v in quality_details.items()
        ) if quality_details else "  Calculating..."

        metadata_info = f"""Repo Name: {record.get('repo_name', 'N/A')}
Path: {record.get('path', 'N/A')}
Size: {cache.get('size_str', 'N/A')} ({record.get('size', 'N/A')} bytes)
Lines of Code: {cache.get('loc', 'N/A')}
Detected Types: {cache.get('type_str', 'N/A')}
Quality Score: {cache.get('quality_str', 'N/A')}

Quality Breakdown:
{quality_breakdown}

License: {record.get('license', 'N/A')}
Copies: {record.get('copies', 'N/A')}"""

        self.set_text_widget(self.metadata_text, metadata_info)

        content = record.get('content', '')
        self.display_code(content)

        self.update_status(
            f"Record {self.current_record_index + 1}/{len(self.filtered_indices)} selected"
        )

    def refresh_current_code(self):
        """Refresh the current code display."""
        if not self.filtered_indices or self.current_record_index >= len(self.filtered_indices):
            return

        record_idx = self.filtered_indices[self.current_record_index]
        record = self.records[record_idx]
        content = record.get('content', '')
        self.display_code(content)

    def display_code(self, code: str):
        """Display code with line numbers and optional syntax highlighting."""
        self.code_text.config(state='normal')
        self.line_numbers.config(state='normal')

        self.code_text.delete('1.0', 'end')
        self.line_numbers.delete('1.0', 'end')

        if not code:
            self.code_text.config(state='disabled')
            self.line_numbers.config(state='disabled')
            return

        self.code_text.insert('1.0', code)

        if self.syntax_highlight_var.get():
            self.apply_syntax_highlighting()

        num_lines = int(self.code_text.index('end-1c').split('.')[0])
        line_nums = '\n'.join(str(i) for i in range(1, num_lines + 1))
        self.line_numbers.insert('1.0', line_nums)

        self.code_text.config(state='disabled')
        self.line_numbers.config(state='disabled')

        self.code_text.yview_moveto(0)
        self.line_numbers.yview_moveto(0)

    def detect_code_type(self, record: Dict[str, Any]) -> Set[str]:
        """Detect code types based on content and path."""
        detected_types = set()

        content = str(record.get('content', '')).lower()
        path = str(record.get('path', '')).lower()

        for type_name, patterns in self.CODE_TYPE_PATTERNS.items():
            for imp in patterns['imports']:
                if imp.lower() in content:
                    detected_types.add(type_name)
                    break

            if type_name not in detected_types:
                for kw in patterns['path_keywords']:
                    if kw.lower() in path:
                        detected_types.add(type_name)
                        break

        return detected_types

    def get_cached_metrics(self, record_idx: int) -> Dict[str, Any]:
        """Get cached metrics or calculate T1."""
        if record_idx in self.record_cache:
            return self.record_cache[record_idx]

        record = self.records[record_idx]
        cache = self.calculate_t1_metrics(record_idx)
        return cache

    def calculate_t1_metrics(self, record_idx: int) -> Dict[str, Any]:
        """Calculate Tier 1 metrics (instant)."""
        record = self.records[record_idx]

        path = record.get('path', '')
        name = os.path.basename(path) if path else f'record_{record_idx}'

        try:
            size = int(record.get('size', 0))
        except (ValueError, TypeError):
            size = 0

        if size >= 1024 * 1024:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        elif size >= 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size} B"

        cache = {
            'tier': 1,
            'name': name[:30] + '...' if len(name) > 30 else name,
            'full_name': name,
            'size': size,
            'size_str': size_str,
            'loc': '...',
            'type_str': '...',
            'quality_str': '...',
        }

        self.record_cache[record_idx] = cache
        return cache

    def calculate_t2_metrics(self, record_idx: int) -> Dict[str, Any]:
        """Calculate Tier 2 metrics (LOC, type, basic quality)."""
        if record_idx not in self.record_cache:
            self.calculate_t1_metrics(record_idx)

        cache = self.record_cache[record_idx]
        if cache.get('tier', 0) >= 2:
            return cache

        record = self.records[record_idx]
        content = record.get('content', '')

        loc = content.count('\n') + 1 if content else 0
        cache['loc'] = loc

        detected_types = self.detect_code_type(record)
        if detected_types:
            type_str = ', '.join(sorted(detected_types)[:2])
            if len(detected_types) > 2:
                type_str += f' +{len(detected_types) - 2}'
        else:
            type_str = '-'
        cache['type_str'] = type_str
        cache['detected_types'] = detected_types

        quality_score = self.calculate_basic_quality(content)
        pct = int((quality_score / self.MAX_QUALITY_SCORE) * 100)
        if pct >= 70:
            cache['quality_str'] = f"★★★ {pct}%"
        elif pct >= 40:
            cache['quality_str'] = f"★★☆ {pct}%"
        else:
            cache['quality_str'] = f"★☆☆ {pct}%"
        cache['quality_score'] = quality_score

        cache['tier'] = 2
        return cache

    def calculate_t3_metrics(self, record_idx: int) -> Dict[str, Any]:
        """Calculate Tier 3 metrics (full quality heuristics)."""
        if record_idx not in self.record_cache:
            self.calculate_t1_metrics(record_idx)

        cache = self.record_cache[record_idx]
        if cache.get('tier', 0) < 2:
            self.calculate_t2_metrics(record_idx)
            cache = self.record_cache[record_idx]

        if cache.get('tier', 0) >= 3:
            return cache

        record = self.records[record_idx]
        content = record.get('content', '')

        quality_details = self.calculate_full_quality(content)
        cache['quality_details'] = quality_details

        score = sum(
            self.QUALITY_WEIGHTS.get(k, 0)
            for k, v in quality_details.items() if v
        )
        pct = int((score / self.MAX_QUALITY_SCORE) * 100)

        if pct >= 70:
            cache['quality_str'] = f"★★★ {pct}%"
        elif pct >= 40:
            cache['quality_str'] = f"★★☆ {pct}%"
        else:
            cache['quality_str'] = f"★☆☆ {pct}%"
        cache['quality_score'] = score

        cache['tier'] = 3
        return cache

    def calculate_basic_quality(self, content: str) -> int:
        """Quick quality estimate for T2."""
        if not content:
            return 0

        score = 0

        if '"""' in content or "'''" in content:
            score += self.QUALITY_WEIGHTS['has_docstring']

        if ': ' in content and '->' in content:
            score += self.QUALITY_WEIGHTS['has_type_hints']

        if 'from ' not in content or 'import *' not in content:
            score += self.QUALITY_WEIGHTS['no_wildcard_imports']

        if 'def ' in content or 'class ' in content:
            score += self.QUALITY_WEIGHTS['has_functions_or_classes']

        if 'eval(' not in content and 'exec(' not in content:
            score += self.QUALITY_WEIGHTS['no_eval_exec']

        return score

    def calculate_full_quality(self, content: str) -> Dict[str, bool]:
        """Full quality heuristics for T3."""
        if not content:
            return {}

        lines = content.split('\n')

        results = {}

        results['has_docstring'] = '"""' in content or "'''" in content

        results['has_type_hints'] = bool(re.search(r'def \w+\([^)]*:\s*\w+', content)) or '->' in content

        comment_lines = sum(1 for l in lines if l.strip().startswith('#'))
        code_lines = sum(1 for l in lines if l.strip() and not l.strip().startswith('#'))
        if code_lines > 0:
            ratio = comment_lines / code_lines
            results['good_comment_ratio'] = 0.05 <= ratio <= 0.4
        else:
            results['good_comment_ratio'] = False

        long_lines = sum(1 for l in lines if len(l) > 120)
        results['reasonable_line_length'] = long_lines < len(lines) * 0.1

        results['no_wildcard_imports'] = 'import *' not in content

        results['has_functions_or_classes'] = 'def ' in content or 'class ' in content

        identifiers = re.findall(r'\b([a-z_][a-z0-9_]*)\b', content, re.I)
        if identifiers:
            good_names = sum(1 for i in identifiers if len(i) > 1 or i in ('i', 'j', 'k', 'x', 'y', 'n'))
            results['good_naming'] = good_names / len(identifiers) > 0.8
        else:
            results['good_naming'] = True

        results['no_bare_except'] = 'except:' not in content

        results['no_eval_exec'] = 'eval(' not in content and 'exec(' not in content

        results['has_exception_handling'] = 'try:' in content and 'except' in content

        nested = max((len(l) - len(l.lstrip())) // 4 for l in lines if l.strip()) if lines else 0
        results['reasonable_complexity'] = nested <= 5

        magic_numbers = re.findall(r'[^0-9_]([2-9]\d{2,}|[1-9]\d{3,})[^0-9_]', content)
        results['no_magic_numbers'] = len(magic_numbers) < 5

        return results

    def start_background_scan(self):
        """Start background T2 scanning."""
        if self.background_scan_active:
            return

        self.background_scan_active = True
        self.background_scan_cancel = False

        thread = threading.Thread(target=self._background_scan_worker, daemon=True)
        thread.start()

    def _background_scan_worker(self):
        """Background worker for T2 metrics."""
        total = len(self.records)

        for i in range(total):
            if self.background_scan_cancel:
                break

            cache = self.record_cache.get(i, {})
            if cache.get('tier', 0) < 2:
                self.calculate_t2_metrics(i)

            if i % 100 == 0:
                pct = int((i / total) * 100)
                self.after(0, lambda p=pct, c=i: self.update_status(f"Indexing: {c}/{total} ({p}%)"))
                self.after(0, self.refresh_visible_items)

        self.background_scan_active = False
        self.after(0, lambda: self.update_status(f"Indexing complete: {total} records"))
        self.after(0, self.refresh_visible_items)

    def refresh_visible_items(self):
        """Refresh currently visible treeview items."""
        for item_id in self.records_tree.get_children():
            try:
                record_idx = int(item_id)
                cache = self.record_cache.get(record_idx, {})

                self.records_tree.item(item_id, values=(
                    cache.get('name', '?'),
                    cache.get('size_str', '?'),
                    cache.get('loc', '...'),
                    cache.get('type_str', '...'),
                    cache.get('quality_str', '...')
                ))
            except (ValueError, tk.TclError):
                pass

    def sort_tree(self, column: str):
        """Sort treeview by column."""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        def get_sort_key(idx: int):
            cache = self.record_cache.get(idx, {})
            if column == 'name':
                return cache.get('full_name', '').lower()
            elif column == 'size':
                return cache.get('size', 0)
            elif column == 'loc':
                loc = cache.get('loc', 0)
                return loc if isinstance(loc, int) else 0
            elif column == 'type':
                return cache.get('type_str', '')
            elif column == 'quality':
                return cache.get('quality_score', 0)
            return ''

        self.filtered_indices.sort(key=get_sort_key, reverse=self.sort_reverse)
        self.load_page()

    def stop_background_scan(self):
        """Stop background scanning."""
        self.background_scan_cancel = True

    def show_type_filter(self):
        """Show filter by type and size dialog."""
        if not self.records:
            messagebox.showwarning("Warning", "No records loaded")
            return

        filter_window = tk.Toplevel(self)
        filter_window.title("Filter by Type & Size")
        filter_window.geometry("550x750")
        filter_window.transient(self)

        main_frame = ttk.Frame(filter_window, padding=10)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="CODE TYPE FILTER",
                  font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))

        type_frame = ttk.LabelFrame(main_frame, text="Select Types (leave unchecked for all)")
        type_frame.pack(fill='x', pady=5)

        type_vars = {}
        type_inner = ttk.Frame(type_frame)
        type_inner.pack(fill='x', padx=5, pady=5)

        col = 0
        row = 0
        for type_name in self.CODE_TYPE_PATTERNS.keys():
            var = tk.BooleanVar(value=(type_name in self.filter_types))
            type_vars[type_name] = var
            ttk.Checkbutton(type_inner, text=type_name, variable=var).grid(
                row=row, column=col, sticky='w', padx=10, pady=2
            )
            col += 1
            if col >= 3:
                col = 0
                row += 1

        ttk.Label(main_frame, text="SIZE FILTER",
                  font=('Arial', 10, 'bold')).pack(anchor='w', pady=(15, 5))

        size_frame = ttk.LabelFrame(main_frame, text="File Size Range")
        size_frame.pack(fill='x', pady=5)

        size_inner = ttk.Frame(size_frame)
        size_inner.pack(fill='x', padx=10, pady=10)

        ttk.Label(size_inner, text="Min Size:").grid(row=0, column=0, sticky='w', padx=5)
        min_size_var = tk.StringVar(value=self.filter_min_size)
        min_combo = ttk.Combobox(size_inner, textvariable=min_size_var,
                                 values=[s[0] for s in self.SIZE_OPTIONS],
                                 state='readonly', width=12)
        min_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(size_inner, text="Max Size:").grid(row=0, column=2, sticky='w', padx=5)
        max_size_var = tk.StringVar(value=self.filter_max_size)
        max_combo = ttk.Combobox(size_inner, textvariable=max_size_var,
                                 values=[s[0] for s in self.SIZE_OPTIONS],
                                 state='readonly', width=12)
        max_combo.grid(row=0, column=3, padx=5, pady=5)

        size_enabled = tk.BooleanVar(value=self.filter_size_enabled)
        ttk.Checkbutton(size_inner, text="Enable size filter",
                        variable=size_enabled).grid(row=1, column=0, columnspan=4, sticky='w', pady=5)

        # Quality filter section
        ttk.Label(main_frame, text="QUALITY FILTER",
                  font=('Arial', 10, 'bold')).pack(anchor='w', pady=(15, 5))

        quality_frame = ttk.LabelFrame(main_frame, text="Minimum Quality Score")
        quality_frame.pack(fill='x', pady=5)

        quality_inner = ttk.Frame(quality_frame)
        quality_inner.pack(fill='x', padx=10, pady=10)

        quality_enabled = tk.BooleanVar(value=getattr(self, 'filter_quality_enabled', False))
        ttk.Checkbutton(quality_inner, text="Enable quality filter",
                        variable=quality_enabled).grid(row=0, column=0, sticky='w', pady=5)

        ttk.Label(quality_inner, text="Min Quality:").grid(row=1, column=0, sticky='w', padx=5)
        quality_options = ['Any', '★☆☆ 20%+', '★★☆ 40%+', '★★★ 70%+']
        min_quality_var = tk.StringVar(value=getattr(self, 'filter_min_quality', 'Any'))
        quality_combo = ttk.Combobox(quality_inner, textvariable=min_quality_var,
                                     values=quality_options,
                                     state='readonly', width=15)
        quality_combo.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        preview_frame = ttk.LabelFrame(main_frame, text="Preview")
        preview_frame.pack(fill='both', expand=True, pady=10)

        preview_text = scrolledtext.ScrolledText(preview_frame, height=10,
                                                 font=('Consolas', 9), state='disabled')
        preview_text.pack(fill='both', expand=True, padx=5, pady=5)

        result_indices = [None]
        is_calculating = [False]

        def get_size_bytes(size_str):
            for label, bytes_val in self.SIZE_OPTIONS:
                if label == size_str:
                    return bytes_val
            return 0

        def get_min_quality_pct(quality_str):
            if quality_str == 'Any':
                return 0
            elif '20%' in quality_str:
                return 20
            elif '40%' in quality_str:
                return 40
            elif '70%' in quality_str:
                return 70
            return 0

        def do_preview_calculation():
            if is_calculating[0]:
                return
            is_calculating[0] = True

            selected_types = [t for t, v in type_vars.items() if v.get()]
            min_bytes = get_size_bytes(min_size_var.get()) if size_enabled.get() else 0
            max_bytes = get_size_bytes(max_size_var.get()) if size_enabled.get() else float('inf')
            min_quality_pct = get_min_quality_pct(min_quality_var.get()) if quality_enabled.get() else 0

            local_indices = []
            type_counts = {t: 0 for t in self.CODE_TYPE_PATTERNS.keys()}
            quality_dist = {'★★★': 0, '★★☆': 0, '★☆☆': 0}

            for i, record in enumerate(self.records):
                # Size filter
                if size_enabled.get():
                    try:
                        size = int(record.get('size', 0))
                    except (ValueError, TypeError):
                        size = 0
                    if size < min_bytes or size > max_bytes:
                        continue

                # Type filter
                detected = self.detect_code_type(record)

                if selected_types:
                    if not detected.intersection(set(selected_types)):
                        continue

                # Quality filter
                if quality_enabled.get() and min_quality_pct > 0:
                    cache = self.record_cache.get(i, {})
                    if cache.get('tier', 0) >= 2:
                        score = cache.get('quality_score', 0)
                        pct = int((score / self.MAX_QUALITY_SCORE) * 100)
                        if pct < min_quality_pct:
                            continue
                    else:
                        content = record.get('content', '')
                        score = self.calculate_basic_quality(content)
                        pct = int((score / self.MAX_QUALITY_SCORE) * 100)
                        if pct < min_quality_pct:
                            continue

                # Record passed all filters
                local_indices.append(i)

                # Count types for matched records only
                for t in detected:
                    type_counts[t] += 1

                # Count quality distribution for matched records
                cache = self.record_cache.get(i, {})
                if cache.get('tier', 0) >= 2:
                    score = cache.get('quality_score', 0)
                    pct = int((score / self.MAX_QUALITY_SCORE) * 100)
                    if pct >= 70:
                        quality_dist['★★★'] += 1
                    elif pct >= 40:
                        quality_dist['★★☆'] += 1
                    else:
                        quality_dist['★☆☆'] += 1

            is_calculating[0] = False
            self.after(0, lambda li=local_indices, tc=type_counts, qd=quality_dist: finish_preview(li, tc, qd))

        def finish_preview(indices, type_counts, quality_dist):
            result_indices[0] = indices

            try:
                preview_text.config(state='normal')
                preview_text.delete('1.0', 'end')

                preview = f"Matching Records: {len(indices)} / {len(self.records)}\n\n"

                if indices:
                    preview += "Type Distribution (filtered results):\n"
                    preview += "─" * 40 + "\n"

                    for type_name, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                        if count > 0:
                            pct = (count / len(indices)) * 100
                            bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
                            preview += f"{type_name:<18} {bar} {count:>6} ({pct:>5.1f}%)\n"

                    preview += "\nQuality Distribution (filtered results):\n"
                    preview += "─" * 40 + "\n"
                    for qual, count in sorted(quality_dist.items(), key=lambda x: x[1], reverse=True):
                        if count > 0:
                            pct = (count / len(indices)) * 100
                            bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
                            preview += f"{qual:<18} {bar} {count:>6} ({pct:>5.1f}%)\n"
                else:
                    preview += "No records match the current filters.\n"

                preview_text.insert('1.0', preview)
                preview_text.config(state='disabled')
            except tk.TclError:
                pass

        def update_preview(*args):
            preview_text.config(state='normal')
            preview_text.delete('1.0', 'end')
            preview_text.insert('1.0', "Calculating...")
            preview_text.config(state='disabled')

            thread = threading.Thread(target=do_preview_calculation, daemon=True)
            thread.start()

        def apply_filter():
            if result_indices[0] is None or len(result_indices[0]) == 0:
                messagebox.showwarning("Warning", "No matching records")
                return

            self.filter_types = {t for t, v in type_vars.items() if v.get()}
            self.filter_size_enabled = size_enabled.get()
            self.filter_min_size = min_size_var.get()
            self.filter_max_size = max_size_var.get()
            self.filter_quality_enabled = quality_enabled.get()
            self.filter_min_quality = min_quality_var.get()

            self.filtered_indices = result_indices[0].copy()
            self.current_page = 0
            self.update_pagination()
            self.load_page()

            filter_desc = []
            if self.filter_types:
                filter_desc.append(f"Types: {', '.join(self.filter_types)}")
            if self.filter_size_enabled:
                filter_desc.append(f"Size: {self.filter_min_size}-{self.filter_max_size}")
            if self.filter_quality_enabled:
                filter_desc.append(f"Quality: {self.filter_min_quality}")

            desc = " | ".join(filter_desc) if filter_desc else "Custom Filter"
            self.show_filter_indicator(desc, len(result_indices[0]))
            self.update_status(f"Filter applied: {len(result_indices[0])} records")

        def clear_all():
            self.filter_types = set()
            self.filter_size_enabled = False
            self.filter_min_size = "1 KB"
            self.filter_max_size = "100 MB"
            self.filter_quality_enabled = False
            self.filter_min_quality = "Any"
            self.clear_filter()
            filter_window.destroy()

        def export_filtered():
            if result_indices[0] is None or len(result_indices[0]) == 0:
                messagebox.showwarning("Warning", "No matching records to export")
                return

            folder = filedialog.askdirectory(title="Select Export Folder")
            if not folder:
                return

            indices_to_export = result_indices[0].copy()
            filter_window.destroy()

            self.show_progress_bar()
            thread = threading.Thread(
                target=self._export_all_codes_thread,
                args=(folder, indices_to_export)
            )
            thread.daemon = True
            thread.start()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="✔ Apply Filter",
                   command=apply_filter).pack(side='left', padx=5)
        ttk.Button(button_frame, text="💾 Export Filtered",
                   command=export_filtered, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="✖ Clear All",
                   command=clear_all, style='Warning.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel",
                   command=filter_window.destroy).pack(side='right', padx=5)

        for var in type_vars.values():
            var.trace_add('write', update_preview)
        size_enabled.trace_add('write', update_preview)
        min_size_var.trace_add('write', update_preview)
        max_size_var.trace_add('write', update_preview)
        quality_enabled.trace_add('write', update_preview)
        min_quality_var.trace_add('write', update_preview)

        update_preview()

    def apply_syntax_highlighting(self):
        """Apply Python syntax highlighting to the code text."""
        code = self.code_text.get('1.0', 'end-1c')

        for tag in ['keyword', 'string', 'comment', 'decorator', 'number', 'builtin']:
            self.code_text.tag_remove(tag, '1.0', 'end')

        for match in re.finditer(r'#.*$', code, re.MULTILINE):
            self._apply_tag('comment', match.start(), match.end())

        for match in re.finditer(r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\')', code):
            self._apply_tag('string', match.start(), match.end())

        for match in re.finditer(r'@\w+', code):
            self._apply_tag('decorator', match.start(), match.end())

        for match in re.finditer(r'\b(' + '|'.join(self.PYTHON_KEYWORDS) + r')\b', code):
            self._apply_tag('keyword', match.start(), match.end())

        for match in re.finditer(r'\b\d+\.?\d*\b', code):
            self._apply_tag('number', match.start(), match.end())

    def _apply_tag(self, tag: str, start_idx: int, end_idx: int):
        """Apply a tag to a range of text."""
        start_pos = f"1.0+{start_idx}c"
        end_pos = f"1.0+{end_idx}c"
        self.code_text.tag_add(tag, start_pos, end_pos)

    def get_current_record(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected record safely."""
        selection = self.records_tree.selection()
        if not selection:
            return None

        try:
            record_idx = int(selection[0])
        except ValueError:
            return None

        if record_idx >= len(self.records):
            return None

        return self.records[record_idx]

    def extract_code(self):
        """Extract code to a file."""
        record = self.get_current_record()
        if not record:
            messagebox.showwarning("Warning", "No record selected")
            return

        content = record.get('content', '')
        if not content:
            messagebox.showwarning("Warning", "No code content to extract")
            return

        original_path = record.get('path', 'code.py')
        suggested_name = self.create_safe_filename(original_path)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            initialfile=suggested_name,
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Code extracted to:\n{file_path}")
                self.update_status(f"Code extracted to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def copy_code(self):
        """Copy code to clipboard."""
        record = self.get_current_record()
        if not record:
            messagebox.showwarning("Warning", "No record selected")
            return

        content = record.get('content', '')
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.update_status("Code copied to clipboard")
        else:
            messagebox.showwarning("Warning", "No code content to copy")

    def save_code_as(self):
        """Save code as file."""
        self.extract_code()

    def export_all_codes(self):
        """Export all code records to separate files."""
        if not self.records:
            messagebox.showwarning("Warning", "No records loaded")
            return

        folder = filedialog.askdirectory(title="Select Export Folder")
        if not folder:
            return

        # Determine what to export
        if self.is_filtered and self.filtered_indices:
            export_count = len(self.filtered_indices)
            export_msg = f"Export {export_count} filtered records"
            export_indices = self.filtered_indices
        else:
            export_count = len(self.records)
            export_msg = f"Export all {export_count} records"
            export_indices = list(range(len(self.records)))

        result = messagebox.askyesno(
            "Confirm Export",
            f"{export_msg} to:\n{folder}\n\n"
            "Long filenames will be replaced with random names.\n"
            "Continue?"
        )
        if not result:
            return

        self.show_progress_bar()
        thread = threading.Thread(
            target=self._export_all_codes_thread,
            args=(folder, export_indices)
        )
        thread.daemon = True
        thread.start()

    def _export_all_codes_thread(self, folder: str, indices: List[int]):
        """Export all codes (runs in background thread)."""
        try:
            exported = 0
            errors = 0
            used_names: Set[str] = set()
            total = len(indices)

            for i, record_idx in enumerate(indices):
                record = self.records[record_idx]
                content = record.get('content', '')
                if not content:
                    continue

                original_path = record.get('path', f'code_{i}.py')
                file_path = self.create_safe_export_path(
                    folder, original_path, i, used_names
                )

                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    exported += 1
                except Exception as e:
                    errors += 1
                    print(f"Error exporting {file_path}: {e}")

                if i % 100 == 0:
                    progress = (i / total) * 100
                    self.after(0, lambda p=progress: self.progress_var.set(p))
                    self.update_status(f"Exporting... {i}/{total}")

            self.after(0, self.hide_progress_bar)

            result_msg = f"Exported {exported} files to:\n{folder}"
            if errors > 0:
                result_msg += f"\n\n{errors} files failed to export."

            self.after(0, lambda: messagebox.showinfo("Export Complete", result_msg))
            self.update_status(f"Exported {exported} code files")

        except Exception as e:
            self.after(0, self.hide_progress_bar)
            self.after(0, lambda: messagebox.showerror("Error", f"Export failed:\n{str(e)}"))

    def show_search(self):
        """Show search dialog."""
        search_window = tk.Toplevel(self)
        search_window.title("Search Records")
        search_window.geometry("450x200")
        search_window.transient(self)
        search_window.grab_set()

        main_frame = ttk.Frame(search_window, padding=10)
        main_frame.pack(fill='both', expand=True)

        # Search field selection
        ttk.Label(main_frame, text="Search in:").grid(
            row=0, column=0, padx=5, pady=5, sticky='w'
        )

        search_field = tk.StringVar(value="repo_name")
        field_frame = ttk.Frame(main_frame)
        field_frame.grid(row=0, column=1, sticky='w')

        ttk.Radiobutton(field_frame, text="Repo Name", variable=search_field,
                        value="repo_name").pack(side='left', padx=5)
        ttk.Radiobutton(field_frame, text="Path", variable=search_field,
                        value="path").pack(side='left', padx=5)
        ttk.Radiobutton(field_frame, text="Content", variable=search_field,
                        value="content").pack(side='left', padx=5)

        # Search term entry
        ttk.Label(main_frame, text="Search term:").grid(
            row=1, column=0, padx=5, pady=10, sticky='w'
        )
        search_entry = ttk.Entry(main_frame, width=40)
        search_entry.grid(row=1, column=1, padx=5, pady=10, sticky='w')
        search_entry.focus()

        # Pre-fill with current search term if exists
        if self.current_search_term:
            search_entry.insert(0, self.current_search_term)
            search_entry.select_range(0, 'end')

        # Case sensitive option
        case_sensitive = tk.BooleanVar(value=False)
        ttk.Checkbutton(main_frame, text="Case sensitive",
                        variable=case_sensitive).grid(row=2, column=1, sticky='w')

        # Result preview label
        result_label = ttk.Label(main_frame, text="", foreground='#666666')
        result_label.grid(row=3, column=0, columnspan=2, pady=5)

        def preview_search(*args):
            """Preview search results count."""
            term = search_entry.get()
            if not term:
                result_label.config(text=f"Total records: {len(self.records)}")
                return

            field = search_field.get()
            search_term = term if case_sensitive.get() else term.lower()

            count = 0
            for r in self.records:
                value = str(r.get(field, ''))
                if not case_sensitive.get():
                    value = value.lower()
                if search_term in value:
                    count += 1

            result_label.config(text=f"Matching records: {count}")

        # Bind preview to entry changes
        search_entry.bind('<KeyRelease>', preview_search)
        search_field.trace('w', preview_search)
        preview_search()  # Initial preview

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        def do_search():
            term = search_entry.get()
            field = search_field.get()

            if not term:
                self.filtered_indices = list(range(len(self.records)))
                self.hide_filter_indicator()
            else:
                search_term = term if case_sensitive.get() else term.lower()

                self.filtered_indices = []
                for i, r in enumerate(self.records):
                    value = str(r.get(field, ''))
                    if not case_sensitive.get():
                        value = value.lower()
                    if search_term in value:
                        self.filtered_indices.append(i)

                # Show filter indicator
                self.show_filter_indicator(term, len(self.filtered_indices))

                # If no results, ask user what to do
                if not self.filtered_indices:
                    search_window.destroy()
                    result = messagebox.askyesno(
                        "No Results",
                        f"No records found matching '{term}'.\n\n"
                        "Would you like to clear the filter and show all records?"
                    )
                    if result:
                        self.clear_filter()
                    else:
                        # Keep the empty filter active so user sees the message
                        self.current_page = 0
                        self.update_pagination()
                        self.load_page()
                    return

            self.current_page = 0
            self.update_pagination()
            self.load_page()
            self.update_status(f"Found {len(self.filtered_indices)} matching records")
            search_window.destroy()

        def clear_and_close():
            self.clear_filter()
            search_window.destroy()

        ttk.Button(button_frame, text="🔍 Search",
                   command=do_search).pack(side='left', padx=5)
        ttk.Button(button_frame, text="✖ Clear Filter",
                   command=clear_and_close).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel",
                   command=search_window.destroy).pack(side='left', padx=5)

        search_entry.bind('<Return>', lambda e: do_search())
        search_entry.bind('<Escape>', lambda e: search_window.destroy())

    def show_statistics(self):
        """Show statistics about loaded data."""
        if not self.records:
            messagebox.showinfo("Statistics", "No data loaded")
            return

        try:
            total = len(self.records)

            total_size = 0
            for r in self.records:
                size_val = r.get('size', 0)
                try:
                    total_size += int(size_val) if size_val else 0
                except (ValueError, TypeError):
                    pass

            licenses: Dict[str, int] = {}
            for r in self.records:
                lic = str(r.get('license', 'unknown'))
                licenses[lic] = licenses.get(lic, 0) + 1

            avg_size = total_size / total if total > 0 else 0

            extensions: Dict[str, int] = {}
            for r in self.records:
                path = r.get('path', '')
                ext = os.path.splitext(path)[1].lower() or 'no extension'
                extensions[ext] = extensions.get(ext, 0) + 1

            stats = f"""═══════════════════════════════════════
           REPOSITORY STATISTICS
═══════════════════════════════════════

Total Records: {total:,}
Total Code Size: {total_size:,} bytes ({total_size / (1024 * 1024):.2f} MB)
Average File Size: {avg_size:,.0f} bytes

"""
            if self.is_filtered:
                stats += f"""Currently Filtered: {len(self.filtered_indices):,} records
Filter Term: '{self.current_search_term}'

"""

            stats += """───────────────────────────────────────
License Distribution (Top 10):
───────────────────────────────────────
"""
            for lic, count in sorted(licenses.items(), key=lambda x: x[1], reverse=True)[:10]:
                percentage = (count / total) * 100
                bar = '█' * int(percentage / 5) + '░' * (20 - int(percentage / 5))
                stats += f"  {lic[:20]:<20} {bar} {count:>6,} ({percentage:>5.1f}%)\n"

            stats += """
───────────────────────────────────────
File Extensions (Top 10):
───────────────────────────────────────
"""
            for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]:
                percentage = (count / total) * 100
                bar = '█' * int(percentage / 5) + '░' * (20 - int(percentage / 5))
                stats += f"  {ext[:20]:<20} {bar} {count:>6,} ({percentage:>5.1f}%)\n"

            stats_window = tk.Toplevel(self)
            stats_window.title("Repository Statistics")
            stats_window.geometry("600x500")
            stats_window.transient(self)

            text_widget = scrolledtext.ScrolledText(stats_window,
                                                    font=('Consolas', 10),
                                                    wrap='word')
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', stats)
            text_widget.config(state='disabled')

            ttk.Button(stats_window, text="Close",
                       command=stats_window.destroy).pack(pady=5)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate statistics:\n{str(e)}")

    def show_about(self):
        """Show about dialog."""
        about_text = """JSON Code Repository Viewer v1.2

A professional tool for browsing and extracting
code from large JSON repositories.

Features:
• Load and browse large JSON files (up to 2GB)
• Scan folders recursively for Python files
• View code with synchronized line numbers
• Python syntax highlighting
• Extract individual or all code files
• Handles long filenames automatically
• Search and filter records
• View metadata and statistics

Keyboard Shortcuts:
• Ctrl+O: Open file
• Ctrl+Shift+O: Open folder
• Ctrl+F: Search
• Ctrl+R / ESC: Clear filter
• Ctrl+Shift+C: Copy code
• Ctrl+Q: Quit

© 2026"""
        messagebox.showinfo("About", about_text)

    def first_page(self):
        """Go to first page."""
        if self.current_page != 0:
            self.current_page = 0
            self.load_page()

    def prev_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self.load_page()

    def next_page(self):
        """Go to next page."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.load_page()

    def last_page(self):
        """Go to last page."""
        last = max(0, self.total_pages - 1)
        if self.current_page != last:
            self.current_page = last
            self.load_page()

    def update_status(self, message: str):
        """Update status bar (thread-safe)."""
        self.after(0, lambda: self.status_bar.config(text=message))


if __name__ == "__main__":
    app = JSONCodeViewer()
    app.mainloop()
