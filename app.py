import re
import os
import json
from flask import Flask, request, jsonify, send_file
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

THEMES = {
    'dark': {
        'bg': 'linear-gradient(135deg, #0f0c29, #302b63, #24243e)',
        'card': 'rgba(255,255,255,0.07)',
        'text': 'white',
        'subtext': 'rgba(255,255,255,0.55)',
        'border': 'rgba(255,255,255,0.15)',
        'input_bg': 'rgba(255,255,255,0.08)',
        'input_border': 'rgba(255,255,255,0.12)',
        'input_text': 'white',
        'result_bg': 'white',
        'result_text': '#1a1a2e',
        'primary': '#a855f7',
        'gradient': 'linear-gradient(135deg, #a855f7, #ec4899)',
    },
    'white': {
        'bg': 'linear-gradient(135deg, #f0f4ff, #e8eaf6, #f3e5f5)',
        'card': 'rgba(255,255,255,0.95)',
        'text': '#1a1a2e',
        'subtext': '#666',
        'border': 'rgba(0,0,0,0.1)',
        'input_bg': '#f8f9ff',
        'input_border': '#ddd',
        'input_text': '#1a1a2e',
        'result_bg': '#f8f9ff',
        'result_text': '#1a1a2e',
        'primary': '#6c3fc5',
        'gradient': 'linear-gradient(135deg, #6c3fc5, #c2185b)',
    },
    'black': {
        'bg': '#000000',
        'card': '#111111',
        'text': 'white',
        'subtext': '#888',
        'border': '#222',
        'input_bg': '#1a1a1a',
        'input_border': '#333',
        'input_text': 'white',
        'result_bg': '#1a1a1a',
        'result_text': '#eee',
        'primary': '#ffffff',
        'gradient': 'linear-gradient(135deg, #ffffff, #aaaaaa)',
    },
    'purple': {
        'bg': 'linear-gradient(135deg, #1a0533, #2d1b69, #0f0c29)',
        'card': 'rgba(255,255,255,0.07)',
        'text': 'white',
        'subtext': 'rgba(255,255,255,0.55)',
        'border': 'rgba(255,255,255,0.15)',
        'input_bg': 'rgba(255,255,255,0.08)',
        'input_border': 'rgba(255,255,255,0.12)',
        'input_text': 'white',
        'result_bg': 'white',
        'result_text': '#1a1a2e',
        'primary': '#a855f7',
        'gradient': 'linear-gradient(135deg, #a855f7, #7c3aed)',
    },
    'ocean': {
        'bg': 'linear-gradient(135deg, #0f2027, #203a43, #2c5364)',
        'card': 'rgba(255,255,255,0.07)',
        'text': 'white',
        'subtext': 'rgba(255,255,255,0.55)',
        'border': 'rgba(255,255,255,0.15)',
        'input_bg': 'rgba(255,255,255,0.08)',
        'input_border': 'rgba(255,255,255,0.12)',
        'input_text': 'white',
        'result_bg': 'white',
        'result_text': '#1a1a2e',
        'primary': '#00b4d8',
        'gradient': 'linear-gradient(135deg, #00b4d8, #0077b6)',
    },
    'forest': {
        'bg': 'linear-gradient(135deg, #0a1628, #0d2137, #0a1628)',
        'card': 'rgba(255,255,255,0.07)',
        'text': 'white',
        'subtext': 'rgba(255,255,255,0.55)',
        'border': 'rgba(255,255,255,0.15)',
        'input_bg': 'rgba(255,255,255,0.08)',
        'input_border': 'rgba(255,255,255,0.12)',
        'input_text': 'white',
        'result_bg': 'white',
        'result_text': '#1a1a2e',
        'primary': '#10b981',
        'gradient': 'linear-gradient(135deg, #10b981, #34d399)',
    },
    'sunset': {
        'bg': 'linear-gradient(135deg, #1a0000, #3d0000, #1a0000)',
        'card': 'rgba(255,255,255,0.07)',
        'text': 'white',
        'subtext': 'rgba(255,255,255,0.55)',
        'border': 'rgba(255,255,255,0.15)',
        'input_bg': 'rgba(255,255,255,0.08)',
        'input_border': 'rgba(255,255,255,0.12)',
        'input_text': 'white',
        'result_bg': 'white',
        'result_text': '#1a1a2e',
        'primary': '#ff6b35',
        'gradient': 'linear-gradient(135deg, #ff6b35, #f7c59f)',
    },
    'gold': {
        'bg': 'linear-gradient(135deg, #1a1200, #2d2000, #1a1200)',
        'card': 'rgba(255,255,255,0.07)',
        'text': 'white',
        'subtext': 'rgba(255,255,255,0.55)',
        'border': 'rgba(255,255,255,0.15)',
        'input_bg': 'rgba(255,255,255,0.08)',
        'input_border': 'rgba(255,255,255,0.12)',
        'input_text': 'white',
        'result_bg': 'white',
        'result_text': '#1a1a2e',
        'primary': '#f59e0b',
        'gradient': 'linear-gradient(135deg, #f59e0b, #fcd34d)',
    },
}

