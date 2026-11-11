"""Small original SVG line icons rendered locally; no icon-font dependency."""
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

PATHS = {
    'Dashboard': '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
    'Tasks': '<rect x="5" y="4" width="15" height="17" rx="3"/><path d="m8 10 2 2 4-4M8 16h8M9 3h7"/>',
    'Session history': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l4 2"/>',
    'XP & Levels': '<path d="m12 2 3 7 7 3-7 3-3 7-3-7-7-3 7-3z"/>',
    'Milestones': '<path d="M7 3h10v7a5 5 0 0 1-10 0zM7 5H3v3a4 4 0 0 0 4 4m10-7h4v3a4 4 0 0 1-4 4M12 15v5m-4 1h8"/>',
    'Analytics': '<path d="M4 3v17h17M8 15v-4m5 4V7m5 8v-6"/>',
    'Settings': '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 1v3m0 16v3M1 12h3m16 0h3"/>',
    'play': '<path d="m8 4 12 8-12 8z"/>',
    'pause': '<path d="M8 5v14M16 5v14"/>',
    'save': '<path d="M5 3h12l4 4v14H3V3zM8 3v6h8V3M7 21v-7h10v7"/>',
}


def icon(name, color='#9facb9'):
    paths = PATHS.get(name, PATHS['XP & Levels'])
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><g fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{paths}</g></svg>'
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pixmap = QPixmap(48, 48)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(2)
    return QIcon(pixmap)
