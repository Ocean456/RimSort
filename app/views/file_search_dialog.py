from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal
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
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


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
        self._search_paths: List[str] = []

        # create main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # search section
        search_section = QWidget()
        search_layout = QVBoxLayout(search_section)
        search_layout.setContentsMargins(0, 0, 0, 0)

        # search input row
        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "将显示包含此文本的文件"
        )
        search_input_layout.addWidget(self.search_input)

        self.search_button = QPushButton("搜索")
        self.stop_button = QPushButton("停止")
        self.stop_button.setEnabled(False)
        search_input_layout.addWidget(self.search_button)
        search_input_layout.addWidget(self.stop_button)
        search_layout.addLayout(search_input_layout)

        # options row
        options_layout = QHBoxLayout()

        # search scope and algorithm
        scope_layout = QVBoxLayout()
        scope_label = QLabel("搜索：")
        self.search_scope = QComboBox()
        self.search_scope.addItem("启用的模组", "active mods")
        self.search_scope.addItem("未启用的模组", "not active mods")
        self.search_scope.addItem("所有模组", "all mods")
        self.search_scope.addItem("配置文件夹", "configs folder")
        scope_layout.addWidget(scope_label)
        scope_layout.addWidget(self.search_scope)
        options_layout.addLayout(scope_layout)

        algo_layout = QVBoxLayout()
        algo_label = QLabel("搜索方法：")
        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItem("简单搜索 (适用于小型模组合集)", "simple search (good for small mod collections)")
        self.algorithm_selector.addItem("并行搜索 (适用于大型模组合集)", "parallel search (for large mod collections)")
        algo_layout.addWidget(algo_label)
        algo_layout.addWidget(self.algorithm_selector)
        options_layout.addLayout(algo_layout)

        # checkboxes in horizontal layout
        checks_layout = QVBoxLayout()
        checks_label = QLabel("选项：")
        checks_box_layout = QHBoxLayout()
        self.case_sensitive = QCheckBox("区分大小写")
        self.skip_translations = QCheckBox("跳过翻译")
        self.xml_only = QCheckBox("仅 xml 文件")
        checks_layout.addWidget(checks_label)
        checks_box_layout.addWidget(self.case_sensitive)
        checks_box_layout.addWidget(self.skip_translations)
        checks_box_layout.addWidget(self.xml_only)
        checks_layout.addLayout(checks_box_layout)
        options_layout.addLayout(checks_layout)

        search_layout.addLayout(options_layout)
        layout.addWidget(search_section)

        # progress section
        progress_section = QWidget()
        progress_layout = QVBoxLayout(progress_section)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(5)  # reduce spacing

        # progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("搜索中... %p% (%v/%m 文件)")
        progress_layout.addWidget(self.progress_bar)

        # statistics label
        self.stats_label = QLabel("准备好搜索了吗")
        progress_layout.addWidget(self.stats_label)

        layout.addWidget(progress_section)

        # filter section
        filter_section = QWidget()
        filter_layout = QVBoxLayout(filter_section)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(5)  # reduce spacing

        filter_label = QLabel("筛选结果:")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText(
            "只显示包含指定文本的路径（适用于路径、文件名和mod名）"
        )
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input)

        layout.addWidget(filter_section)

        # results section
        results_section = QWidget()
        results_layout = QVBoxLayout(results_section)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(5)  # reduce spacing

        results_label = QLabel("结果:")
        results_layout.addWidget(results_label)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)  # added column for preview
        self.results_table.setHorizontalHeaderLabels(
            ["模组名称", "文件名", "路径", "预览"]
        )

        # stretch columns to content
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        # enable context menu
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self._show_context_menu)

        results_layout.addWidget(self.results_table)
        layout.addWidget(results_section)

        # set minimum size and adjust margins
        self.resize(1200, 800)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)  # reduce overall spacing

    def _show_context_menu(self, pos: Any) -> None:
        """show context menu for results table"""
        menu = QMenu()

        open_file = menu.addAction("打开文件")
        open_folder = menu.addAction("打开所在文件夹")
        copy_path = menu.addAction("复制路径")

        # get selected item
        item = self.results_table.itemAt(pos)
        if item is None:
            return

        row = item.row()
        path_item = self.results_table.item(row, 2)
        if path_item is None:
            return

        path = path_item.text()

        # connect actions
        open_file.triggered.connect(lambda: self._open_file(path))
        open_folder.triggered.connect(lambda: self._open_folder(path))
        copy_path.triggered.connect(lambda: self._copy_path(path))

        menu.exec(self.results_table.viewport().mapToGlobal(pos))

    def _open_file(self, path: str) -> None:
        """open file in default application"""
        from app.utils.generic import platform_specific_open

        platform_specific_open(path)

    def _open_folder(self, path: str) -> None:
        """open containing folder"""
        import os

        from app.utils.generic import platform_specific_open

        platform_specific_open(os.path.dirname(path))

    def _copy_path(self, path: str) -> None:
        """copy path to clipboard"""
        QApplication.clipboard().setText(path)

    def get_search_options(self) -> Dict[str, Any]:
        """get current search options as a dictionary"""
        return {
            "scope": self.search_scope.currentData(),
            "algorithm": self.algorithm_selector.currentData().split(" (")[0],
            "case_sensitive": self.case_sensitive.isChecked(),
            "skip_translations": self.skip_translations.isChecked(),
            "xml_only": self.xml_only.isChecked(),
            "filter_text": self.filter_input.text(),
            "paths": self._search_paths,
        }

    def set_search_paths(self, paths: List[str]) -> None:
        """set the search paths"""
        self._search_paths = paths

    def add_result(
        self, mod_name: str, file_name: str, path: str, preview: str = ""
    ) -> None:
        """add a search result to the table"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        self.results_table.setItem(row, 0, QTableWidgetItem(mod_name))
        self.results_table.setItem(row, 1, QTableWidgetItem(file_name))
        self.results_table.setItem(row, 2, QTableWidgetItem(path))
        self.results_table.setItem(row, 3, QTableWidgetItem(preview))

    def clear_results(self) -> None:
        """clear all results from the table"""
        self.results_table.setRowCount(0)

    def update_progress(self, current: int, total: int) -> None:
        """update progress bar"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def update_stats(self, stats: str) -> None:
        """update statistics label"""
        self.stats_label.setText(stats)

    def _on_filter_changed(self, text: str) -> None:
        """handle filter text changes"""
        filter_text = text.lower()
        for row in range(self.results_table.rowCount()):
            show_row = False
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(row, col)
                if item is not None and filter_text in item.text().lower():
                    show_row = True
                    break
            self.results_table.setRowHidden(row, not show_row)