THEME_ICONS = {
    'dark': '🌙', 'white': '☀️', 'black': '🖤',
    'purple': '💜', 'ocean': '🌊', 'forest': '🌿',
    'sunset': '🌅', 'gold': '✨',
}

LANGUAGES = {
    'en': {'name': '🇬🇧 English', 'dir': 'ltr',
           'prompt': 'You are a professional CV writer. Improve this CV in English only. Use professional language, strong action verbs, and quantifiable achievements.'},
    'ar': {'name': '🇸🇦 Arabic', 'dir': 'rtl',
           'prompt': 'You are a professional CV writer. Improve this CV in Arabic only. Use professional language and strong action verbs.'},
    'fr': {'name': '🇫🇷 French', 'dir': 'ltr',
           'prompt': 'You are a professional CV writer. Improve this CV in French only. Use professional language and strong action verbs.'},
    'es': {'name': '🇪🇸 Spanish', 'dir': 'ltr',
           'prompt': 'You are a professional CV writer. Improve this CV in Spanish only. Use professional language and strong action verbs.'},
    'de': {'name': '🇩🇪 German', 'dir': 'ltr',
           'prompt': 'You are a professional CV writer. Improve this CV in German only. Use professional language and strong action verbs.'},
    'it': {'name': '🇮🇹 Italian', 'dir': 'ltr',
           'prompt': 'You are a professional CV writer. Improve this CV in Italian only. Use professional language and strong action verbs.'},
    'pt': {'name': '🇧🇷 Portuguese', 'dir': 'ltr',
           'prompt': 'You are a professional CV writer. Improve this CV in Portuguese only. Use professional language and strong action verbs.'},
    'ru': {'name': '🇷🇺 Russian', 'dir': 'ltr',
           'prompt': 'You are a professional CV writer. Improve this CV in Russian only. Use professional language and strong action verbs.'},
    'tr': {'name': '🇹🇷 Turkish', 'dir': 'ltr',
           'prompt': 'You are a professional CV writer. Improve this CV in Turkish only. Use professional language and strong action verbs.'},
    'zh': {'name': '🇨🇳 Chinese', 'dir': 'ltr',
           'prompt': 'You are a professional CV writer. Improve this CV in Chinese only. Use professional language and strong action verbs.'},
    'ja': {'name': '🇯🇵 Japanese', 'dir': 'ltr',
           'prompt': 'You are a professional CV writer. Improve this CV in Japanese only. Use professional language and strong action verbs.'},
    'ko': {'name': '🇰🇷 Korean', 'dir': 'ltr',
           'prompt': 'You are a professional CV writer. Improve this CV in Korean only. Use professional language and strong action verbs.'},
}

CV_TYPES = {
    'tech': '💻 Technology',
    'business': '💼 Business',
    'medical': '🏥 Medical',
    'creative': '🎨 Creative',
    'engineering': '⚙️ Engineering',
    'education': '📚 Education',
    'legal': '⚖️ Legal',
    'finance': '💰 Finance',
}

