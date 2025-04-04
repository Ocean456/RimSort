import os
import platform
from functools import partial
from typing import Any

from loguru import logger
from PySide6.QtCore import QPoint, QSize, Qt, QUrl, Signal
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from app.models.image_label import ImageLabel
from app.utils.app_info import AppInfo
from app.utils.generic import extract_page_title_steam_browser
from app.utils.metadata import MetadataManager
from app.utils.steam.webapi.wrapper import (
    ISteamRemoteStorage_GetCollectionDetails,
    ISteamRemoteStorage_GetPublishedFileDetails,
)
from app.views.dialogue import show_warning


class SteamBrowser(QWidget):
    """
    A generic panel used to browse Workshop content - downloader included
    """

    steamcmd_downloader_signal = Signal(list)
    steamworks_subscription_signal = Signal(list)

    def __init__(self, startpage: str, metadata_manager: MetadataManager):
        super().__init__()
        logger.debug("Initializing SteamBrowser")

        # store metadata manager reference so we can use it to check if mods are installed
        self.metadata_manager = metadata_manager

        # This is used to fix issue described here on non-Windows platform:
        # https://doc.qt.io/qt-6/qtwebengine-platform-notes.html#sandboxing-support
        if platform.system() != "Windows":
            logger.info("Setting QTWEBENGINE_DISABLE_SANDBOX for non-Windows platform")
            os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

        # VARIABLES
        self.current_html = ""
        self.current_title = "RimSort - Steam Browser"
        self.current_url = startpage

        # TODO: Are these actually ever assigned?
        self.downloader_list_mods_tracking: list[str] = []
        self.downloader_list_dupe_tracking: dict[str, Any] = {}
        self.startpage = QUrl(startpage)

        self.searchtext_string = "&searchtext="
        self.url_prefix_steam = "https://steamcommunity.com"
        self.url_prefix_sharedfiles = (
            "https://steamcommunity.com/sharedfiles/filedetails/?id="
        )
        self.url_prefix_workshop = (
            "https://steamcommunity.com/workshop/filedetails/?id="
        )

        # LAYOUTS
        self.window_layout = QHBoxLayout()
        self.browser_layout = QVBoxLayout()
        self.downloader_layout = QVBoxLayout()

        # DOWNLOADER WIDGETS
        self.downloader_label = QLabel("Mod下载器")
        self.downloader_label.setObjectName("browserPaneldownloader_label")
        self.downloader_list = QListWidget()
        self.downloader_list.setFixedWidth(200)
        self.downloader_list.setItemAlignment(Qt.AlignmentFlag.AlignCenter)
        self.downloader_list.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.downloader_list.customContextMenuRequested.connect(
            self._downloader_item_contextmenu_event
        )
        self.clear_list_button = QPushButton("清空列表")
        self.clear_list_button.setObjectName("browserPanelClearList")
        self.clear_list_button.clicked.connect(self._clear_downloader_list)
        self.download_steamcmd_button = QPushButton("下载Mod（SteamCMD）")
        self.download_steamcmd_button.clicked.connect(
            partial(
                self.steamcmd_downloader_signal.emit, self.downloader_list_mods_tracking
            )
        )
        self.download_steamworks_button = QPushButton("下载Mod（Steam）")
        self.download_steamworks_button.clicked.connect(
            self._subscribe_to_mods_from_list
        )

        # BROWSER WIDGETS
        # "Loading..." placeholder
        self.web_view_loading_placeholder = ImageLabel()
        self.web_view_loading_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.web_view_loading_placeholder.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.web_view_loading_placeholder.setPixmap(
            QPixmap(
                str(AppInfo().theme_data_folder / "default-icons" / "AppIcon_b.png")
            )
        )
        # WebEngineView
        self.web_view = QWebEngineView()
        self.web_view.loadStarted.connect(self._web_view_load_started)
        self.web_view.loadProgress.connect(self._web_view_load_progress)
        self.web_view.loadFinished.connect(self._web_view_load_finished)
        self.web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.web_view.load(self.startpage)

        QWebEngineProfile.defaultProfile().setHttpAcceptLanguage("zh-CN")

        # Location box
        self.location = QLineEdit()
        self.location.setSizePolicy(
            QSizePolicy.Policy.Expanding, self.location.sizePolicy().verticalPolicy()
        )
        self.location.setText(self.startpage.url())
        self.location.returnPressed.connect(self.__browse_to_location)

        # Nav bar
        self.add_to_list_button = QAction("添加到列表")
        self.add_to_list_button.triggered.connect(self._add_collection_or_mod_to_list)
        self.nav_bar = QToolBar()
        self.nav_bar.setObjectName("browserPanelnav_bar")
        self.nav_bar.addAction(self.web_view.pageAction(QWebEnginePage.WebAction.Back))
        self.nav_bar.addAction(
            self.web_view.pageAction(QWebEnginePage.WebAction.Forward)
        )
        self.nav_bar.addAction(self.web_view.pageAction(QWebEnginePage.WebAction.Stop))
        self.nav_bar.addAction(
            self.web_view.pageAction(QWebEnginePage.WebAction.Reload)
        )
        # self.nav_bar.addSeparator()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)

        # Build the downloader layout
        self.downloader_layout.addWidget(self.downloader_label)
        self.downloader_layout.addWidget(self.downloader_list)
        self.downloader_layout.addWidget(self.clear_list_button)
        self.downloader_layout.addWidget(self.download_steamcmd_button)
        self.downloader_layout.addWidget(self.download_steamworks_button)

        # Build the browser layout
        self.browser_layout.addWidget(self.location)
        self.browser_layout.addWidget(self.nav_bar)
        self.browser_layout.addWidget(self.progress_bar)
        self.browser_layout.addWidget(self.web_view_loading_placeholder)
        self.browser_layout.addWidget(self.web_view)

        # Add our layouts to the main layout
        self.window_layout.addLayout(self.downloader_layout)
        self.window_layout.addLayout(self.browser_layout)

        self.setObjectName("browserPanel")
        # Put it all together
        self.setWindowTitle(self.current_title)
        self.setLayout(self.window_layout)
        self.setMinimumSize(QSize(800, 600))

    def __browse_to_location(self) -> None:
        url = QUrl(self.location.text())
        logger.debug(f"Browsing to: {url.url()}")
        self.web_view.load(url)

    def _add_collection_or_mod_to_list(self) -> None:
        # Ascertain the pfid depending on the url prefix
        if self.url_prefix_sharedfiles in self.current_url:
            publishedfileid = self.current_url.split(self.url_prefix_sharedfiles, 1)[1]
        elif self.url_prefix_workshop in self.current_url:
            publishedfileid = self.current_url.split(self.url_prefix_workshop, 1)[1]
        else:
            logger.error(
                f"Unable to parse publishedfileid from url: {self.current_url}"
            )
            show_warning(
                title="未找到文件ID",
                text="无法从URL解析文件ID",
                information=f"Url地址： {self.current_url}",
            )
            return None
        # If there is extra data after the PFID, strip it
        if self.searchtext_string in publishedfileid:
            publishedfileid = publishedfileid.split(self.searchtext_string)[0]
        # Handle collection vs individual mod
        if "collectionItemDetails" not in self.current_html:
            self._add_mod_to_list(publishedfileid)
        else:
            # Use WebAPI to get titles for all the mods
            collection_mods_pfid_to_title = self.__compile_collection_datas(
                publishedfileid
            )
            if len(collection_mods_pfid_to_title) > 0:
                # ask user whether to add all mods or only missing ones
                from app.views.dialogue import show_dialogue_conditional

                answer = show_dialogue_conditional(
                    title="添加合集",
                    text="请选择添加合集的方式",
                    information="您可以选择添加合集所有模组或仅添加未安装模组",
                    button_text_override=["添加所有模组", "添加缺失模组"],
                )

                if answer == "添加所有模组":
                    # add all mods
                    for pfid, title in collection_mods_pfid_to_title.items():
                        self._add_mod_to_list(publishedfileid=pfid, title=title)
                elif answer == "添加缺失模组":
                    # add only mods that aren't installed
                    for pfid, title in collection_mods_pfid_to_title.items():
                        if not self._is_mod_installed(pfid):
                            self._add_mod_to_list(publishedfileid=pfid, title=title)
            else:
                logger.warning(
                    "Empty list of mods returned, unable to add collection to list!"
                )
                show_warning(
                    title="SteamCMD downloader",
                    text="返回的模组列表为空，无法将合集添加至列表！",
                    information="如需反馈问题，请前往 GitHub Issues 页面 或 Rocketman/CAI Discord 服务器的 #rimsort-testing 频道 联系我们。",
                )
        if len(self.downloader_list_dupe_tracking.keys()) > 0:
            # Build a report from our dict
            dupe_report = ""
            for pfid, name in self.downloader_list_dupe_tracking.items():
                dupe_report = dupe_report + f"{name} | {pfid}\n"
            # Notify the user
            show_warning(
                title="SteamCMD downloader",
                text="当前模组已存在于您的下载列表中！",
                information="已跳过以下已存在于下载列表中的模组！",
                details=dupe_report,
            )
            self.downloader_list_dupe_tracking = {}

    def __compile_collection_datas(self, publishedfileid: str) -> dict[str, Any]:
        collection_mods_pfid_to_title: dict[str, Any] = {}
        collection_webapi_result = ISteamRemoteStorage_GetCollectionDetails(
            [publishedfileid]
        )
        collection_pfids = []

        if collection_webapi_result is not None and len(collection_webapi_result) > 0:
            for mod in collection_webapi_result[0]["children"]:
                if mod.get("publishedfileid"):
                    collection_pfids.append(mod["publishedfileid"])
            if len(collection_pfids) > 0:
                collection_mods_webapi_response = (
                    ISteamRemoteStorage_GetPublishedFileDetails(collection_pfids)
                )
            else:
                return collection_mods_pfid_to_title

            if collection_mods_webapi_response is None:
                return collection_mods_pfid_to_title

            for metadata in collection_mods_webapi_response:
                # Retrieve the published mod's title from the response
                pfid = metadata["publishedfileid"]
                if "title" in metadata:
                    collection_mods_pfid_to_title[pfid] = metadata["title"]
                else:
                    collection_mods_pfid_to_title[pfid] = metadata["publishedfileid"]
        return collection_mods_pfid_to_title

    def _add_mod_to_list(
        self,
        publishedfileid: str,
        title: str | None = None,
    ) -> None:
        # Try to extract the mod name from the page title, fallback to current_title
        extracted_page_title = extract_page_title_steam_browser(self.current_title)
        page_title = (
            extracted_page_title if extracted_page_title else self.current_title
        )
        # Check if the mod is already in the list
        if publishedfileid not in self.downloader_list_mods_tracking:
            # Add pfid to tracking list
            logger.debug(f"Tracking PublishedFileId for download: {publishedfileid}")
            self.downloader_list_mods_tracking.append(publishedfileid)
            # Create our list item
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, publishedfileid)
            # Set list item label
            if not title:  # If title wasn't passed, get it from the web_view title
                label = QLabel(page_title)
                item.setToolTip(f"{label.text()}\n--> {self.current_url}")
            else:  # If the title passed, use it
                label = QLabel(title)
                item.setToolTip(
                    f"{label.text()}\n--> {self.url_prefix_sharedfiles}{publishedfileid}"
                )
            label.setObjectName("ListItemLabel")
            # Set the size hint of the item to be the size of the label
            item.setSizeHint(label.sizeHint())
            self.downloader_list.addItem(item)
            self.downloader_list.setItemWidget(item, label)
        else:
            logger.debug(
                f"Tried to add duplicate PFID to downloader list: {publishedfileid}"
            )
            if publishedfileid not in self.downloader_list_dupe_tracking.keys():
                if not title:
                    self.downloader_list_dupe_tracking[publishedfileid] = page_title
                else:
                    self.downloader_list_dupe_tracking[publishedfileid] = title

    def _clear_downloader_list(self) -> None:
        self.downloader_list.clear()
        self.downloader_list_mods_tracking.clear()
        self.downloader_list_dupe_tracking.clear()

    def _downloader_item_contextmenu_event(self, point: QPoint) -> None:
        context_item = self.downloader_list.itemAt(point)

        if context_item:  # Check if the right-clicked point corresponds to an item
            context_menu = QMenu(self)  # Downloader item context menu event
            remove_item = context_menu.addAction("从列表中移除Mod")
            remove_item.triggered.connect(
                partial(self._remove_mod_from_list, context_item)
            )
            context_menu.exec_(self.downloader_list.mapToGlobal(point))

    def _remove_mod_from_list(self, context_item: QListWidgetItem) -> None:
        publishedfileid = context_item.data(Qt.ItemDataRole.UserRole)
        if publishedfileid in self.downloader_list_mods_tracking:
            self.downloader_list.takeItem(self.downloader_list.row(context_item))
            self.downloader_list_mods_tracking.remove(publishedfileid)
        else:
            logger.error("Steam Browser Error: Item not found in tracking list.")

    def _subscribe_to_mods_from_list(self) -> None:
        logger.debug(
            f"Signaling Steamworks subscription handler with {len(self.downloader_list_mods_tracking)} mods"
        )
        self.steamworks_subscription_signal.emit(
            [
                "subscribe",
                [eval(str_pfid) for str_pfid in self.downloader_list_mods_tracking],
            ]
        )

    def _web_view_load_started(self) -> None:
        # Progress bar start, placeholder start
        self.progress_bar.show()
        self.web_view.hide()
        self.web_view_loading_placeholder.show()

    def _web_view_load_progress(self, progress: int) -> None:
        # Progress bar progress
        self.progress_bar.setValue(progress)
        # Placeholder done after page begins to load
        if progress > 25:
            self.web_view_loading_placeholder.hide()
            self.web_view.show()

    def _web_view_load_finished(self) -> None:
        # Progress bar done
        self.progress_bar.hide()
        self.progress_bar.setValue(0)

        # Cache information from page
        self.current_title = self.web_view.title()
        self.web_view.page().toHtml(self.__set_current_html)
        self.current_url = self.web_view.url().toString()

        # Update UI elements
        self.setWindowTitle(self.current_title)
        self.location.setText(self.current_url)

        # Check if we are browsing a collection/mod - remove elements if found
        if self.url_prefix_steam in self.current_url:
            # Remove "Install Steam" button
            install_button_removal_script = """
            var elements = document.getElementsByClassName("header_installsteam_btn header_installsteam_btn_green");
            while (elements.length > 0) {
                elements[0].parentNode.removeChild(elements[0]);
            }
            """
            self.web_view.page().runJavaScript(
                install_button_removal_script, 0, lambda result: None
            )
            remove_top_banner = """
            var element = document.getElementById("global_header"); 
            var elements = document.getElementsByClassName("responsive_header")
            if (element) {
                element.parentNode.removeChild(element);
            }
            if (elements){
                elements[0].parentNode.removeChild(elements[0])
                document.getElementsByClassName("responsive_page_content")[0].setAttribute("style","padding-top: 0px;")
                document.getElementsByClassName("apphub_HeaderTop workshop")[0].setAttribute("style","padding-top: 0px;")
                document.getElementsByClassName("apphub_HomeHeaderContent")[0].setAttribute("style","padding-top: 0px;")
            }
            
            """
            self.web_view.page().runJavaScript(
                remove_top_banner, 0, lambda result: None
            )
            # change target <a>
            change_target_a_script = """
            var elements = document.getElementsByTagName("a");
            for (var i = 0, l = elements.length; i < l; i++) {
                elements[i].target = "_self";
            }
            """
            self.web_view.page().runJavaScript(
                change_target_a_script, 0, lambda result: None
            )
            # Remove "Login" button
            # login_button_removal_script = """
            # var elements = document.getElementsByClassName("global_action_link");
            # while (elements.length > 0) {
            #     elements[0].parentNode.removeChild(elements[0]);
            # }
            # """

            if (
                self.url_prefix_sharedfiles in self.current_url
                or self.url_prefix_workshop in self.current_url
            ):
                # get mod id from steam workshop url
                if self.url_prefix_sharedfiles in self.current_url:
                    publishedfileid = self.current_url.split(
                        self.url_prefix_sharedfiles, 1
                    )[1]
                else:
                    publishedfileid = self.current_url.split(
                        self.url_prefix_workshop, 1
                    )[1]
                if self.searchtext_string in publishedfileid:
                    publishedfileid = publishedfileid.split(self.searchtext_string)[0]
                # check if mod is installed
                is_installed = self._is_mod_installed(publishedfileid)
                # Remove area that shows "Subscribe to download" and "Subscribe"/"Unsubscribe" button for mods
                mod_subscribe_area_removal_script = """
                var elements = document.getElementsByClassName("game_area_purchase_game");
                while (elements.length > 0) {
                    elements[0].parentNode.removeChild(elements[0]);
                }
                """
                self.web_view.page().runJavaScript(
                    mod_subscribe_area_removal_script, 0, lambda result: None
                )
                # Remove area that shows "Subscribe to all" and "Unsubscribe to all" buttons for collections
                mod_unsubscribe_button_removal_script = """
                var elements = document.getElementsByClassName("subscribeCollection");
                while (elements.length > 0) {
                    elements[0].parentNode.removeChild(elements[0]);
                }
                """
                self.web_view.page().runJavaScript(
                    mod_unsubscribe_button_removal_script, 0, lambda result: None
                )
                # Remove "Subscribe" buttons from any mods shown in a collection
                subscribe_buttons_removal_script = """
                var elements = document.getElementsByClassName("general_btn subscribe");
                while (elements.length > 0) {
                    elements[0].parentNode.removeChild(elements[0]);
                }
                """
                self.web_view.page().runJavaScript(
                    subscribe_buttons_removal_script, 0, lambda result: None
                )
                # add buttons for collection items
                add_collection_buttons_script = """
                // find all collection items
                var collectionItems = document.getElementsByClassName('collectionItem');
                
                for (var i = 0; i < collectionItems.length; i++) {
                    var item = collectionItems[i];
                    
                    // get the mod id from the item
                    var modId = item.id.replace('sharedfile_', '');
                    
                    // find the subscription controls div
                    var subscriptionControls = item.querySelector('.subscriptionControls');
                    if (!subscriptionControls) {
                        continue;
                    }
                    
                    // check if mod is installed
                    var isInstalled = window.installedMods && window.installedMods.includes(modId);
                    
                    if (isInstalled) {
                        // create installed indicator
                        var installedIndicator = document.createElement('div');
                        installedIndicator.innerHTML = '✓';
                        installedIndicator.style.backgroundColor = '#4CAF50';
                        installedIndicator.style.color = 'white';
                        installedIndicator.style.width = '24px';
                        installedIndicator.style.height = '24px';
                        installedIndicator.style.borderRadius = '4px';
                        installedIndicator.style.display = 'flex';
                        installedIndicator.style.alignItems = 'center';
                        installedIndicator.style.justifyContent = 'center';
                        installedIndicator.style.fontWeight = 'bold';
                        installedIndicator.style.fontSize = '16px';
                        
                        // Replace subscription controls with our indicator
                        subscriptionControls.innerHTML = '';
                        subscriptionControls.appendChild(installedIndicator);
                    } else {
                        // create link button
                        var linkButton = document.createElement('a');
                        linkButton.innerHTML = '→';
                        linkButton.href = 'https://steamcommunity.com/sharedfiles/filedetails/?id=' + modId;
                        linkButton.style.backgroundColor = '#2196F3';
                        linkButton.style.color = 'white';
                        linkButton.style.width = '24px';
                        linkButton.style.height = '24px';
                        linkButton.style.borderRadius = '4px';
                        linkButton.style.display = 'flex';
                        linkButton.style.alignItems = 'center';
                        linkButton.style.justifyContent = 'center';
                        linkButton.style.cursor = 'pointer';
                        linkButton.style.fontWeight = 'bold';
                        linkButton.style.fontSize = '20px';
                        linkButton.style.textDecoration = 'none';
                        
                        // Replace subscription controls with our button
                        subscriptionControls.innerHTML = '';
                        subscriptionControls.appendChild(linkButton);
                    }
                }
                """
                # Get list of installed mod IDs and inject into page
                installed_mods = []
                for metadata in self.metadata_manager.internal_local_metadata.values():
                    if metadata.get("publishedfileid"):
                        installed_mods.append(metadata["publishedfileid"])
                inject_installed_mods_script = f"""
                window.installedMods = {installed_mods};
                """
                self.web_view.page().runJavaScript(
                    inject_installed_mods_script, 0, lambda result: None
                )
                self.web_view.page().runJavaScript(
                    add_collection_buttons_script, 0, lambda result: None
                )
                # add installed indicator if mod is installed
                if is_installed:
                    add_installed_indicator_script = """
                    // Create a new div for the installed indicator
                    var installedDiv = document.createElement('div');
                    installedDiv.style.backgroundColor = '#4CAF50';  // Green background
                    installedDiv.style.color = 'white';
                    installedDiv.style.padding = '10px';
                    installedDiv.style.borderRadius = '5px';
                    installedDiv.style.marginBottom = '10px';
                    installedDiv.style.textAlign = 'center';
                    installedDiv.style.fontWeight = 'bold';
                    installedDiv.innerHTML = '✓ 已安装';
                    // Insert it at the top of the page content
                    var contentDiv = document.querySelector('.workshopItemDetailsHeader');
                    if (contentDiv) {
                        contentDiv.parentNode.insertBefore(installedDiv, contentDiv);
                    }
                    """
                    self.web_view.page().runJavaScript(
                        add_installed_indicator_script, 0, lambda result: None
                    )
                # Show the add_to_list_button
                self.nav_bar.addAction(self.add_to_list_button)
            else:
                self.nav_bar.removeAction(self.add_to_list_button)

    def __set_current_html(self, html: str) -> None:
        # Update cached html with html from current page
        self.current_html = html

    def _is_mod_installed(self, publishedfileid: str) -> bool:
        """Check if a mod is installed by looking through local and workshop folders"""
        # check all mods in internal metadata
        for metadata in self.metadata_manager.internal_local_metadata.values():
            if metadata.get("publishedfileid") == publishedfileid:
                return True
        return False
