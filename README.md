# anki-deutsch

A small desktop tool that turns a German sentence + a target word into a fully-formed Anki card:
translation, the word's dictionary form (infinitive, or `der/die/das` + noun), a fill-in-the-blank
sentence, and sentence audio — pushed straight into Anki.

## For friends: installing the ready-made app

You don't need Python. You need:

1. **Anki** desktop — https://apps.ankiweb.net/
2. **The AnkiConnect add-on**: in Anki, go to *Tools → Add-ons → Get Add-ons…*, enter
   code **2055492159**, click OK, then **restart Anki**.
3. **This app** — unzip the file you were sent:
   - **Windows:** open the `Anki Deutsch` folder and double-click `Anki Deutsch.exe`.
     If a blue "Windows protected your PC" box appears, click *More info → Run anyway*.
     (Keep the whole folder together — the `.exe` needs the files next to it.)
   - **Mac:** drag `Anki Deutsch.app` into *Applications* and double-click it. The first time,
     macOS will say it can't verify the developer: click *Done*, then open
     *System Settings → Privacy & Security*, scroll down and click **Open Anyway**.
     (If it instead says the app is "damaged", run this once in Terminal:
     `xattr -dr com.apple.quarantine "/Applications/Anki Deutsch.app"`)

**Keep Anki open** while using the app — it talks to Anki through AnkiConnect. The first launch
can take ~10 seconds while the German language model loads. An internet connection is needed
for translation and audio.

### About port 8765

AnkiConnect listens on `http://127.0.0.1:8765` — a *local* address on your own computer, the
same on every Mac/PC. Nothing needs to be opened in a firewall or router. Only if you changed
AnkiConnect's port in its config, put the new address in `~/.anki-deutsch.json`
(on Windows: `C:\Users\<you>\.anki-deutsch.json`):

```json
{ "ankiconnect_url": "http://127.0.0.1:8765" }
```

## Usage

1. Pick a deck from your Anki decks, or type a new name (it's created automatically). The app
   remembers the last deck you used.
2. Type a German sentence and the target word as it appears in that sentence (any inflected form
   is fine — the app will find it and figure out the dictionary form).
3. Click **Generate**. Review the preview: hidden sentence, full sentence, the English translation,
   and the computed dictionary form. Both the translation and the dictionary form are editable in
   case the automatic guess (e.g. noun gender) is wrong.
4. Click **Add to Anki**.

The resulting card shows the translation + hidden sentence on the front; flipping it reveals the
dictionary form, the full sentence, and an audio player for the full sentence.

## Development

Requires Python 3.9+.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download de_core_news_sm
python -m app.main
```

## Building the app

On a Mac (builds for the Mac you're on):

```bash
pip install pyinstaller
pyinstaller anki_deutsch.spec --noconfirm
"dist/Anki Deutsch.app/Contents/MacOS/Anki Deutsch" --selftest   # quick check
```

A Windows `.exe` can't be built on a Mac. Push this repo to GitHub and run the **Build app**
workflow (*Actions* tab → *Build app* → *Run workflow*). It builds Windows, Apple-Silicon Mac
and Intel Mac versions; download the zips from the finished run. Pushing a tag like `v1.0`
also attaches them to a GitHub Release.