def format_result(text):
    lines = text.split('\n')
    result = []
    counter = 1
    for line in lines:
        line = line.strip()
        if not line:
            result.append('<br>')
            counter = 1
            continue
        if re.match(r'^#{1,6}\s', line):
            title = re.sub(r'^#{1,6}\s*', '', line)
            title = re.sub(r'\*\*(.*?)\*\*', r'\1', title)
            result.append(f'<h3>{title}</h3>')
            counter = 1
        elif line.startswith('-') or line.startswith('•'):
            content = re.sub(r'^[-•]\s*', '', line)
            content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
            result.append(
                f'<div class="item">'
                f'<span class="num">{counter}</span>'
                f'<span class="text">{content}</span>'
                f'</div>'
            )
            counter += 1
        elif re.match(r'^\*\*.*\*\*$', line):
            content = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            result.append(f'<h3>{content}</h3>')
            counter = 1
        else:
            content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            result.append(f'<p>{content}</p>')
    return '\n'.join(result)

@app.route('/manifest.json')
def manifest():
    with open('manifest.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/service-worker.js')
def service_worker():
    return send_file('static/service-worker.js',
                     mimetype='application/javascript')

@app.route('/static/icons/<filename>')
def icons(filename):
    return send_file(f'static/icons/{filename}',
                     mimetype='image/png')

@app.route('/')
def home():
    theme_name = request.args.get('theme', 'dark')
    theme = THEMES.get(theme_name, THEMES['dark'])

    lang_options = ''.join(
        f'<option value="{c}" {"selected" if c == "en" else ""}>{i["name"]}</option>'
        for c, i in LANGUAGES.items()
    )
    type_options = ''.join(
        f'<option value="{c}">{l}</option>'
        for c, l in CV_TYPES.items()
    )
    theme_buttons = ''.join(
        f'''<a href="/?theme={c}" title="{c}" style="
            display:inline-flex;
            align-items:center;
            justify-content:center;
            width:28px; height:28px;
            border-radius:50%;
            background:{THEMES[c]["gradient"]};
            margin:2px;
            font-size:12px;
            border:{"3px solid white" if c == theme_name else "2px solid transparent"};
            box-shadow:{"0 0 8px " + THEMES[c]["primary"] if c == theme_name else "none"};
            text-decoration:none;
        ">{THEME_ICONS[c]}</a>'''
        for c in THEMES
    )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV Pro AI — Professional CV Builder</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#a855f7">
    <meta name="description" content="AI-powered CV builder. Get a professional CV in seconds. Supports 12 languages.">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="CV Pro AI">
    <link rel="apple-touch-icon" href="/static/icons/icon-192.png">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            font-family: "Poppins", sans-serif;
            background: {theme["bg"]};
            min-height: 100vh;
            padding: 20px;
        }}
        .card {{
            background: {theme["card"]};
            backdrop-filter: blur(20px);
            border: 1px solid {theme["border"]};
            border-radius: 28px;
            padding: 28px;
            max-width: 480px;
            margin: 0 auto;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        }}
        .top-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .badge {{
            background: {theme["gradient"]};
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        h1 {{
            color: {theme["text"]};
            font-size: 26px;
            margin-bottom: 6px;
            font-weight: 700;
            text-align: center;
            letter-spacing: -0.5px;
        }}
        .subtitle {{
            color: {theme["subtext"]};
            font-size: 13px;
            margin-bottom: 22px;
            text-align: center;
            font-weight: 500;
            line-height: 1.5;
        }}
        .divider {{
            height: 1px;
            background: {theme["border"]};
            margin: 18px 0;
        }}
        label {{
            color: {theme["text"]};
            font-size: 13px;
            font-weight: 600;
            display: block;
            margin-bottom: 6px;
            margin-top: 14px;
        }}
        select, textarea {{
            width: 100%;
            background: {theme["input_bg"]};
            border: 1.5px solid {theme["input_border"]};
            border-radius: 14px;
            padding: 12px 14px;
            color: {theme["input_text"]};
            font-size: 14px;
            font-family: "Poppins", sans-serif;
            font-weight: 500;
            outline: none;
            transition: border 0.3s;
        }}
        select:focus, textarea:focus {{
            border-color: {theme["primary"]};
        }}
        select option {{ background: #1a1a2e; color: white; }}
        textarea {{
            height: 170px;
            resize: none;
            line-height: 1.7;
        }}
        .row {{ display: flex; gap: 10px; }}
        .row > div {{ flex: 1; }}
        button {{
            width: 100%;
            padding: 16px;
            background: {theme["gradient"]};
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 16px;
            font-weight: 700;
            font-family: "Poppins", sans-serif;
            margin-top: 18px;
            cursor: pointer;
            letter-spacing: 0.5px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.25);
            transition: transform 0.2s;
        }}
        button:active {{ transform: scale(0.98); }}
        .footer {{
            text-align: center;
            color: {theme["subtext"]};
            font-size: 11px;
            margin-top: 20px;
            opacity: 0.7;
            line-height: 1.8;
        }}
        .whatsapp-btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 18px;
            background: #25D366;
            color: white;
            border-radius: 20px;
            font-weight: 600;
            font-size: 12px;
            text-decoration: none;
            margin-top: 10px;
        }}
        .install-banner {{
            background: {theme["primary"]}22;
            border: 1px solid {theme["primary"]}44;
            border-radius: 14px;
            padding: 12px 16px;
            margin-bottom: 18px;
            text-align: center;
            color: {theme["text"]};
            font-size: 12px;
            font-weight: 500;
            display: none;
        }}
    </style>
    <script>
        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', () => {{
                navigator.serviceWorker.register('/service-worker.js')
                    .then(reg => console.log('SW registered'))
                    .catch(err => console.log('SW error:', err));
            }});
        }}

        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            document.getElementById('install-banner').style.display = 'block';
        }});

        function installApp() {{
            if (deferredPrompt) {{
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((result) => {{
                    if (result.outcome === 'accepted') {{
                        document.getElementById('install-banner').style.display = 'none';
                    }}
                    deferredPrompt = null;
                }});
            }}
        }}
    </script>
