"""Browser integration tests for the voice iframe and the actual Streamlit text area.

Speech recognition events are simulated, not microphone recordings.
"""
import os
from playwright.sync_api import sync_playwright, expect

URL = os.environ.get("ACPA_TEST_URL", "http://127.0.0.1:8501")
MOCK = """() => {
  class MockSpeech {
    constructor() { window.mockSpeech = this; }
    start() {}
    stop() {
      if (this.mode === 'silent') return;
      if (this.mode === 'revised') this.emit([['الجري السريع', true]]);
      this.onend?.();
      this.onend?.();
    }
    abort() { this.onend?.(); }
    emit(items) {
      const results = items.map(([transcript, isFinal]) =>
        Object.assign([{transcript}], {isFinal}));
      this.onresult?.({resultIndex: 0, results});
    }
  }
  Object.defineProperty(window, 'SpeechRecognition', {value:MockSpeech, configurable:true});
  Object.defineProperty(window, 'webkitSpeechRecognition', {value:MockSpeech, configurable:true});
}"""


def open_search(browser, language):
    page = browser.new_page(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
    page.add_init_script("(" + MOCK + ")()")
    page.goto(f"{URL}/?lang={language}")
    page.locator(".st-key-core_find button").click(timeout=60000)
    area = page.locator('[data-testid="stTextArea"] textarea').first
    expect(area).to_be_visible(timeout=60000)
    frames = page.locator('iframe[title*="acpa_voice"]')
    expect(frames).to_have_count(2 if language == "ar" else 1, timeout=60000)
    return page, area, frames


def dictate(frames, index, items, mode, auto_end=False):
    frame = frames.nth(index).content_frame
    button = frame.locator("#b")
    expect(button).to_be_enabled(timeout=30000)
    button.click()
    button.evaluate("""(el, arg) => {
      const r = window.mockSpeech;
      r.mode = arg.mode;
      r.emit(arg.items);
      if (arg.auto) r.onend();
    }""", {"items":items,"mode":mode,"auto":auto_end})
    if not auto_end:
        button.click()


def check(browser, engine):
    page, area, frames = open_search(browser, "ar")
    dictate(frames, 0, [["كرة القدم", False]], "normal")
    expect(area).to_have_value("كرة القدم", timeout=30000)
    dictate(frames, 0, [["الجري", False]], "revised")
    expect(area).to_have_value("كرة القدم, الجري السريع", timeout=30000)
    dictate(frames, 0, [["التوازن", False]], "silent")
    expect(area).to_have_value("كرة القدم, الجري السريع, التوازن", timeout=30000)
    dictate(frames, 1, [["endurance", True]], "normal", auto_end=True)
    expect(area).to_have_value("كرة القدم, الجري السريع, التوازن, endurance", timeout=30000)
    page.close()
    page, area, frames = open_search(browser, "fr")
    dictate(frames, 0, [["course", True], [" rapide", False]], "normal", auto_end=True)
    expect(area).to_have_value("course rapide", timeout=30000)
    page.close()
    print(f"PASS {engine} voice: interim stop, revised final, missing end, bilingual and French", flush=True)


if __name__ == "__main__":
    with sync_playwright() as p:
        for engine in (p.chromium, p.webkit):
            browser = engine.launch()
            check(browser, engine.name)
            browser.close()
