# ============================================================
# AI Grammar Correction Assistant - app.py
# Run with:  python app.py
# Install first:  pip install transformers accelerate torch gradio
# ============================================================

# ------------------------------------------------------------
# BACKEND (your original code, unchanged)
# ------------------------------------------------------------
from transformers import pipeline

assistant = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-0.5B-Instruct",
    device_map="auto"
)

from torch.cuda import temperature
def grammar_assistant(question):

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI grammar correction assistant. "
                "Correct grammar, spelling, and punctuation. "
                "Keep the original meaning of the sentence. "
                "Explain the corrections in simple English. "
                "Show the original sentence and corrected sentence. "
                "If the sentence is already correct, say so."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    response = assistant(
        messages,
        max_new_tokens=200,
        do_sample=True,
        temperature=0.5
  )

    answer = response[0]["generated_text"][-1]["content"]

    return answer


# ------------------------------------------------------------
# FRONTEND (Gradio UI)
# ------------------------------------------------------------
import time
import html
import gradio as gr

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root { --accent:#7c5cff; --accent2:#00e5c3; --bg:#0b0b14; --card:rgba(255,255,255,.04); --line:rgba(255,255,255,.09); }

body, .gradio-container {
    background:
        radial-gradient(900px 500px at 10% -10%, rgba(124,92,255,.28), transparent 60%),
        radial-gradient(800px 500px at 100% 0%, rgba(0,229,195,.18), transparent 60%),
        var(--bg) !important;
    font-family:'Space Grotesk', sans-serif !important;
    color:#eceaff !important;
}
.gradio-container { max-width: 1080px !important; margin:auto !important; }
footer { display:none !important; }

/* ---------- Hero ---------- */
.hero { text-align:center; padding:38px 10px 10px; }
.badge {
    display:inline-flex; gap:8px; align-items:center;
    padding:6px 14px; border:1px solid var(--line); border-radius:999px;
    background:var(--card); font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:#b9b4ff;
}
.dot { width:8px; height:8px; border-radius:50%; background:var(--accent2); box-shadow:0 0 12px var(--accent2); animation:pulse 1.8s infinite; }
@keyframes pulse { 50% { opacity:.35; transform:scale(.8);} }
.hero h1 {
    font-size:clamp(38px,6vw,68px); line-height:1.03; margin:18px 0 10px; font-weight:700; letter-spacing:-.03em;
    background:linear-gradient(100deg,#fff 10%,#b7a8ff 45%,#00e5c3 90%);
    -webkit-background-clip:text; background-clip:text; color:transparent;
}
.hero p { color:#a7a3c9; font-size:17px; max-width:620px; margin:0 auto; }
.pills { display:flex; gap:10px; justify-content:center; margin-top:18px; flex-wrap:wrap; }
.pill { font-size:13px; padding:6px 12px; border-radius:10px; background:var(--card); border:1px solid var(--line); color:#cfcbff; }

/* ---------- Panels ---------- */
.panel {
    background:var(--card) !important; border:1px solid var(--line) !important; border-radius:20px !important;
    backdrop-filter: blur(14px); padding:6px !important;
}
.label-row { font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:#8f8bb8; margin:2px 0 8px 4px; }

textarea {
    background:rgba(0,0,0,.35) !important; border:1px solid var(--line) !important; color:#fff !important;
    border-radius:14px !important; font-size:17px !important; font-family:'Space Grotesk',sans-serif !important;
    line-height:1.6 !important;
}
textarea:focus { border-color:var(--accent) !important; box-shadow:0 0 0 3px rgba(124,92,255,.25) !important; }

/* ---------- Buttons ---------- */
#fix-btn {
    background:linear-gradient(100deg,var(--accent),#4f8bff 60%,var(--accent2)) !important;
    border:none !important; color:#fff !important; font-weight:700 !important; font-size:16px !important;
    border-radius:14px !important; padding:14px !important; letter-spacing:.02em;
    box-shadow:0 10px 30px -8px rgba(124,92,255,.7); transition:transform .15s, box-shadow .15s;
}
#fix-btn:hover { transform:translateY(-2px); box-shadow:0 16px 36px -8px rgba(124,92,255,.9); }
#clear-btn { background:transparent !important; border:1px solid var(--line) !important; color:#b9b4ff !important; border-radius:14px !important; }

/* ---------- Result cards ---------- */
.card { border-radius:16px; padding:16px 18px; margin-bottom:12px; border:1px solid var(--line); background:rgba(0,0,0,.28); }
.card .tag { font-size:11px; letter-spacing:.16em; text-transform:uppercase; font-weight:700; margin-bottom:8px; display:block; }
.card.orig { border-left:3px solid #ff6b8b; }
.card.orig .tag { color:#ff8fa6; }
.card.orig .txt { color:#d9d6f5; text-decoration:line-through; text-decoration-color:rgba(255,107,139,.55); font-size:17px; }
.card.ai { border-left:3px solid var(--accent2); min-height:120px; }
.card.ai .tag { color:var(--accent2); }
.card.ai .txt { color:#f1fffc; font-size:16px; line-height:1.7; white-space:pre-wrap; }
.card.empty .txt { color:#6f6b94; font-style:italic; text-decoration:none; }

.stats { display:flex; gap:10px; flex-wrap:wrap; margin-top:4px; }
.chip { font-family:'JetBrains Mono',monospace; font-size:12px; padding:5px 10px; border-radius:8px; background:rgba(124,92,255,.14); color:#cfc6ff; border:1px solid rgba(124,92,255,.3); }

.thinking { display:flex; gap:6px; align-items:center; color:#9be9dc; }
.thinking i { width:8px; height:8px; border-radius:50%; background:var(--accent2); animation:bounce 1s infinite; }
.thinking i:nth-child(2){ animation-delay:.15s } .thinking i:nth-child(3){ animation-delay:.3s }
@keyframes bounce { 0%,80%,100%{ transform:translateY(0); opacity:.4 } 40%{ transform:translateY(-7px); opacity:1 } }

/* ---------- Examples ---------- */
.examples-label { font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:#8f8bb8; margin:18px 0 4px 4px; }
table.table, .examples table { background:transparent !important; }
.gallery-item, .examples td { background:var(--card) !important; border:1px solid var(--line) !important; border-radius:10px !important; color:#cfcbff !important; }

.foot { text-align:center; color:#6f6b94; font-size:13px; padding:26px 0 10px; }
"""

HERO = """
<div class="hero">
  <span class="badge"><span class="dot"></span> Powered by Qwen2.5 · Runs on your GPU</span>
  <h1>Write it right.</h1>
  <p>Paste any sentence and get instant grammar, spelling and punctuation fixes, with simple explanations.</p>
  <div class="pills">
    <span class="pill">✍️ Grammar</span><span class="pill">🔤 Spelling</span>
    <span class="pill">❗ Punctuation</span><span class="pill">💡 Easy explanations</span>
  </div>
</div>
"""

EMPTY_ORIG = '<div class="card orig empty"><span class="tag">Original</span><div class="txt">Your sentence will appear here…</div></div>'
EMPTY_AI = '<div class="card ai empty"><span class="tag">AI Assistant</span><div class="txt" style="color:#6f6b94;font-style:italic">Corrections and explanations will appear here…</div></div>'
EMPTY_STATS = ""


def render_orig(text):
    return f'<div class="card orig"><span class="tag">Original</span><div class="txt">{html.escape(text)}</div></div>'


def render_ai(text):
    return f'<div class="card ai"><span class="tag">AI Assistant</span><div class="txt">{html.escape(text)}</div></div>'


def render_thinking():
    return ('<div class="card ai"><span class="tag">AI Assistant</span>'
            '<div class="thinking"><i></i><i></i><i></i>&nbsp; Checking your sentence…</div></div>')


def run_ui(text):
    if not text or not text.strip():
        yield EMPTY_ORIG, render_ai("Please type a sentence first."), EMPTY_STATS
        return

    yield render_orig(text), render_thinking(), EMPTY_STATS

    start = time.time()
    answer = grammar_assistant(text)          # <- your backend, untouched
    took = time.time() - start

    stats = (
        '<div class="stats">'
        f'<span class="chip">⏱ {took:.1f}s</span>'
        f'<span class="chip">📝 {len(text.split())} words in</span>'
        f'<span class="chip">🔠 {len(text)} chars</span>'
        '</div>'
    )
    yield render_orig(text), render_ai(answer), stats


def clear_ui():
    return "", EMPTY_ORIG, EMPTY_AI, EMPTY_STATS


theme = gr.themes.Base(primary_hue="violet", neutral_hue="slate")

with gr.Blocks(theme=theme, css=CSS, title="Write it right · AI Grammar Assistant") as demo:
    gr.HTML(HERO)

    with gr.Row(equal_height=False):
        with gr.Column(scale=1, elem_classes="panel"):
            gr.HTML('<div class="label-row">Your sentence</div>')
            inp = gr.Textbox(
                lines=7, show_label=False, container=False,
                placeholder="e.g. She dont like going to school becuase it are boring"
            )
            with gr.Row():
                clear_btn = gr.Button("Clear", elem_id="clear-btn", scale=1)
                fix_btn = gr.Button("✨ Fix my grammar", elem_id="fix-btn", scale=3)

        with gr.Column(scale=1, elem_classes="panel"):
            gr.HTML('<div class="label-row">Result</div>')
            out_orig = gr.HTML(EMPTY_ORIG)
            out_ai = gr.HTML(EMPTY_AI)
            out_stats = gr.HTML(EMPTY_STATS)

    gr.HTML('<div class="examples-label">Try an example</div>')
    gr.Examples(
        examples=[
            ["i has a apple and she have two oranges"],
            ["Their going to the park tomorow, weather or not it rains"],
            ["me and him goes to market yesterday"],
            ["The quick brown fox jumps over the lazy dog."],
        ],
        inputs=inp,
        label=None,
    )

    gr.HTML('<div class="foot">Built with Qwen2.5-0.5B-Instruct · Results may not always be perfect</div>')

    outputs = [out_orig, out_ai, out_stats]
    fix_btn.click(run_ui, inp, outputs)
    inp.submit(run_ui, inp, outputs)
    clear_btn.click(clear_ui, None, [inp, out_orig, out_ai, out_stats])

if __name__ == "__main__":
    demo.queue().launch()