</head>
<body>
<div class="card">
    <div class="top-bar">
        <div class="badge">✨ AI Powered</div>
        <div>{theme_buttons}</div>
    </div>

    <div class="install-banner" id="install-banner">
        📱 Install CV Pro AI on your phone!
        <br>
        <button onclick="installApp()" style="
            width:auto; padding:6px 16px;
            font-size:12px; margin-top:8px;
            border-radius:20px;
        ">Install App</button>
    </div>

    <h1>🚀 CV Pro AI</h1>
    <p class="subtitle">
        Transform your CV into a professional masterpiece<br>
        in seconds — powered by AI
    </p>

    <div class="divider"></div>

    <form method="POST" action="/improve">
        <input type="hidden" name="theme" value="{theme_name}">
        <div class="row">
            <div>
                <label>🌍 Language</label>
                <select name="lang">{lang_options}</select>
            </div>
            <div>
                <label>💼 Field</label>
                <select name="cv_type">{type_options}</select>
            </div>
        </div>
        <label>📄 Paste Your CV Here</label>
        <textarea name="cv"
            placeholder="Paste your current CV here and let AI transform it into a professional masterpiece..."></textarea>
        <button type="submit">🚀 Improve My CV Now — It's Free!</button>
    </form>

    <div class="footer">
        CV Pro AI • 12 Languages • 8 Themes • 8 Fields
        <br>Powered by Groq & Llama 3.3 • Made with ❤️
        <br>
        <a href="https://wa.me/213555123456"
           target="_blank" class="whatsapp-btn">
            📱 Contact Support on WhatsApp
        </a>
    </div>
</div>
</body>
</html>'''

@app.route('/improve', methods=['POST'])
def improve():
    cv_text = request.form['cv']
    lang = request.form.get('lang', 'en')
    cv_type = request.form.get('cv_type', 'tech')
    theme_name = request.form.get('theme', 'dark')
    theme = THEMES.get(theme_name, THEMES['dark'])
    lang_info = LANGUAGES.get(lang, LANGUAGES['en'])
    type_label = CV_TYPES.get(cv_type, '')
    direction = lang_info['dir']

    prompt = f"""{lang_info['prompt']}
Field: {type_label}

Strict Rules:
1. Use the selected language ONLY — no mixing of languages
2. No foreign characters, symbols, or emojis in the CV content
3. Follow this professional structure:
   ## Professional Summary
   ## Contact Information
   ## Work Experience
   ## Skills
   ## Education
   ## Additional Information
4. Use strong action verbs (Led, Built, Achieved, Improved...)
5. Add measurable achievements with numbers and percentages
6. Keep it concise, impactful, and ATS-friendly
7. Format each section clearly with numbered points"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": cv_text}
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    result = format_result(response.choices[0].message.content)

    return f'''<!DOCTYPE html>
