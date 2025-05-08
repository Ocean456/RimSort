import json
import os
import subprocess
from typing import Any, Optional

from loguru import logger
from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QFont, QKeyEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.utils.app_info import AppInfo
from app.utils.generic import platform_specific_open


class FileSearchDialog(QDialog):
    """dialog for searching files within mods"""

    # signals for search events
    search_started = Signal(str, str, dict)  # search_text, algorithm, options
    search_stopped = Signal()
    result_found = Signal(str, str, str)  # mod_name, file_name, path

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("文件搜索")
        self.setWindowFlags(Qt.WindowType.Window)
        self.resize(900, 700)  # Set a reasonable default size
        self._search_paths: list[str] = []
        self._recent_searches: list[str] = []
        self._max_recent_searches = 10

        # Added a placeholder for search_worker to resolve attribute access issues
        self.search_worker = None

        # Load recent searches
        self._load_recent_searches()

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)

        # ===== SEARCH QUERY SECTION =====
        # Top section with search input and buttons
        top_section = QWidget()
        top_layout = QVBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)

        # ===== SEARCH QUERY AND SCOPE ROW =====
        # Combined row for search input and scope
        search_row = QHBoxLayout()
        search_row.setSpacing(15)

        # Left side - Search input with label
        search_input_layout = QHBoxLayout()
        search_input_layout.setSpacing(5)

        search_label = QLabel("搜索内容：")
        search_label.setFixedWidth(80)
        search_input_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入要在文件中搜索的文本")
        search_input_layout.addWidget(self.search_input)

        self.recent_searches_button = QPushButton("▼")
        self.recent_searches_button.setFixedWidth(25)
        self.recent_searches_button.setToolTip("最近的搜索")
        self.recent_searches_button.clicked.connect(self._show_recent_searches)
        search_input_layout.addWidget(self.recent_searches_button)

        # Add search input to the row (takes 3/5 of the width)
        search_row.addLayout(search_input_layout, 3)

        # Right side - Search scope with label
        scope_layout = QHBoxLayout()
        scope_layout.setSpacing(5)

        scope_label = QLabel("搜索范围：")
        scope_label.setFixedWidth(80)
        scope_layout.addWidget(scope_label)

        self.search_scope = QComboBox()
        self.search_scope.addItem("启用的模组", "active mods")
        self.search_scope.addItem("未启用的模组", "inactive mods")
        self.search_scope.addItem("所有模组", "all mods")
        self.search_scope.addItem("配置文件夹", "configs folder")
        scope_layout.addWidget(self.search_scope)

        # Add scope to the row (takes 2/5 of the width)
        search_row.addLayout(scope_layout, 2)

        # Add the combined row to the top layout
        top_layout.addLayout(search_row)

        # ===== SEARCH OPTIONS SECTION =====
        # Create a horizontal layout for the options area
        options_area = QVBoxLayout()
        options_area.setSpacing(20)

        # Left column - Search options
        search_options_column = QHBoxLayout()
        search_options_column.setSpacing(8)

        search_options_label = QLabel("搜索方法：")
        search_options_label.setStyleSheet("font-weight: bold;")
        search_options_column.addWidget(search_options_label)

        self.case_sensitive = QCheckBox("区分大小写")
        self.case_sensitive.setToolTip("搜索时区分大小写")

        self.use_regex = QCheckBox("使用正则表达式（模式搜索）")
        self.use_regex.setToolTip(
            "启用正则表达式搜索功能\n"
            "示例：\n"
            "- 使用 'def.*\\(' 查找函数定义\n"
            "- 使用 '<[^>]+>' 查找 XML 标签\n"
            "- 使用 '\\d+\\.\\d+(\\.\\d+)?' 查找版本号"
        )

        # XML only checkbox (moved from scope section)
        self.xml_only = QCheckBox("仅限 XML 文件")
        self.xml_only.setToolTip(
            "选中时，仅搜索 XML 文件，并使用优化的 XML 搜索方式。\n"
            "未选中时，使用标准搜索，搜索所有文件类型。"
        )
        self.xml_only.setChecked(True)

        # Connect signal to update algorithm on checkbox change
        self.xml_only.stateChanged.connect(self._update_algorithm_for_file_type)

        search_options_column.addWidget(self.xml_only)
        search_options_column.addWidget(self.case_sensitive)
        search_options_column.addWidget(self.use_regex)
        search_options_column.addStretch()

        # Connect regex checkbox
        self.use_regex.stateChanged.connect(self._on_regex_checkbox_changed)

        # Initialize the state based on the current checkbox state
        self._on_regex_checkbox_changed(self.use_regex.checkState())

        # Right column - Skip options
        skip_options_column = QHBoxLayout()
        skip_options_column.setSpacing(8)

        skip_options_label = QLabel("从搜索中排除：")
        skip_options_label.setStyleSheet("font-weight: bold;")
        skip_options_column.addWidget(skip_options_label)

        self.skip_translations = QCheckBox("跳过翻译")
        self.skip_translations.setChecked(True)
        self.skip_translations.setToolTip(
            "跳过翻译文件以提高搜索速度"
        )

        self.skip_git = QCheckBox("跳过 .git 文件夹")
        self.skip_git.setChecked(True)
        self.skip_git.setToolTip("跳过 Git 仓库文件夹")

        self.skip_source = QCheckBox("跳过 Source 文件夹")
        self.skip_source.setChecked(True)
        self.skip_source.setToolTip("跳过包含 C# 代码的 Source 文件夹")

        self.skip_textures = QCheckBox("跳过 Textures 文件夹")
        self.skip_textures.setChecked(True)
        self.skip_textures.setToolTip("跳过包含图像的 Textures 文件夹")

        skip_options_column.addWidget(self.skip_translations)
        skip_options_column.addWidget(self.skip_git)
        skip_options_column.addWidget(self.skip_source)
        skip_options_column.addWidget(self.skip_textures)
        skip_options_column.addStretch()

        # Add columns to options area
        options_area.addLayout(search_options_column)
        options_area.addLayout(skip_options_column)

        # Add options area to top layout
        top_layout.addLayout(options_area)

        # Search and Stop buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Add a note about search method
        search_method_info = QLabel(
            "搜索方法会根据选项自动选择"
        )
        buttons_layout.addWidget(search_method_info)

        # Add spacer to push buttons to the right
        buttons_layout.addStretch()

        self.search_button = QPushButton("搜索")
        self.search_button.setMinimumWidth(100)
        self.search_button.setEnabled(True)
        self.search_button.setStyleSheet("font-weight: bold; background-color: green;")

        self.stop_button = QPushButton("停止")
        self.stop_button.setMinimumWidth(100)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("font-weight: bold; background-color: normal;")

        buttons_layout.addWidget(self.search_button)
        buttons_layout.addWidget(self.stop_button)

        top_layout.addLayout(buttons_layout)

        # Add top section to main layout
        main_layout.addWidget(top_section)

        # Add a horizontal separator line
        separator = QWidget()
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)

        # ===== PROGRESS AND RESULTS SECTION =====
        results_section = QWidget()
        results_layout = QVBoxLayout(results_section)
        results_layout.setContentsMargins(0, 5, 0, 0)
        results_layout.setSpacing(10)

        # Progress section with improved layout and visual feedback
        progress_group = QWidget()
        progress_group.setObjectName("progressGroup")  # For potential styling
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(8)

        # Status and stats in a horizontal layout
        status_row = QHBoxLayout()
        status_row.setSpacing(10)

        # Statistics
        self.stats_label = QLabel("准备搜索")
        self.stats_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        status_row.addWidget(self.stats_label)

        progress_layout.addLayout(status_row)

        results_layout.addWidget(progress_group)

        # Results filter with icon
        filter_group = QWidget()
        filter_layout = QHBoxLayout(filter_group)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(10)

        filter_label = QLabel("筛选结果:")
        filter_label.setFixedWidth(80)
        filter_layout.addWidget(filter_label)

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText(
            "通过模组名称、文件名或路径过滤结果"
        )
        filter_layout.addWidget(self.filter_input)

        results_layout.addWidget(filter_group)

        # Results table with header
        results_table_group = QWidget()
        results_table_layout = QVBoxLayout(results_table_group)
        results_table_layout.setContentsMargins(0, 0, 0, 0)
        results_table_layout.setSpacing(5)

        results_header = QHBoxLayout()
        results_label = QLabel("搜索结果：")
        results_label.setStyleSheet("font-weight: bold;")
        results_header.addWidget(results_label)

        # Add a right-aligned label with instructions
        results_help = QLabel("双击结果以打开文件")
        results_help.setAlignment(Qt.AlignmentFlag.AlignRight)
        results_header.addWidget(results_help)

        results_table_layout.addLayout(results_header)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(
            ["模组名称", "文件名", "路径", "预览"]
        )

        # Set table properties for better appearance
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.results_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.results_table.setSortingEnabled(True)
        self.results_table.verticalHeader().setVisible(False)

        # Set a minimum height for the results table
        self.results_table.setMinimumHeight(300)

        # Configure column stretching
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )  # Mod name
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )  # File name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Path
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )  # Preview (stretch to fill remaining space)

        # Enable context menu
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self._show_context_menu)

        # Connect double-click to open file
        self.results_table.cellDoubleClicked.connect(self._on_cell_double_clicked)

        # Add table to results layout
        results_table_layout.addWidget(self.results_table)

        # Add the results table group to the results layout
        results_layout.addWidget(results_table_group)

        # Add results section to main layout with stretch factor
        main_layout.addWidget(
            results_section, 1
        )  # Give it a stretch factor of 1 to take available space

        # Connect filter input to filter method
        self.filter_input.textChanged.connect(self._on_filter_changed)

        # Connect search button to start search timer
        self.search_button.clicked.connect(self._on_search_start)

        # Connect stop button to cancel search
        self.stop_button.clicked.connect(self.search_stopped.emit)

        # Set focus to search input
        self.search_input.setFocus()

        # Initialize algorithm based on XML only checkbox (after all UI elements are created)
        self._update_algorithm_for_file_type()

    def _on_search_start(self) -> None:
        """Initialize search timer and UI state when search starts"""
        logger.info("Search started from FileSearchDialog.")
        self.search_started.emit("", "", {})

        # Enable/disable buttons
        self.search_button.setEnabled(False)
        self.search_button.setStyleSheet(
            "font-weight: bold; background-color: green; color: white; border: 2px solid darkgreen;"
            if self.search_button.isEnabled()
            else "font-weight: bold; background-color: lightgray; color: darkgray; border: 2px solid gray;"
        )
        self.stop_button.setEnabled(True)
        self.stop_button.setStyleSheet(
            "font-weight: bold; background-color: red; color: white; border: 2px solid darkred;"
            if self.stop_button.isEnabled()
            else "font-weight: bold; background-color: lightgray; color: darkgray; border: 2px solid gray;"
        )

    def _on_search_complete(self) -> None:
        """Update UI state when search completes"""
        logger.info("Search completed successfully.")
        self.search_stopped.emit()

        # Ensure the status label is updated correctly when search completes
        result_count = self.results_table.rowCount()

        if result_count > 0:
            self.stats_label.setText(f"找到 {result_count} 个结果")
        else:
            self.stats_label.setText("未找到结果")

        # Reset buttons
        self.search_button.setEnabled(True)
        self.search_button.setStyleSheet(
            "font-weight: bold; background-color: green; color: white; border: 2px solid darkgreen;"
        )
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet(
            "font-weight: bold; background-color: lightgray; color: darkgray; border: 2px solid gray;"
        )

        # Focus on filter input if we have results
        if result_count > 0:
            self.filter_input.setFocus()

        logger.debug(f"Search complete with {result_count} results.")

    def _show_context_menu(self, pos: QPoint) -> None:
        """
        Show context menu for results table.

        Args:
            pos: Position where the context menu is requested.
        """
        menu = QMenu()

        # get selected item
        item = self.results_table.itemAt(pos)
        if item is None:
            return

        row = item.row()
        path_item = self.results_table.item(row, 2)
        if path_item is None:
            return

        path = path_item.text()

        # Create actions with keyboard shortcuts
        open_file = menu.addAction("打开文件（Enter）")
        open_file.setShortcut("Return")

        open_folder = menu.addAction("打开包含文件的文件夹（Ctrl+O）")
        open_folder.setShortcut("Ctrl+O")

        copy_path = menu.addAction("复制路径（Ctrl+C）")
        copy_path.setShortcut("Ctrl+C")

        # Add a separator and more actions
        menu.addSeparator()

        # Add "Open With" submenu
        open_with_menu = menu.addMenu("使用......打开")
        open_with_notepad = open_with_menu.addAction("记事本")
        open_with_vscode = open_with_menu.addAction("VS Code")
        open_with_default = open_with_menu.addAction("默认编辑器")

        # connect actions
        open_file.triggered.connect(lambda: self._open_file(path))
        open_folder.triggered.connect(lambda: self._open_folder(path))
        copy_path.triggered.connect(lambda: self._copy_path(path))

        # Connect "Open With" actions
        open_with_notepad.triggered.connect(lambda: self._open_with(path, "notepad"))
        open_with_vscode.triggered.connect(lambda: self._open_with(path, "code"))
        open_with_default.triggered.connect(lambda: self._open_file(path))

        menu.exec(self.results_table.viewport().mapToGlobal(pos))

    def _open_file(self, path: str) -> None:
        """open file in default application"""
        if path and os.path.exists(path):
            platform_specific_open(path)
        else:
            logger.warning(f"Cannot open file: {path} (file does not exist)")

    def _open_folder(self, path: str) -> None:
        """open containing folder"""
        folder = os.path.dirname(path)
        if folder and os.path.exists(folder):
            platform_specific_open(folder)
        else:
            logger.warning(f"Cannot open folder: {folder} (folder does not exist)")

    def _copy_path(self, path: str) -> None:
        """copy path to clipboard"""
        QApplication.clipboard().setText(path)

    def _open_with(self, path: str, program: str) -> None:
        """open file with specified program"""
        try:
            if os.name == "nt":  # Windows
                if program == "notepad":
                    subprocess.Popen(["notepad.exe", path])
                elif program == "code":
                    subprocess.Popen(["code", path])
                else:
                    self._open_file(path)
            else:  # Unix-like
                if program == "notepad":
                    subprocess.Popen(["gedit", path])
                elif program == "code":
                    subprocess.Popen(["code", path])
                else:
                    self._open_file(path)
        except Exception as e:
            logger.error(f"Error opening file with {program}: {e}")
            # Fallback to default opener
            self._open_file(path)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard shortcuts"""
        # Get currently selected row
        selected_rows = self.results_table.selectedItems()
        if not selected_rows:
            return super().keyPressEvent(event)

        # Find the path in the selected row
        row = selected_rows[0].row()
        path_item = self.results_table.item(row, 2)
        if not path_item:
            return super().keyPressEvent(event)

        path = path_item.text()

        # Handle keyboard shortcuts
        if event.key() == Qt.Key.Key_Return:
            self._open_file(path)
        elif (
            event.key() == Qt.Key.Key_C
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self._copy_path(path)
        elif (
            event.key() == Qt.Key.Key_O
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self._open_folder(path)
        else:
            super().keyPressEvent(event)

    def _on_cell_double_clicked(self, row: int, column: int) -> None:
        """Handle double-click on a cell"""
        logger.debug(f"Cell double-clicked at row {row}, column {column}.")
        if row >= 0:
            path_item = self.results_table.item(row, 2)
            if path_item is not None:
                self._open_file(path_item.text())

    def get_search_options(self) -> dict[str, Any]:
        """Get current search options as a dictionary, including exclude options."""
        # Determine file type based on XML only checkbox
        file_type = "XML Files" if self.xml_only.isChecked() else "All Files"

        # Set file extensions based on XML only checkbox
        selected_extensions = [".xml"] if self.xml_only.isChecked() else []

        # Determine the search algorithm based on checkboxes
        if self.use_regex.isChecked():
            algorithm = "pattern search"
        elif self.xml_only.isChecked():
            algorithm = "xml search"
        else:
            algorithm = "standard search"

        # Include exclude options in the search options
        exclude_options = {
            "skip_translations": self.skip_translations.isChecked(),
            "skip_git": self.skip_git.isChecked(),
            "skip_source": self.skip_source.isChecked(),
            "skip_textures": self.skip_textures.isChecked(),
        }

        return {
            "scope": self.search_scope.currentData(),
            "algorithm": algorithm,
            "case_sensitive": self.case_sensitive.isChecked(),
            "use_regex": self.use_regex.isChecked(),
            "recursive": True,  # Always do recursive search
            "file_type": file_type,
            "file_extensions": selected_extensions,
            "filter_text": self.filter_input.text(),
            "paths": self._search_paths,
            "exclude_options": exclude_options,  # Add exclude options to the search options
        }

    def _update_algorithm_for_file_type(self, state: Optional[int] = None) -> None:
        """Remove redundant method as algorithm is dynamically determined."""
        pass

    def _on_regex_checkbox_changed(self, state: Qt.CheckState) -> None:
        """Remove redundant method as regex state is dynamically handled."""
        pass

    def set_search_paths(self, paths: list[str]) -> None:
        """set the search paths"""
        self._search_paths = paths

    def update_stats(self, text: str) -> None:
        """Update the statistics label with the given text

        Args:
            text: The text to display in the statistics label
        """
        self.stats_label.setText(text)

        # If this is a "Found X results" message, update the status label too
        if text.startswith("Found ") and " results" in text:
            self._on_search_complete()

    def add_result(
        self, mod_name: str, file_name: str, path: str, preview: str = ""
    ) -> None:
        """Add a search result to the table with improved performance and error handling."""
        try:
            # Batch insertion for better performance
            current_row = self.results_table.rowCount()
            batch_size = 10  # Increased batch size for efficiency

            if current_row % batch_size == 0:
                self.results_table.setSortingEnabled(False)
                self.results_table.setUpdatesEnabled(False)

            # Insert new row
            row = current_row
            self.results_table.insertRow(row)

            # Truncate preview intelligently
            max_preview_length = 1000
            if len(preview) > max_preview_length:
                cutoff = preview.rfind("\n", 0, max_preview_length)
                cutoff = (
                    cutoff if cutoff > max_preview_length // 2 else max_preview_length
                )
                preview = preview[:cutoff] + "\n... [Preview truncated]"

            # Create table items
            mod_item = QTableWidgetItem(mod_name)
            file_item = QTableWidgetItem(file_name)
            path_item = QTableWidgetItem(path)
            preview_item = QTableWidgetItem(preview)

            # Set tooltips and formatting
            mod_item.setToolTip(f"模组: {mod_name}")
            file_item.setToolTip(f"文件: {file_name}")
            path_item.setToolTip(f"路径: {path}")
            preview_item.setToolTip("双击打开文件")
            preview_item.setFont(QFont("Courier New", 9))
            preview_item.setFlags(preview_item.flags() ^ Qt.ItemFlag.ItemIsEditable)

            # Add items to table
            self.results_table.setItem(row, 0, mod_item)
            self.results_table.setItem(row, 1, file_item)
            self.results_table.setItem(row, 2, path_item)
            self.results_table.setItem(row, 3, preview_item)

            # Re-enable updates and sorting at batch boundaries
            if (
                current_row % batch_size == batch_size - 1
                or current_row == self.results_table.rowCount() - 1
            ):
                self.results_table.setUpdatesEnabled(True)
                self.results_table.setSortingEnabled(True)

        except Exception as e:
            logger.error(f"Error adding result: {e}")
            self.results_table.setUpdatesEnabled(True)

    def clear_results(self) -> None:
        """clear all results from the table"""
        self.results_table.setRowCount(0)

    def update_progress(self, current: int, total: int) -> None:
        """Update progress bar and related UI elements.

        Args:
            current (int): Current progress value.
            total (int): Maximum progress value.
        """

    def _show_recent_searches(self) -> None:
        """Show recent searches menu"""
        if not self._recent_searches:
            return

        menu = QMenu(self)

        # Add recent searches to menu
        for search in self._recent_searches:
            action = menu.addAction(search)
            action.triggered.connect(
                lambda checked=False, text=search: self._use_recent_search(text)
            )

        # Add a separator and clear action
        if self._recent_searches:
            menu.addSeparator()
            clear_action = menu.addAction("清除最近的搜索")
            clear_action.triggered.connect(self._clear_recent_searches)

        # Show menu below the button
        menu.exec(
            self.recent_searches_button.mapToGlobal(
                self.recent_searches_button.rect().bottomLeft()
            )
        )

    def _use_recent_search(self, text: str) -> None:
        """Use a recent search"""
        self.search_input.setText(text)

    def _clear_recent_searches(self) -> None:
        """Clear recent searches"""
        self._recent_searches.clear()
        self._save_recent_searches()

    def add_recent_search(self, search_text: str) -> None:
        """Add a search to recent searches"""
        if not search_text or search_text.isspace():
            return

        # Remove if already exists (to move it to the top)
        if search_text in self._recent_searches:
            self._recent_searches.remove(search_text)

        # Add to the beginning of the list
        self._recent_searches.insert(0, search_text)

        # Limit the number of recent searches
        if len(self._recent_searches) > self._max_recent_searches:
            self._recent_searches = self._recent_searches[: self._max_recent_searches]

        # Save recent searches
        self._save_recent_searches()

    def _save_recent_searches(self) -> None:
        """Save recent searches to recent_searches.json in the app storage folder."""
        app_info = AppInfo()
        recent_searches_file = app_info.app_storage_folder / "recent_searches.json"

        try:
            with open(recent_searches_file, "w", encoding="utf-8") as f:
                json.dump(self._recent_searches, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Failed to save recent searches: {e}")

    def _load_recent_searches(self) -> None:
        """Load recent searches from recent_searches.json in the app storage folder."""
        app_info = AppInfo()
        recent_searches_file = app_info.app_storage_folder / "recent_searches.json"

        if recent_searches_file.exists():
            try:
                with open(recent_searches_file, "r", encoding="utf-8") as f:
                    self._recent_searches = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load recent searches: {e}")

    def _on_filter_changed(self, text: str) -> None:
        """Handle filter text changes"""
        filter_text = text.lower()
        visible_rows = 0
        total_rows = self.results_table.rowCount()

        for row in range(total_rows):
            show_row = False
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(row, col)
                if item is not None and filter_text in item.text().lower():
                    show_row = True
                    break

            self.results_table.setRowHidden(row, not show_row)
            if show_row:
                visible_rows += 1

        # Update the stats label to show filter results
        if text:
            self.update_stats(f"过滤：{visible_rows} 个结果可见，共 {total_rows} 个结果")
        elif total_rows > 0:
            self.update_stats(f"找到 {total_rows} 个结果")
        else:
            self.update_stats("准备搜索")
