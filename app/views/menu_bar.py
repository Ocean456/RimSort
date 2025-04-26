from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenu, QMenuBar

from app.utils.system_info import SystemInfo


class MenuBar(QObject):
    def __init__(self, menu_bar: QMenuBar) -> None:
        """
        Initialize the MenuBar object.

        Args:
            menu_bar (QMenuBar): The menu bar to which the menus and actions will be added.
        """
        super().__init__()

        self.menu_bar: QMenuBar = menu_bar

        # Declare actions and submenus as class variables
        # to be used by menu_bar_controller
        self.settings_action: QAction
        self.quit_action: QAction
        self.open_mod_list_action: QAction
        self.save_mod_list_action: QAction
        self.import_from_rentry_action: QAction
        self.import_from_workshop_collection_action: QAction
        self.export_to_clipboard_action: QAction
        self.export_to_rentry_action: QAction
        self.upload_rimsort_log_action: QAction
        self.upload_rimsort_old_log_action: QAction
        self.upload_rimworld_log_action: QAction
        self.open_app_directory_action: QAction
        self.open_settings_directory_action: QAction
        self.open_rimsort_logs_directory_action: QAction
        self.open_rimworld_directory_action: QAction
        self.open_rimworld_config_directory_action: QAction
        self.open_rimworld_logs_directory_action: QAction
        self.open_local_mods_directory_action: QAction
        self.open_steam_mods_directory_action: QAction
        self.cut_action: QAction
        self.copy_action: QAction
        self.paste_action: QAction
        self.rule_editor_action: QAction
        self.reset_all_warnings_action: QAction
        self.add_git_mod_action: QAction
        self.browse_workshop_action: QAction
        self.update_workshop_mods_action: QAction
        self.backup_instance_action: QAction
        self.restore_instance_action: QAction
        self.clone_instance_action: QAction
        self.create_instance_action: QAction
        self.delete_instance_action: QAction
        self.optimize_textures_action: QAction
        self.delete_dds_textures_action: QAction
        self.wiki_action: QAction
        self.check_for_updates_action: QAction
        self.check_for_updates_on_startup_action: QAction
        self.file_search_action: QAction

        self.import_submenu: QMenu
        self.export_submenu: QMenu
        self.upload_submenu: QMenu
        self.shortcuts_submenu: QMenu
        self.instances_submenu: QMenu

        self._create_menu_bar()

    def _add_action(
        self,
        menu: QMenu,
        title: str,
        shortcut: str | None = None,
        checkable: bool = False,
        role: QAction.MenuRole | None = None,
    ) -> QAction:
        """
        Add an action to a menu.

        Args:
            menu (QMenu): The menu to which the action will be added.
            title (str): The title of the action.
            shortcut (str | None = None): The keyboard shortcut for the action.
            checkable (bool = False): Whether the action is checkable.
            role (QAction.MenuRole | None, optional): The menu role of the action. Defaults to None.
        Returns:
            QAction: The created action.
        """
        action = QAction(title, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        if checkable:
            action.setCheckable(True)
        if role:
            action.setMenuRole(role)
        menu.addAction(action)
        return action

    def _create_file_menu(self) -> QMenu:
        """
        Create the "File" menu and add its actions and submenus.

        Returns:
            QMenu: The created "File" menu.
        """
        file_menu = self.menu_bar.addMenu("文件")
        self.open_mod_list_action = self._add_action(
            file_menu, "打开模组列表", "Ctrl+O"
        )
        file_menu.addSeparator()
        self.save_mod_list_action = self._add_action(
            file_menu, "保存模组列表", "Ctrl+Shift+S"
        )
        file_menu.addSeparator()
        self.import_submenu = QMenu("导入")
        file_menu.addMenu(self.import_submenu)
        self.import_from_rentry_action = self._add_action(
            self.import_submenu, "从 Rentry.co 导入"
        )
        self.import_from_workshop_collection_action = self._add_action(
            self.import_submenu, "从 创意工坊 导入"
        )
        self.export_submenu = QMenu("导出")
        file_menu.addMenu(self.export_submenu)
        self.export_to_clipboard_action = self._add_action(
            self.export_submenu, "导出到 剪切板"
        )
        self.export_to_rentry_action = self._add_action(
            self.export_submenu, "导出到 Rentry.co"
        )
        file_menu.addSeparator()
        self.file_search_action = self._add_action(
            file_menu, "文件搜索", "Ctrl+Shift+F"
        )
        file_menu.addSeparator()
        self.upload_submenu = QMenu("上传日志")
        file_menu.addMenu(self.upload_submenu)
        self.upload_rimsort_log_action = self._add_action(
            self.upload_submenu, "RimSort.log"
        )
        self.upload_rimsort_old_log_action = self._add_action(
            self.upload_submenu, "RimSort.old.log"
        )
        self.upload_rimworld_log_action = self._add_action(
            self.upload_submenu, "RimWorld Player.log"
        )
        file_menu.addSeparator()
        self.shortcuts_submenu = QMenu("打开")
        file_menu.addMenu(self.shortcuts_submenu)
        # Add submenu under Shortcuts
        self.rimsort_shortcuts_submenu = QMenu("RimSort")
        self.shortcuts_submenu.addMenu(self.rimsort_shortcuts_submenu)
        self.rimworld_shortcuts_submenu = QMenu("RimWorld")
        self.shortcuts_submenu.addMenu(self.rimworld_shortcuts_submenu)
        # Add actions to RimSort submenu
        self.open_app_directory_action = self._add_action(
            self.rimsort_shortcuts_submenu, "根目录"
        )
        self.open_settings_directory_action = self._add_action(
            self.rimsort_shortcuts_submenu, "配置目录"
        )
        self.open_rimsort_logs_directory_action = self._add_action(
            self.rimsort_shortcuts_submenu, "日志目录"
        )
        # Add action to RimWorld submenu
        self.open_rimworld_directory_action = self._add_action(
            self.rimworld_shortcuts_submenu, "根目录"
        )
        self.open_rimworld_config_directory_action = self._add_action(
            self.rimworld_shortcuts_submenu, "配置目录"
        )
        self.open_rimworld_logs_directory_action = self._add_action(
            self.rimworld_shortcuts_submenu, "日志目录"
        )
        self.open_local_mods_directory_action = self._add_action(
            self.rimworld_shortcuts_submenu, "本地模组目录"
        )
        self.open_steam_mods_directory_action = self._add_action(
            self.rimworld_shortcuts_submenu, "Steam模组目录"
        )

        if SystemInfo().operating_system != SystemInfo.OperatingSystem.MACOS:
            file_menu.addSeparator()
            self.settings_action = self._add_action(file_menu, "设置", "Ctrl+,")
            file_menu.addSeparator()
            self.quit_action = self._add_action(file_menu, "退出", "Ctrl+Q")
        return file_menu

    def _create_edit_menu(self) -> QMenu:
        """
        Create the "Edit" menu and add its actions.

        Returns:
            QMenu: The created "Edit" menu.
        """
        edit_menu = self.menu_bar.addMenu("编辑")
        self.cut_action = self._add_action(edit_menu, "剪切", "Ctrl+X")
        self.copy_action = self._add_action(edit_menu, "复制", "Ctrl+C")
        self.paste_action = self._add_action(edit_menu, "粘贴", "Ctrl+V")
        edit_menu.addSeparator()
        self.rule_editor_action = self._add_action(edit_menu, "规则编辑器")
        self.reset_all_warnings_action = self._add_action(
            edit_menu, "重置警告状态"
        )
        return edit_menu

    def _create_download_menu(self) -> QMenu:
        """
        Create the "Download" menu and add its actions.

        Returns:
            QMenu: The created "Download" menu.
        """
        download_menu = self.menu_bar.addMenu("下载")
        self.add_git_mod_action = self._add_action(download_menu, "添加 Git 模组")
        download_menu.addSeparator()
        self.browse_workshop_action = self._add_action(download_menu, "浏览创意工坊")
        self.update_workshop_mods_action = self._add_action(
            download_menu, "更新创意工坊模组"
        )
        return download_menu

    def _create_instances_menu(self) -> QMenu:
        """
        Create the "Instances" menu and add its actions and submenus.

        Returns:
            QMenu: The created "Instances" menu.
        """
        instances_menu = self.menu_bar.addMenu("实例")
        self.instances_submenu = QMenu('当前：默认')
        instances_menu.addMenu(self.instances_submenu)
        instances_menu.addSeparator()
        self.backup_instance_action = self._add_action(
            instances_menu, "备份实例"
        )
        self.restore_instance_action = self._add_action(
            instances_menu, "恢复实例"
        )
        instances_menu.addSeparator()
        self.clone_instance_action = self._add_action(instances_menu, "克隆实例")
        self.create_instance_action = self._add_action(
            instances_menu, "创建实例"
        )
        self.delete_instance_action = self._add_action(
            instances_menu, "删除实例"
        )
        return instances_menu

    def _create_texture_menu(self) -> QMenu:
        """
        Create the "Textures" menu and add its actions.

        Returns:
            QMenu: The created "Textures" menu.
        """
        texture_menu = self.menu_bar.addMenu("纹理")
        self.optimize_textures_action = self._add_action(
            texture_menu, "优化纹理"
        )
        texture_menu.addSeparator()
        self.delete_dds_textures_action = self._add_action(
            texture_menu, "删除 .dds 纹理"
        )
        return texture_menu

    def _create_help_menu(self) -> QMenu:
        """
        Create the "Help" menu and add its actions.

        Returns:
            QMenu: The created "Help" menu.
        """
        help_menu = self.menu_bar.addMenu("帮助")
        self.wiki_action = self._add_action(help_menu, "RimSort Wiki…")
        help_menu.addSeparator()
        # TODO: updates not implemented yet
        # self.check_for_updates_action = self._add_action(
        #     help_menu, "Check for Updates…"
        # )
        # self.check_for_updates_on_startup_action = self._add_action(
        #     help_menu, "Check for Updates on Startup", checkable=True
        # )
        # help_menu.addSeparator()
        return help_menu

    def _create_menu_bar(self) -> None:
        """
        Create the menu bar. On macOS, include the app menu.
        """
        if SystemInfo().operating_system == SystemInfo.OperatingSystem.MACOS:
            app_menu = self.menu_bar.addMenu("应用程序名称")
            app_menu.addSeparator()
            self.settings_action = self._add_action(
                app_menu,
                "设置",
                shortcut="Ctrl+,",
                role=QAction.MenuRole.ApplicationSpecificRole,
            )
            app_menu.addSeparator()
            self.quit_action = self._add_action(app_menu, "退出")
        self._create_file_menu()
        self._create_edit_menu()
        self._create_download_menu()
        self._create_instances_menu()
        self._create_texture_menu()
        self._create_help_menu()
