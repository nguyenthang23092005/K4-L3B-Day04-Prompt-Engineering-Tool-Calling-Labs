from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import run_model_tool_loop, trim_history

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)


HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Northstar Desk</title>
<style>
:root{--ink:#14211f;--muted:#6f7d78;--line:#dce5df;--paper:#f6f8f5;--panel:#fff;--teal:#0e6b62;--teal-dark:#0a514b;--mint:#d9efe7;--amber:#b46a24;--shadow:0 18px 50px rgba(20,33,31,.08)}
*{box-sizing:border-box}body{margin:0;color:var(--ink);font-family:Georgia,'Times New Roman',serif;background:var(--paper)}button,input,select,textarea{font:inherit}button{cursor:pointer}
.app{min-height:100vh;display:grid;grid-template-columns:270px minmax(0,1fr);background:linear-gradient(135deg,#f7faf7 0%,#eef5f0 55%,#f9f5ed 100%)}
.sidebar{padding:28px 20px;border-right:1px solid var(--line);background:rgba(255,255,255,.7);backdrop-filter:blur(18px);display:flex;flex-direction:column;gap:28px}.brand{display:flex;align-items:center;gap:12px}.mark{width:38px;height:38px;border-radius:11px;background:var(--teal);color:white;display:grid;place-items:center;font:700 18px/1 Arial}.brand strong{font-size:20px;letter-spacing:-.4px}.brand small{display:block;color:var(--muted);font:12px Arial;margin-top:3px}.side-label{font:11px Arial;text-transform:uppercase;letter-spacing:1.4px;color:var(--muted);margin:0 0 9px}.context{padding:14px;border:1px solid var(--line);background:#fff;border-radius:12px}.context-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;font:13px Arial;border-bottom:1px solid #edf1ed}.context-row:last-child{border:0}.context-row span{color:var(--muted)}.dot{width:8px;height:8px;border-radius:50%;background:#4aa879;display:inline-block;margin-right:7px}.tip{margin-top:auto;padding:16px;border-radius:12px;background:#173c38;color:#e7f3ed;font:13px/1.55 Arial}.tip b{display:block;margin-bottom:7px;color:#fff}.new-chat{width:100%;border:1px solid var(--teal);background:var(--teal);color:#fff;border-radius:9px;padding:11px 14px;text-align:left;font:600 13px Arial}.new-chat:hover{background:var(--teal-dark)}
.main{min-width:0;display:flex;flex-direction:column;min-height:100vh}.topbar{height:82px;padding:20px 38px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,.4)}.eyebrow{font:11px Arial;text-transform:uppercase;letter-spacing:1.6px;color:var(--teal);font-weight:700}.topbar h1{font-size:25px;margin:5px 0 0;letter-spacing:-.7px}.status{font:12px Arial;color:var(--muted);display:flex;align-items:center;gap:8px}.status i{width:8px;height:8px;background:#4aa879;border-radius:50%;display:block}.conversation{width:min(900px,100%);margin:0 auto;padding:34px 38px 150px;flex:1}.welcome{padding:20px 0 25px;border-bottom:1px solid var(--line);margin-bottom:27px}.welcome h2{font-size:32px;line-height:1.05;margin:0 0 10px;letter-spacing:-1px}.welcome p{font:14px/1.6 Arial;color:var(--muted);max-width:610px;margin:0}.suggestions{display:flex;flex-wrap:wrap;gap:8px;margin-top:19px}.suggestion{border:1px solid var(--line);background:rgba(255,255,255,.75);border-radius:20px;padding:8px 12px;color:var(--teal-dark);font:12px Arial}.suggestion:hover{border-color:var(--teal);background:#fff}.message{display:flex;gap:12px;margin:22px 0;animation:rise .3s ease both}.message.user{justify-content:flex-end}.avatar{width:30px;height:30px;border-radius:9px;background:var(--mint);color:var(--teal-dark);display:grid;place-items:center;flex:none;font:700 12px Arial}.message.user .avatar{order:2;background:var(--teal);color:#fff}.bubble{max-width:76%;padding:14px 16px;border:1px solid var(--line);border-radius:4px 15px 15px 15px;background:#fff;box-shadow:0 6px 18px rgba(20,33,31,.035);font:14px/1.55 Arial;white-space:pre-wrap}.message.user .bubble{border:0;border-radius:15px 4px 15px 15px;background:var(--teal);color:#fff}.tool-card{margin:8px 0 8px 42px;border:1px solid #cfe4db;border-left:3px solid var(--teal);border-radius:9px;background:#f8fcfa;padding:12px 14px;font:12px Arial}.tool-head{display:flex;justify-content:space-between;color:var(--teal-dark);font-weight:700}.tool-meta{color:var(--muted);margin-top:6px;white-space:pre-wrap}.error{border-left-color:var(--amber);background:#fff8f0}.typing{display:inline-flex;gap:4px;padding:7px}.typing i{width:5px;height:5px;background:var(--teal);border-radius:50%;animation:pulse 1s infinite}.typing i:nth-child(2){animation-delay:.15s}.typing i:nth-child(3){animation-delay:.3s}
.composer-wrap{position:fixed;bottom:0;left:270px;right:0;padding:18px 38px 24px;background:linear-gradient(transparent,var(--paper) 30%)}.composer{max-width:900px;margin:auto;display:flex;align-items:flex-end;gap:10px;padding:9px;border:1px solid #cbd9d1;border-radius:14px;background:#fff;box-shadow:var(--shadow)}textarea{resize:none;border:0;outline:0;flex:1;min-height:42px;max-height:130px;padding:10px 9px;color:var(--ink);font:14px/1.5 Arial}textarea::placeholder{color:#9aa8a1}.send{width:42px;height:42px;border:0;border-radius:10px;background:var(--teal);color:white;font:700 18px Arial}.send:disabled{opacity:.45;cursor:wait}.composer-note{max-width:900px;margin:8px auto 0;color:var(--muted);font:10px Arial;text-align:right}
@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}@keyframes pulse{0%,100%{opacity:.3}50%{opacity:1}}
@media(max-width:760px){.app{display:block}.sidebar{display:none}.topbar{height:72px;padding:16px 20px}.conversation{padding:25px 18px 145px}.welcome h2{font-size:28px}.bubble{max-width:88%}.composer-wrap{left:0;padding:14px 14px 18px}.status{display:none}}
</style>
</head>
<body>
<div class="app">
<aside class="sidebar">
  <div class="brand"><div class="mark">N</div><div><strong>Northstar</strong><small>IT service desk</small></div></div>
  <button class="new-chat" id="newChat">+ New conversation</button>
  <div><p class="side-label">Session</p><div class="context"><div class="context-row"><span>Provider</span><b id="providerLabel">Gemini</b></div><div class="context-row"><span>Prompt</span><b id="versionLabel">v1</b></div><div class="context-row"><span>Artifact</span><b id="artifactLabel">loading</b></div></div></div>
  <div><p class="side-label">Suggested routes</p><div class="context"><div class="context-row"><span>Service status</span><b>→</b></div><div class="context-row"><span>Device diagnosis</span><b>→</b></div><div class="context-row"><span>Knowledge base</span><b>→</b></div></div></div>
  <div class="tip"><b>Evidence first</b>Every answer shows the tools used and the source events behind it.</div>
</aside>
<main class="main">
<header class="topbar"><div><div class="eyebrow">Operations console</div><h1>Helpdesk assistant</h1></div><div class="status"><i></i><span id="statusText">Ready for requests</span></div></header>
<section class="conversation" id="conversation"><div class="welcome" id="welcome"><h2>What can we resolve?</h2><p>Ask about a service, a device, or an internal support guide. I will gather the right evidence before answering.</p><div class="suggestions"><button class="suggestion">Is VPN production healthy?</button><button class="suggestion">Check LT-204 network</button><button class="suggestion">Find the Windows Wi-Fi guide</button></div></div></section>
<div class="composer-wrap"><form class="composer" id="chatForm"><textarea id="input" rows="1" placeholder="Describe the issue or request..." aria-label="Message"></textarea><button class="send" id="send" aria-label="Send message">↑</button></form><div class="composer-note">Northstar internal assistant · tool activity is logged to the transcript</div></div>
</main></div>
<script>
const conversation=document.querySelector('#conversation'), input=document.querySelector('#input'), form=document.querySelector('#chatForm'), send=document.querySelector('#send'), statusText=document.querySelector('#statusText');
let history=[];
function addMessage(role,text){const row=document.createElement('div');row.className='message '+role;row.innerHTML='<div class="avatar">'+(role==='user'?'You':'N')+'</div><div class="bubble"></div>';row.querySelector('.bubble').textContent=text;conversation.appendChild(row);row.scrollIntoView({behavior:'smooth',block:'nearest'});return row}
function addTool(event){const card=document.createElement('div');card.className='tool-card '+(event.result&&event.result.error?'error':'');const detail=JSON.stringify(event.args||{},null,2);card.innerHTML='<div class="tool-head"><span>Tool call · '+event.tool+'</span><span>'+(event.result&&event.result.error?'Attention':'Complete')+'</span></div><div class="tool-meta">'+detail.replaceAll('<','&lt;')+'</div>';conversation.appendChild(card)}
function setBusy(value){send.disabled=value;statusText.textContent=value?'Gathering evidence...':'Ready for requests'}
async function submit(text){text=(text||input.value).trim();if(!text||send.disabled)return;if(document.querySelector('#welcome'))document.querySelector('#welcome').remove();addMessage('user',text);input.value='';input.style.height='auto';setBusy(true);const loading=addMessage('assistant','');loading.querySelector('.bubble').innerHTML='<span class="typing"><i></i><i></i><i></i></span>';try{const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text,history})});const data=await res.json();loading.remove();if(data.tool_events) data.tool_events.forEach(addTool);addMessage('assistant',data.assistant_text||data.error||'No response returned.');history.push({role:'user',content:text},{role:'assistant',content:data.assistant_text||''});}catch(err){loading.remove();addMessage('assistant','The service could not complete this request. Check the provider configuration and try again.');}finally{setBusy(false)}}
form.addEventListener('submit',e=>{e.preventDefault();submit()});input.addEventListener('input',()=>{input.style.height='auto';input.style.height=Math.min(input.scrollHeight,130)+'px'});input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();submit()}});document.querySelectorAll('.suggestion').forEach(b=>b.addEventListener('click',()=>submit(b.textContent)));document.querySelector('#newChat').addEventListener('click',()=>{history=[];conversation.innerHTML='<div class="welcome" id="welcome"><h2>What can we resolve?</h2><p>Ask about a service, a device, or an internal support guide. I will gather the right evidence before answering.</p></div>'});
fetch('/api/session').then(r=>r.json()).then(d=>{document.querySelector('#providerLabel').textContent=d.provider;document.querySelector('#versionLabel').textContent=d.version;document.querySelector('#artifactLabel').textContent=d.artifact_version.split('+')[1].slice(0,8)}).catch(()=>{});
</script>
</body></html>'''


class Handler(BaseHTTPRequestHandler):
    server_version = "NorthstarDesk/1.0"

    def __init__(self, *args, app_config: dict[str, Any], **kwargs):
        self.app_config = app_config
        super().__init__(*args, **kwargs)

    def _send(self, payload: Any, status: int = 200, content_type: str = "application/json") -> None:
        body = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self._send(HTML.encode("utf-8"), content_type="text/html")
        elif path == "/api/session":
            self._send(self.app_config["session"])
        else:
            self._send({"error": "Not found"}, 404)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/chat":
            self._send({"error": "Not found"}, 404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(size) or b"{}")
            message = str(data.get("message", "")).strip()
            if not message:
                raise ValueError("message is required")
            history = data.get("history", [])
            messages = [{"role": "system", "content": self.app_config["system_prompt"]}]
            messages.extend(trim_history(history, self.app_config["history_window"]))
            messages.append({"role": "user", "content": message})
            result = run_model_tool_loop(provider=self.app_config["provider_obj"], messages=messages, tools=self.app_config["tools"], model=self.app_config["model"], max_tool_rounds=4)
            self._send(result)
        except Exception as exc:
            self._send({"error": f"{type(exc).__name__}: {exc}", "tool_events": []}, 500)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Northstar Desk web chat")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini"], default="gemini")
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", default="v1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    provider_obj = make_provider(args.provider)
    declarations = load_tool_declarations(tools_path)
    artifact_version = build_artifact_version(args.version, prompt_path, tools_path)
    session = {"provider": args.provider, "model": args.model or getattr(provider_obj, "default_model", None), "version": args.version, **artifact_version_dict(artifact_version)}
    config = {"provider_obj": provider_obj, "model": args.model, "tools": to_openai_tools(declarations), "system_prompt": prompt_path.read_text(encoding="utf-8"), "history_window": 5, "session": session}
    server = ThreadingHTTPServer(("127.0.0.1", args.port), lambda *a, **kw: Handler(*a, app_config=config, **kw))
    print(f"Northstar Desk running at http://127.0.0.1:{args.port}")
    print(f"artifact_version={artifact_version.artifact_version}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
