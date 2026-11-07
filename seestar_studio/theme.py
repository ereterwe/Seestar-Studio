STYLE = """
QWidget { background: #0b1016; color: #dce4ed; font-family: 'Segoe UI'; font-size: 13px; }
QMainWindow { background: #0b1016; }
QFrame#card { background: #121a24; border: 1px solid #283342; border-radius: 10px; }
QFrame#card QLabel, QFrame#card QWidget#metrics, QFrame#card QWidget#details { background: transparent; }
QLabel#brand { font-size: 24px; font-weight: 700; letter-spacing: 2px; color: #f5f8fb; }
QLabel#eyebrow { color: #6fdfb5; font-size: 10px; font-weight: 700; letter-spacing: 2px; }
QLabel#muted { color: #8b9aae; font-size: 12px; }
QLabel#device { font-size: 16px; font-weight: 600; color: #cbd6e4; }
QLabel#target { font-size: 25px; font-weight: 600; color: #f1f5f9; }
QLabel#metricLabel { color: #8495aa; font-size: 10px; font-weight: 600; letter-spacing: 1px; }
QLabel#metricValue { color: #e3ebf4; font-size: 19px; font-weight: 600; }
QLabel#badge { border-radius: 5px; padding: 5px 9px; font-size: 11px; font-weight: 600; }
QPushButton, QToolButton { background: #1a2532; border: 1px solid #2c3b4e; border-radius: 5px; padding: 6px 10px; }
QPushButton:hover, QToolButton:hover { background: #29394b; border-color: #4e6d82; }
QPushButton:pressed { background: #33485c; }
QPushButton:disabled { color: #526174; background: #141c26; }
QPushButton#primary { color: #8ce7c2; border-color: #315e50; background: #16332c; }
QScrollArea { border: none; }
QScrollBar:vertical { background: #0b1016; width: 9px; }
QScrollBar::handle:vertical { background: #334252; border-radius: 4px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QStatusBar { background: #0b1016; color: #8191a4; font-size: 11px; }
QToolTip { color: #e3ebf4; background: #202e3e; border: 1px solid #465c76; padding: 6px; }
QTabWidget::pane { border: none; }
QTabBar::tab { background: #17222e; color: #94a8be; padding: 10px 20px; margin-right: 4px; border-bottom: 2px solid #26374a; }
QTabBar::tab:selected { color: #8ce7c2; border-bottom-color: #68cda6; }
QTreeWidget { background: #111a24; alternate-background-color: #15212d; border: 1px solid #29384a; }
QTreeWidget::item { padding: 5px; }
QTreeWidget::item:selected { background: #284c53; color: #f2ffff; }
QTableWidget { background: #111a24; alternate-background-color: #15212d; border: 1px solid #29384a; gridline-color: #26374a; selection-background-color: #284c53; selection-color: #f2ffff; }
QTableWidget::item { padding: 5px; }
QTableWidget::item:selected { background: #284c53; color: #f2ffff; }
QAbstractSpinBox { background: #162332; border: 1px solid #34475d; padding: 5px; }
QHeaderView::section { background: #1b2a3a; padding: 7px; border: none; color: #a9bbcd; }
QLineEdit, QComboBox { background: #162332; border: 1px solid #34475d; border-radius: 4px; padding: 7px; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 14px; height: 14px; border: 1px solid #71859b; border-radius: 3px; background: #162332; }
QCheckBox::indicator:checked { background: #6fdfb5; border: 2px solid #315e50; }
QCheckBox::indicator:disabled { border-color: #394553; background: #202b36; }
"""