<html lang="en" dir="{direction}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV Pro AI — Your Improved CV</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            font-family: "Poppins", sans-serif;
            background: {theme["bg"]};
            min-height: 100vh;
            padding: 20px;
        }}
        .card {{
            background: {theme["card"]};
            backdrop-filter: blur(20px);
            border: 1px solid {theme["border"]};
            border-radius: 28px;
            padding: 28px;
            max-width: 480px;
            margin: 0 auto;
        }}
        .header {{ text-align: center; margin-bottom: 20px; }}
        .badge {{
            display: inline-block;
            background: {theme["gradient"]};
            color: white;
            padding: 5px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        }}
        .header h2 {{
            color: {theme["text"]};
            font-size: 20px;
            font-weight: 700;
        }}
        .header p {{
            color: {theme["subtext"]};
            font-size: 12px;
            margin-top: 4px;
        }}
        .result {{
            background: {theme["result_bg"]};
            border-radius: 18px;
            padding: 22px;
            color: {theme["result_text"]};
            direction: {direction};
        }}
        .result h3 {{
            color: {theme["primary"]};
            font-size: 14px;
            font-weight: 700;
            margin: 18px 0 10px;
            padding: 8px 14px;
            background: {theme["primary"]}15;
            border-left: 4px solid {theme["primary"]};
            border-radius: 8px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        .result .item {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin: 8px 0;
            padding: 10px 12px;
            background: {theme["primary"]}08;
            border-radius: 10px;
        }}
        .result .num {{
            background: {theme["gradient"]};
            color: white;
            min-width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 700;
            flex-shrink: 0;
        }}
        .result .text {{
            font-size: 13.5px;
            line-height: 1.7;
            font-weight: 500;
            color: {theme["result_text"]};
        }}
        .result p {{
            font-size: 13.5px;
            line-height: 1.8;
            margin: 6px 0;
            font-weight: 500;
            padding: 0 4px;
        }}
        .result b {{
            font-weight: 700;
            color: {theme["primary"]};
        }}
        .actions {{
            display: flex;
            gap: 10px;
            margin-top: 18px;
        }}
        .btn {{
            flex: 1;
            padding: 14px;
            border-radius: 14px;
            text-align: center;
            font-weight: 700;
            font-size: 14px;
            font-family: "Poppins", sans-serif;
            text-decoration: none;
            border: none;
            cursor: pointer;
            transition: transform 0.2s;
            letter-spacing: 0.3px;
        }}
        .btn:active {{ transform: scale(0.97); }}
        .btn-back {{
            background: {theme["input_bg"]};
            border: 1px solid {theme["border"]};
            color: {theme["text"]};
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }}
        .btn-copy {{
            background: {theme["gradient"]};
            color: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .footer {{
            text-align: center;
            color: {theme["subtext"]};
            font-size: 10px;
            margin-top: 16px;
            opacity: 0.6;
        }}
    </style>
</head>
<body>
<div class="card">
    <div class="header">
        <div class="badge">✨ AI Enhanced</div>
        <h2>Your Professional CV is Ready! 🎯</h2>
        <p>Review, copy, and start applying for jobs</p>
    </div>
    <div class="result" id="result">{result}</div>
    <div class="actions">
        <a href="/?theme={theme_name}" class="btn btn-back">
            ← Back
        </a>
        <button class="btn btn-copy"
            onclick="navigator.clipboard.writeText(
            document.getElementById('result').innerText)
            .then(()=>alert('✅ CV copied to clipboard! Ready to paste.'))">
            📋 Copy CV
        </button>
    </div>
    <div class="footer">
        CV Pro AI • Powered by Groq & Llama 3.3 • Made with ❤️
    </div>
</div>
</body>
</html>'''

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
