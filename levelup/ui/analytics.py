"""Date/task filters, duration chart and exact-value table."""
from PySide6.QtCore import QDate, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QComboBox, QDateEdit, QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QScrollArea, QTabWidget, QToolTip, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)

from .formatting import format_duration


class FocusChart(QWidget):
    def __init__(self):
        super().__init__()
        self.buckets = ()
        self.setMinimumHeight(190)
        self.setMouseTracking(True)
        self.setAccessibleName('Focus duration bar chart; exact values available in the Totals tab')

    def render(self, buckets):
        self.buckets = buckets
        self.setMinimumWidth(max(400, len(buckets) * 56 + 70))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        left, top, bottom = 60, 28, self.height() - 48
        width = (self.width() - left - 10) / max(1, len(self.buckets))
        maximum = max((item.seconds for item in self.buckets), default=0)
        painter.setPen(QColor('#b9c5d8'))
        painter.drawText(8, 18, 'Hours')
        painter.drawText(8, top + 12, f'{maximum / 3600:.2f}')
        painter.drawText(25, bottom, '0')
        painter.drawLine(left, bottom, self.width() - 8, bottom)
        for index, bucket in enumerate(self.buckets):
            x = left + width * index
            height = (bottom - top) * bucket.seconds / maximum if maximum else 0
            painter.fillRect(QRectF(x + 7, bottom - height, max(1, width - 14), height), QColor('#7389eb'))
            painter.drawText(QRectF(x, bottom + 7, width, 20), Qt.AlignmentFlag.AlignCenter,
                             bucket.start.strftime('%m-%d'))
        if not maximum:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, 'No saved focus in this range')
        painter.end()

    def mouseMoveEvent(self, event):
        width = (self.width() - 70) / max(1, len(self.buckets))
        index = int((event.position().x() - 60) // width)
        if 0 <= index < len(self.buckets):
            bucket = self.buckets[index]
            QToolTip.showText(event.globalPosition().toPoint(),
                              f'{bucket.start.isoformat()}: {format_duration(bucket.seconds)} • {bucket.sessions} sessions', self)
        else:
            QToolTip.hideText()


class AnalyticsPage(QWidget):
    filter_requested = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel('Focus analytics')
        heading.setObjectName('heading')
        layout.addWidget(heading)
        note = QLabel('Saved sessions by local start date • Weeks start Monday • Up to 366 days')
        note.setObjectName('muted')
        note.setWordWrap(True)
        layout.addWidget(note)
        dates = QHBoxLayout()
        self.start = QDateEdit(QDate.currentDate().addDays(-29))
        self.end = QDateEdit(QDate.currentDate())
        for label, widget in (('From', self.start), ('Through', self.end)):
            widget.setCalendarPopup(True)
            widget.setDisplayFormat('yyyy-MM-dd')
            widget.setAccessibleName(label + ' date')
            dates.addWidget(QLabel(label))
            dates.addWidget(widget)
        self.grouping = QComboBox()
        self.grouping.addItem('Daily', 'daily')
        self.grouping.addItem('Weekly', 'weekly')
        self.grouping.setAccessibleName('Group focus totals')
        dates.addWidget(self.grouping)
        layout.addLayout(dates)
        row = QHBoxLayout()
        self.task = QComboBox()
        self.task.setMinimumContentsLength(10)
        self.task.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.task.setAccessibleName('Filter by task')
        self.apply = QPushButton('Apply filters')
        self.apply.clicked.connect(self.filter_requested.emit)
        row.addWidget(self.task, 1)
        row.addWidget(self.apply)
        layout.addLayout(row)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.tabs = QTabWidget()
        self.chart = FocusChart()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.chart)
        self.tabs.addTab(scroll, 'Chart')
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Date / week starting', 'Saved focus', 'Sessions'])
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setAccessibleName('Exact focus totals')
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in (1, 2):
            self.tree.header().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        self.tabs.addTab(self.tree, 'Totals')
        layout.addWidget(self.tabs, 1)

    def set_tasks(self, tasks):
        selected = self.task.currentData()
        self.task.clear()
        self.task.addItem('All tasks', None)
        self.task.addItem('Deleted tasks', 'deleted')
        for task in tasks:
            self.task.addItem(f"{task['title']} (#{task['id']})", task['id'])
        index = self.task.findData(selected)
        self.task.setCurrentIndex(max(0, index))

    def filters(self):
        selected = self.task.currentData()
        return dict(start=self.start.date().toPython(), end=self.end.date().toPython(),
                    grouping=self.grouping.currentData(),
                    task_id=selected if isinstance(selected, int) else None,
                    deleted_only=selected == 'deleted')

    def show_error(self, message):
        self.summary.setText(message)
        self.tree.clear()
        self.chart.render(())

    def render(self, report):
        self.summary.setText(f'Filtered saved focus: {format_duration(report.seconds)} • Sessions: {report.sessions}')
        self.tree.clear()
        for bucket in report.buckets:
            self.tree.addTopLevelItem(QTreeWidgetItem([
                bucket.start.isoformat(), format_duration(bucket.seconds), str(bucket.sessions)]))
        self.chart.render(report.buckets)
