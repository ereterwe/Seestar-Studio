from ..i18n import QFileDialog
from ..i18n import source as ui_text, tr
from datetime import datetime, timezone
from pathlib import Path
from PySide6.QtCore import Qt, QStandardPaths
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTreeWidget, QTreeWidgetItem, QAbstractItemView, QLabel, QLineEdit, QComboBox, QPushButton, QHeaderView
from ..card import label, button
from .browser import FileBrowserService
from .downloads import DownloadService
from .models import RemoteEntry
from ..telemetry import number
from ..timezones import local_text, system_timezone

def size_text(size: float) -> str:
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if size < 1024:
            return number(size, ' '+unit, 1)
        size /= 1024
    return number(size, ' PiB', 1)

class FileManagerWidget(QWidget):

    def __init__(self, settings, browser=None, downloads=None):
        super().__init__()
        self.settings = settings
        cache = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)) / 'thumbnails'
        self.browser = browser or FileBrowserService(cache)
        self.downloads = downloads or DownloadService()
        self.devices = {}
        self.roots = {}
        self.pending = []
        self.current = None
        self._generation = 0
        self._preview_generation = 0
        self._closing = False
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 8, 0, 0)
        outer.addWidget(label(ui_text('m0307'), 'eyebrow'))
        top = QHBoxLayout()
        self.destination = QLineEdit(settings.values.get('download_dir', ''))
        self.destination.setPlaceholderText(ui_text('m0298'))
        self.destination.setReadOnly(True)
        top.addWidget(self.destination, 1)
        top.addWidget(button(ui_text('m0308'), self.choose_destination))
        self.limit = QComboBox()
        for text, value in [('1 MiB/s', 1), (ui_text('m0309'), 2), ('5 MiB/s', 5), ('10 MiB/s', 10), (ui_text('m0310'), 0)]:
            self.limit.addItem(text, value * 1024 * 1024)
        self.limit.setCurrentIndex(1)
        top.addWidget(self.limit)
        outer.addLayout(top)
        actions = QHBoxLayout()
        actions.addWidget(button(ui_text('m0416'), self.refresh_current))
        actions.addWidget(button(ui_text('m0311'), self.download_selected))
        actions.addWidget(button(ui_text('m0312'), self.download_folder))
        actions.addStretch()
        self.search = QLineEdit()
        self.search.setPlaceholderText(ui_text('m0299'))
        self.search.textChanged.connect(self.filter_files)
        actions.addWidget(self.search)
        outer.addLayout(actions)
        split = QSplitter()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(ui_text('m0300'))
        self.tree.itemExpanded.connect(self.expand_folder)
        self.tree.itemClicked.connect(self.open_folder)
        split.addWidget(self.tree)
        center = QWidget()
        middle = QVBoxLayout(center)
        middle.setContentsMargins(0, 0, 0, 0)
        self.path_label = label(ui_text('m0301'), 'muted')
        middle.addWidget(self.path_label)
        self.files = QTreeWidget()
        self.files.setHeaderLabels([ui_text('m0313'), ui_text('m0314'), ui_text('m0315'), ui_text('m0316')])
        self.files.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.files.setSortingEnabled(True)
        self.files.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.files.itemDoubleClicked.connect(self.open_file_item)
        self.files.itemSelectionChanged.connect(self.preview_selected)
        middle.addWidget(self.files, 1)
        split.addWidget(center)
        preview_panel = QWidget()
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.addWidget(label('VORSCHAU', 'eyebrow'))
        self.preview = label(ui_text('m0302'), 'muted')
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setWordWrap(True)
        self.preview.setMinimumWidth(230)
        self.preview.setMaximumWidth(340)
        preview_layout.addWidget(self.preview, 1)
        self.preview_info = label('', 'muted')
        self.preview_info.setWordWrap(True)
        preview_layout.addWidget(self.preview_info)
        split.addWidget(preview_panel)
        split.setSizes([260, 850, 270])
        outer.addWidget(split, 1)
        outer.addWidget(label(ui_text('m0317'), 'eyebrow'))
        self.jobs = QTreeWidget()
        self.jobs.setHeaderLabels([ui_text('m0318'), ui_text('m0319'), ui_text('m0320'), ui_text('extra.6'), ui_text('extra.7'), ui_text('m0321')])
        self.jobs.setMaximumHeight(190)
        self.jobs.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        outer.addWidget(self.jobs)
        bottom = QHBoxLayout()
        bottom.addWidget(button(ui_text('m0207'), self.cancel_selected))
        bottom.addWidget(button(ui_text('m0322'), self.retry_selected))
        self.message = label(ui_text('m0303'), 'muted')
        self.message.setWordWrap(True)
        bottom.addWidget(self.message, 1)
        outer.addLayout(bottom)

    def choose_destination(self):
        path = QFileDialog.getExistingDirectory(self, ui_text('m0304'), self.destination.text() or str(Path.home()))
        if path:
            self.destination.setText(path)
            self.settings.values['download_dir'] = path

    def sync_devices(self, data):
        if self._closing:
            return
        for serial, (info, telemetry, _) in data.items():
            self.devices[serial] = info
            if serial not in self.roots:
                item = QTreeWidgetItem(self.tree, [f'{info.model} · {serial}'])
                item.setData(0, Qt.ItemDataRole.UserRole, (serial, ''))
                item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
                self.roots[serial] = item
                self.load_tree(item)
        self.downloads.update_devices(self.devices)
        self.poll()

    def load_tree(self, item):
        identity = item.data(0, Qt.ItemDataRole.UserRole)
        if not identity or item.data(0, Qt.ItemDataRole.UserRole + 1) == 'loading':
            return
        serial, path = identity
        item.setData(0, Qt.ItemDataRole.UserRole + 1, 'loading')
        future = self.browser.list(self.devices[serial], path)
        self.pending.append(('tree', future, (item, identity)))

    def expand_folder(self, item):
        if item.childCount() == 0:
            self.load_tree(item)

    def open_folder(self, item, column=0):
        identity = item.data(0, Qt.ItemDataRole.UserRole)
        if identity:
            self.show_path(*identity)

    def show_path(self, serial, path):
        self.current = (serial, path)
        self._generation += 1
        self._preview_generation += 1
        self.files.clear()
        self.preview.clear()
        self.path_label.setText(f"{self.devices[serial].model} / {path or 'EMMC Images'}")
        self.message.setText(ui_text('m0305'))
        self.pending.append(('files', self.browser.list(self.devices[serial], path), self._generation))

    def refresh_current(self):
        for item in self.roots.values():
            self.load_tree(item)
        if self.current:
            self.show_path(*self.current)

    def open_file_item(self, item, column=0):
        entry = item.data(0, Qt.ItemDataRole.UserRole)
        if entry and entry.is_dir and self.current:
            self.show_path(self.current[0], entry.path)

    def filter_files(self):
        text = self.search.text().casefold()
        for index in range(self.files.topLevelItemCount()):
            item = self.files.topLevelItem(index)
            item.setHidden(text not in (item.text(0) + ' ' + item.text(1)).casefold())

    def preview_selected(self):
        self._preview_generation += 1
        for kind, future, _ in self.pending:
            if kind == 'preview':
                future.cancel()
        selected = self.files.selectedItems()
        if len(selected) != 1 or not self.current:
            return
        entry = selected[0].data(0, Qt.ItemDataRole.UserRole)
        self.preview.clear()
        self.preview_info.setText(entry.name)
        if entry.is_dir or Path(entry.name).suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
            self.preview.setText(ui_text('m0323'))
            return
        self.preview.setText(ui_text('m0306'))
        future = self.browser.thumbnail(self.devices[self.current[0]], entry)
        self.pending.append(('preview', future, self._preview_generation))

    def download_selected(self):
        self.enqueue([item.data(0, Qt.ItemDataRole.UserRole) for item in self.files.selectedItems()])

    def download_folder(self):
        if self.current:
            path = self.current[1]
            self.enqueue([RemoteEntry(path, path.rsplit('/', 1)[-1] or 'EMMC Images', True)])

    def enqueue(self, entries):
        if not self.current or not entries:
            self.message.setText(ui_text('m0324'))
            return
        if not self.destination.text():
            self.choose_destination()
        if not self.destination.text():
            return
        try:
            self.downloads.submit(self.devices[self.current[0]], entries, Path(self.destination.text()), self.limit.currentData())
            self.message.setText(ui_text('m0325'))
        except Exception as exc:
            self.message.setText(str(exc) if isinstance(exc, ValueError) else type(exc).__name__)

    def cancel_selected(self):
        for item in self.jobs.selectedItems():
            self.downloads.cancel(item.data(0, Qt.ItemDataRole.UserRole))

    def retry_selected(self):
        for item in self.jobs.selectedItems():
            self.downloads.retry(item.data(0, Qt.ItemDataRole.UserRole))

    def poll(self):
        for kind, future, context in list(self.pending):
            if not future.done():
                continue
            self.pending.remove((kind, future, context))
            try:
                value = future.result()
                if kind == 'tree':
                    item, (serial, path) = context
                    item.takeChildren()
                    item.setData(0, Qt.ItemDataRole.UserRole + 1, 'ready')
                    for entry in value:
                        if entry.is_dir:
                            child = QTreeWidgetItem(item, [entry.name])
                            child.setData(0, Qt.ItemDataRole.UserRole, (serial, entry.path))
                            child.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
                    item.setExpanded(True)
                elif kind == 'files' and context == self._generation:
                    for entry in value:
                        try:
                            date = local_text(datetime.fromtimestamp(entry.modified, timezone.utc), system_timezone(), True) if entry.modified else '—'
                        except (OSError, OverflowError, ValueError):
                            date = '—'
                        item = QTreeWidgetItem(self.files, [entry.name, entry.kind, '—' if entry.is_dir else size_text(entry.size), date])
                        item.setData(0, Qt.ItemDataRole.UserRole, entry)
                    self.filter_files()
                    self.message.setText(ui_text('m0327').format(p0=f'{len(value)}'))
                elif kind == 'preview' and context == self._preview_generation:
                    self.preview.setPixmap(QPixmap.fromImage(value).scaled(320, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            except Exception as exc:
                message = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
                if kind == 'tree':
                    context[0].setData(0, Qt.ItemDataRole.UserRole + 1, 'error')
                    context[0].setToolTip(0, ui_text('m0328').format(p0=f'{message}'))
                elif kind == 'preview' and context == self._preview_generation:
                    self.preview.setText(message)
                else:
                    self.message.setText(ui_text('m0329') + message)
        selected = {item.data(0, Qt.ItemDataRole.UserRole) for item in self.jobs.selectedItems()}
        existing = {self.jobs.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole): self.jobs.topLevelItem(i) for i in range(self.jobs.topLevelItemCount())}
        for status in self.downloads.statuses():
            item = existing.get(status.job_id)
            if item is None:
                item = QTreeWidgetItem(self.jobs)
                item.setData(0, Qt.ItemDataRole.UserRole, status.job_id)
            values = [f'{status.serial} · {status.name}', status.state, number(100 * status.done / status.total, ' %', 1) if status.total else '—', size_text(max(0, status.total - status.done)), size_text(status.speed) + '/s', f'{status.files_done}/{status.files_total}']
            for column, text in enumerate(values):
                item.setText(column, text)
                item.setToolTip(column, status.error or ui_text('m0326'))
            item.setSelected(status.job_id in selected)

    def stop(self):
        self._closing = True
        self.browser.stop()
        self.downloads.stop()

    @property
    def running(self):
        return self.browser.running or self.downloads.running
