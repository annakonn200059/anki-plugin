"""Entry point: load the spaCy model once, then start the GUI."""

import customtkinter as ctk

from app import nlp
from app.gui import App


def main():
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    nlp.load_model()

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
