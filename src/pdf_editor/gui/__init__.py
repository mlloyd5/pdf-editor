import sys


def main():
    """Launch the PDF Editor GUI."""
    from PySide6.QtWidgets import QApplication

    from pdf_editor.gui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("PDF Editor")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
