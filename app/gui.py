"""CustomTkinter UI: sentence+word input -> preview -> confirm add to Anki."""

import queue
import threading

import customtkinter as ctk

from app import anki_client, constants, pipeline


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("German Vocab -> Anki")
        self.geometry("640x720")
        self.minsize(560, 480)

        self._queue = queue.Queue()
        self._card_data = None

        self._build_widgets()
        self._poll_queue()
        self._check_connection_async()
        # Workaround for a macOS Tk bug where the window renders blank until
        # its size changes; nudging it by a pixel forces an immediate redraw.
        self.after(50, self._nudge_redraw)

    def _nudge_redraw(self):
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w + 1}x{h}")
        self.after(10, lambda: self.geometry(f"{w}x{h}"))

    # ---- widget construction -------------------------------------------------

    def _build_widgets(self):
        pad = {"padx": 16, "pady": 6}

        self.status_label = ctk.CTkLabel(
            self, text="Checking connection to Anki...", text_color="gray",
            anchor="w", justify="left", wraplength=580,
        )
        self.status_label.pack(fill="x", **pad)

        ctk.CTkLabel(self, text="Deck:", anchor="w").pack(fill="x", padx=16)
        self.deck_var = ctk.StringVar(value=constants.DECKS[0])
        self.deck_menu = ctk.CTkOptionMenu(self, values=constants.DECKS, variable=self.deck_var)
        self.deck_menu.pack(fill="x", **pad)

        ctk.CTkLabel(self, text="German sentence:", anchor="w").pack(fill="x", padx=16)
        self.sentence_entry = ctk.CTkEntry(
            self, placeholder_text="e.g. Der Hund läuft schnell über die Straße."
        )
        self.sentence_entry.pack(fill="x", **pad)

        ctk.CTkLabel(self, text="Target word (as it appears in the sentence):", anchor="w").pack(
            fill="x", padx=16
        )
        self.target_entry = ctk.CTkEntry(self, placeholder_text="e.g. läuft")
        self.target_entry.pack(fill="x", **pad)

        self.generate_btn = ctk.CTkButton(self, text="Generate", command=self.on_generate_click)
        self.generate_btn.pack(pady=10)

        self.preview_frame = ctk.CTkScrollableFrame(self)

        ctk.CTkLabel(self.preview_frame, text="Hidden sentence (Front):", anchor="w").pack(fill="x")
        self.hidden_label = ctk.CTkLabel(
            self.preview_frame, text="", anchor="w", justify="left", wraplength=580
        )
        self.hidden_label.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(self.preview_frame, text="Full sentence (Back):", anchor="w").pack(fill="x")
        self.full_label = ctk.CTkLabel(
            self.preview_frame, text="", anchor="w", justify="left", wraplength=580
        )
        self.full_label.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(self.preview_frame, text="Translation (editable):", anchor="w").pack(fill="x")
        self.translation_entry = ctk.CTkEntry(self.preview_frame)
        self.translation_entry.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            self.preview_frame, text="Answer / dictionary form (editable):", anchor="w"
        ).pack(fill="x")
        self.answer_entry = ctk.CTkEntry(self.preview_frame)
        self.answer_entry.pack(fill="x", pady=(0, 8))

        self.warnings_label = ctk.CTkLabel(
            self.preview_frame, text="", text_color="#b8860b", anchor="w",
            justify="left", wraplength=580,
        )
        self.warnings_label.pack(fill="x", pady=(0, 8))

        self.allow_dup_var = ctk.BooleanVar(value=False)
        self.allow_dup_check = ctk.CTkCheckBox(
            self.preview_frame, text="Add anyway (allow duplicate)", variable=self.allow_dup_var
        )
        self.allow_dup_check.pack(anchor="w")

        self.add_btn = ctk.CTkButton(
            self.preview_frame, text="Add to Anki", command=self.on_add_click, state="disabled"
        )
        self.add_btn.pack(pady=10)

    # ---- background work + queue polling --------------------------------------

    def _poll_queue(self):
        try:
            while True:
                kind, payload = self._queue.get_nowait()
                self._handle_queue_item(kind, payload)
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)

    def _handle_queue_item(self, kind, payload):
        if kind == "conn_ok":
            self._set_status("Connected to Anki.", error=False)
        elif kind == "conn_error":
            self._set_status(f"{payload}", error=True)
        elif kind == "generate_ok":
            self.generate_btn.configure(state="normal")
            self._card_data = payload
            self._show_preview(payload)
            self._set_status("Preview ready — review before adding.", error=False)
        elif kind == "generate_error":
            self.generate_btn.configure(state="normal")
            self._card_data = None
            self._hide_preview()
            self._set_status(f"Error: {payload}", error=True)
        elif kind == "add_ok":
            self._set_status(f"Added to Anki (note id {payload}).", error=False)
            self._hide_preview()
            self._card_data = None
            self.sentence_entry.delete(0, "end")
            self.target_entry.delete(0, "end")
        elif kind == "add_error":
            self.add_btn.configure(state="normal")
            self._set_status(f"Error: {payload}", error=True)

    def _check_connection_async(self):
        def worker():
            try:
                anki_client.check_connection()
                self._queue.put(("conn_ok", None))
            except Exception as e:
                self._queue.put(("conn_error", str(e)))

        threading.Thread(target=worker, daemon=True).start()

    # ---- actions ---------------------------------------------------------------

    def on_generate_click(self):
        sentence = self.sentence_entry.get().strip()
        target = self.target_entry.get().strip()
        if not sentence or not target:
            self._set_status("Please enter both a sentence and a target word.", error=True)
            return

        self.generate_btn.configure(state="disabled")
        self.add_btn.configure(state="disabled")
        self._hide_preview()
        self._set_status("Working...", error=False)

        def worker():
            try:
                card = pipeline.build_card(sentence, target)
                self._queue.put(("generate_ok", card))
            except Exception as e:
                self._queue.put(("generate_error", str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def on_add_click(self):
        if self._card_data is None:
            return
        self._card_data.translation = self.translation_entry.get().strip()
        self._card_data.answer = self.answer_entry.get().strip()
        allow_dup = self.allow_dup_var.get()
        deck_name = self.deck_var.get()
        card_data = self._card_data

        self.add_btn.configure(state="disabled")
        self._set_status("Adding to Anki...", error=False)

        def worker():
            try:
                note_id = pipeline.confirm_add(card_data, deck_name, allow_duplicate=allow_dup)
                self._queue.put(("add_ok", note_id))
            except Exception as e:
                self._queue.put(("add_error", str(e)))

        threading.Thread(target=worker, daemon=True).start()

    # ---- preview panel -----------------------------------------------------------

    def _show_preview(self, card):
        self.hidden_label.configure(text=card.hidden_sentence)
        self.full_label.configure(text=card.sentence)
        self.translation_entry.delete(0, "end")
        self.translation_entry.insert(0, card.translation)
        self.answer_entry.delete(0, "end")
        self.answer_entry.insert(0, card.answer)
        self.warnings_label.configure(text="\n".join(card.warnings))
        self.allow_dup_var.set(False)
        self.preview_frame.pack(fill="both", expand=True, padx=16, pady=6)
        self.add_btn.configure(state="normal")

    def _hide_preview(self):
        self.preview_frame.pack_forget()

    def _set_status(self, text, error=False):
        self.status_label.configure(text=text, text_color="#b00020" if error else "gray")
