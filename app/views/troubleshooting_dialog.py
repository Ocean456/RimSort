from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class TroubleshootingDialog(QDialog):
    """
    Dialog window for troubleshooting options including game file recovery,
    mod configuration management, and Steam utilities.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle("疑难解答")

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Style constants
        self._group_box_style = """
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid blue;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: blue;
            }
        """
        self._button_style_base = """
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                min-width: 160px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """
        self._button_style_danger = """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                min-width: 160px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """

        # Game files recovery section
        group_box = QGroupBox("游戏文件恢复")
        group_box.setStyleSheet(self._group_box_style)
        main_layout.addWidget(group_box)
        group_layout = QVBoxLayout()
        group_box.setLayout(group_layout)
        group_layout.setSpacing(8)
        group_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Warning label with icon
        warning_layout = QVBoxLayout()
        warning_label = QLabel(
            "⚠️ 警告：这些操作将永久删除选定的文件！"
        )
        warning_label.setStyleSheet("color: red; font-size: 20px; font-weight: bold;")
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_layout.addWidget(warning_label)
        warning_layout.addStretch()
        group_layout.addLayout(warning_layout)

        # Info label
        info_label = QLabel(
            "如果您在游戏中遇到问题，可以尝试以下恢复选项。 "
            "Steam 将在下次启动时自动重新下载已删除的文件。"
        )
        info_label.setStyleSheet("color: yellow; font-size: 12px; padding: 5px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_layout.addWidget(info_label)

        # Checkboxes for integrity options with tooltips
        self.integrity_delete_game_files = QCheckBox(
            "重置游戏文件（保留本地模组，删除并重新下载游戏文件）"
        )
        self.integrity_delete_game_files.setStyleSheet("padding: 5px;")
        self.integrity_delete_game_files.setToolTip(
            "Deletes and redownloads game files but keeps your local mods intact."
        )
        group_layout.addWidget(self.integrity_delete_game_files)

        self.integrity_delete_steam_mods = QCheckBox(
            "重置Steam创意工坊模组（删除并重新下载所有Steam模组）"
        )
        self.integrity_delete_steam_mods.setStyleSheet("padding: 5px;")
        self.integrity_delete_steam_mods.setToolTip(
            "Deletes all Steam Workshop mods and triggers redownload."
        )
        group_layout.addWidget(self.integrity_delete_steam_mods)

        self.integrity_delete_mod_configs = QCheckBox(
            "重置模组配置（保留ModsConfig.xml和Prefs.xml）"
        )
        self.integrity_delete_mod_configs.setStyleSheet("padding: 5px;")
        self.integrity_delete_mod_configs.setToolTip(
            "Deletes mod configuration files except ModsConfig.xml and Prefs.xml."
        )
        group_layout.addWidget(self.integrity_delete_mod_configs)

        self.integrity_delete_game_configs = QCheckBox(
            "重置游戏配置（ModsConfig.xml, Prefs.xml, KeyPrefs.xml）*"
        )
        self.integrity_delete_game_configs.setStyleSheet("padding: 5px;")
        self.integrity_delete_game_configs.setToolTip(
            "Deletes game configuration files including ModsConfig.xml, Prefs.xml, and KeyPrefs.xml."
        )
        group_layout.addWidget(self.integrity_delete_game_configs)

        # Note about ModsConfig.xml
        note_label = QLabel(
            "After resetting game configurations, launch the game directly through Steam to regenerate ModsConfig.xml, then restart RimSort."
        )
        note_label.setStyleSheet("color: yellow; font-size: 12px; padding: 5px;")
        note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_layout.addWidget(note_label)

        # Buttons layout
        button_layout: QHBoxLayout = QHBoxLayout()
        group_layout.addLayout(button_layout)

        # Apply button
        self.integrity_apply_button = QPushButton("Apply Recovery")
        self.integrity_apply_button.setStyleSheet(self._button_style_danger)
        self.integrity_apply_button.setShortcut("Ctrl+R")
        self.integrity_apply_button.setToolTip("Apply the selected recovery options")

        # Cancel button
        self.integrity_cancel_button = QPushButton("Cancel")
        self.integrity_cancel_button.setStyleSheet(self._button_style_base)
        self.integrity_cancel_button.setShortcut("Ctrl+C")
        self.integrity_cancel_button.setToolTip("Cancel and clear selections")

        # Add Apply and Cancel buttons to layout
        button_layout.addWidget(self.integrity_apply_button)
        button_layout.addWidget(self.integrity_cancel_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Mod configuration options section
        mod_config_group = QGroupBox("Mod Configuration Options")
        mod_config_group.setStyleSheet(self._group_box_style)
        main_layout.addWidget(mod_config_group)
        mod_config_layout = QVBoxLayout()
        mod_config_group.setLayout(mod_config_layout)
        mod_config_layout.setSpacing(8)

        # Info label for mod configuration
        mod_config_info = QLabel(
            "管理您的模组配置和加载顺序。这些选项可帮助您组织和分享模组设置。"
        )
        mod_config_info.setStyleSheet(
            "color: yellow; font-size: 15px; margin-bottom: 5px;"
        )
        mod_config_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mod_config_layout.addWidget(mod_config_info)

        # Mod list import/export section
        mod_list_layout = QHBoxLayout()
        mod_config_layout.addLayout(mod_list_layout)
        mod_list_layout.setSpacing(8)

        # Export mod list vertical layout
        export_mod_layout = QVBoxLayout()
        mod_list_layout.addLayout(export_mod_layout)

        export_mod_list_desc = QLabel(
            "Save your current mod list to a .xml file to share with others."
        )
        export_mod_list_desc.setStyleSheet(
            "color: white; padding-left: 0px; margin-top: 5px; font-size: 15px;"
        )
        export_mod_list_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        export_mod_layout.addWidget(export_mod_list_desc)

        self.mod_export_list_button = QPushButton("导出模组列表")
        self.mod_export_list_button.setStyleSheet(self._button_style_base)
        self.mod_export_list_button.setToolTip("Export your current mod list to a file")
        export_mod_layout.addWidget(self.mod_export_list_button)

        # Import mod list vertical layout
        import_mod_layout = QVBoxLayout()
        mod_list_layout.addLayout(import_mod_layout)

        import_mod_list_desc = QLabel(
            "Import a mod list in .xml format from another player"
        )
        import_mod_list_desc.setStyleSheet(
            "color: white; padding-left: 0px; margin-top: 5px; font-size: 15px;"
        )
        import_mod_list_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        import_mod_layout.addWidget(import_mod_list_desc)

        self.mod_import_list_button = QPushButton("Import Mod List")
        self.mod_import_list_button.setStyleSheet(self._button_style_base)
        self.mod_import_list_button.setToolTip("Import a mod list from a file")
        import_mod_layout.addWidget(self.mod_import_list_button)

        # Clear mods section (in red)
        clear_mods_layout = QVBoxLayout()
        clear_mods_layout.setSpacing(8)
        mod_config_layout.addLayout(clear_mods_layout)

        clear_mods_desc = QLabel(
            "⚠️ 警告：此操作将删除您的Mods文件夹中的所有Mod，并重置为原版状态"
        )
        clear_mods_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        clear_mods_desc.setStyleSheet(
            "color: #e74c3c; font-weight: bold; font-size: 20px; margin-top: 5px;"
        )
        clear_mods_layout.addWidget(clear_mods_desc)

        self.clear_mods_button = QPushButton("Clear Mods")
        self.clear_mods_button.setStyleSheet(self._button_style_danger)
        self.clear_mods_button.setMinimumWidth(160)
        self.clear_mods_button.setToolTip("Delete all mods and reset to vanilla state")
        clear_mods_layout.addWidget(
            self.clear_mods_button, alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Steam tools section
        steam_group = QGroupBox("Steam Utilities")
        steam_group.setStyleSheet(self._group_box_style)
        main_layout.addWidget(steam_group)
        steam_layout = QHBoxLayout()
        steam_group.setLayout(steam_layout)
        steam_group.setAlignment(Qt.AlignmentFlag.AlignCenter)
        steam_layout.setSpacing(8)

        # Initialize steam buttons
        self.steam_clear_cache_button = QPushButton("🔄 清除下载缓存")
        self.steam_verify_game_button = QPushButton("✓ 验证游戏文件")
        self.steam_repair_library_button = QPushButton("🔧 修复Steam库")

        # Steam buttons with icons and descriptions
        steam_buttons = [
            (
                self.steam_clear_cache_button,
                "删除 Steam 下载缓存文件夹以解决下载问题",
            ),
            (
                self.steam_verify_game_button,
                "检查并修复 RimWorld 游戏文件",
            ),
            (
                self.steam_repair_library_button,
                "验证所有已安装 Steam 游戏的完整性",
            ),
        ]

        button_style_steam = """
            QPushButton {
                text-align: left;
                padding: 8px;
                border-radius: 3px;
                background-color: #4a90e2;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """

        for button, description in steam_buttons:
            button_container = QVBoxLayout()
            button_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button.setStyleSheet(button_style_steam)
            button.setToolTip(description)
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: white; font-size: 12px; padding: 5px 8px;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button_container.addWidget(button)
            button_container.addWidget(desc_label)
            steam_layout.addLayout(button_container)

        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)
        button_layout.addStretch()
