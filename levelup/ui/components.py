"""Shared presentation components. No database queries or reward calculations."""
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLayout, QScrollArea, QStackedWidget, QVBoxLayout, QWidget


def label(text='', role='body'):
    widget = QLabel(text)
    widget.setObjectName(role)
    widget.setWordWrap(True)
    widget.setTextFormat(Qt.TextFormat.PlainText)
    return widget


class Card(QFrame):
    def __init__(self, variant='card'):
        super().__init__()
        self.setObjectName(variant)
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(22, 20, 22, 20)
        self.body.setSpacing(12)
        self.setMinimumWidth(0)


class PageHeader(QWidget):
    def __init__(self, eyebrow, title, description):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 6)
        layout.setSpacing(7)
        layout.addWidget(label(eyebrow.upper(), 'eyebrow'))
        layout.addWidget(label(title, 'heading'))
        layout.addWidget(label(description, 'muted'))


class StatCard(Card):
    def __init__(self, title, detail):
        super().__init__()
        self.body.addWidget(label(title.upper(), 'eyebrow'))
        self.value = label('—', 'statValue')
        self.body.addWidget(self.value)
        self.body.addWidget(label(detail, 'muted'))


class ResponsiveGrid(QWidget):
    """Reflow cards without reconstructing them or losing accessible state."""
    def __init__(self, minimum=240, maximum_columns=3):
        super().__init__()
        self.minimum = minimum
        self.maximum_columns = maximum_columns
        self.items = []
        self.columns = 0
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(14)
        self.grid.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)

    def add(self, widget):
        self.items.append(widget)
        self.reflow()

    def reflow(self):
        measured = max((item.minimumSizeHint().width() for item in self.items), default=0)
        minimum = max(self.minimum, measured)
        columns = max(1, min(self.maximum_columns, (self.width() + 14) // (minimum + 14)))
        if columns == self.columns and self.grid.count() == len(self.items):
            return
        previous = self.columns
        while self.grid.count():
            self.grid.takeAt(0)
        for column in range(max(previous, columns)):
            self.grid.setColumnStretch(column, 1 if column < columns else 0)
        for index, widget in enumerate(self.items):
            self.grid.addWidget(widget, index // columns, index % columns)
        self.columns = columns

    def minimumSizeHint(self):
        # Do not let a previously wide column layout prevent later shrinking.
        # Child minimum widths decide column count during reflow instead.
        return QSize(0, self.grid.minimumSize().height())

    def resizeEvent(self, event):
        self.reflow()
        super().resizeEvent(event)


class PageStack(QStackedWidget):
    """Each page owns its scroll area; long hidden pages cannot stretch others."""
    def addWidget(self, page):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        return super().addWidget(scroll)

    def currentWidget(self):
        scroll = super().currentWidget()
        return scroll.widget() if scroll else None

    def currentScroll(self):
        return super().currentWidget()

    def setCurrentWidget(self, page):
        for index in range(self.count()):
            scroll = super().widget(index)
            if scroll.widget() is page:
                super().setCurrentWidget(scroll)
                return
        raise ValueError('Page is not registered in this workspace.')
