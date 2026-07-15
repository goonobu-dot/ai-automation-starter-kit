"""Human-first browser UI for choosing Manual Studio evidence frames."""

from __future__ import annotations

import json


def render_manual_frame_picker_ui(language: str, token: str) -> str:
    if language not in {"ja", "en"}:
        raise ValueError("language must be 'ja' or 'en'")
    copy = {
        "ja": {
            "title": "手順画像を選び直す",
            "lead": "AIが最初に選んだ画像をそのまま使う必要はありません。手元、対象物、作業結果が最も伝わる一枚を選んでください。",
            "steps": "手順",
            "candidates": "動画内の候補画像",
            "nearby": "前後の候補",
            "all": "動画全体",
            "current": "現在の画像",
            "initial": "マニュアルで現在使用中",
            "save": "選んだ画像を保存",
            "saving": "保存中",
            "saved": "マニュアルへ反映しました",
            "unchanged": "画像の変更はありません",
            "manual": "更新したマニュアルを見る",
            "previous": "前の手順",
            "next": "次の手順",
            "time": "動画時刻",
            "loading": "候補画像を読み込んでいます",
            "error": "読み込みに失敗しました。Codexへ画面の再起動を依頼してください。",
            "guide": "判断の目安",
            "guide_text": "作業者の手で重要部分が隠れていない、動作がぶれていない、作業前後の違いが分かる画像を優先します。",
            "no_image": "この手順は回答情報だけで作られているため、動画画像はありません。",
        },
        "en": {
            "title": "Choose better step images",
            "lead": "You do not have to keep the image initially selected by AI. Choose the frame that best shows the hands, work item, and result.",
            "steps": "Steps",
            "candidates": "Candidate frames from the recording",
            "nearby": "Nearby frames",
            "all": "Full recording",
            "current": "Current image",
            "initial": "Currently used in the manual",
            "save": "Save selected images",
            "saving": "Saving",
            "saved": "The manual was updated",
            "unchanged": "No image was changed",
            "manual": "View updated manual",
            "previous": "Previous step",
            "next": "Next step",
            "time": "Video time",
            "loading": "Loading candidate frames",
            "error": "The picker could not load. Ask Codex to restart this screen.",
            "guide": "What makes a useful image",
            "guide_text": "Prefer a sharp image where hands do not hide the important area and the before-or-after state is easy to understand.",
            "no_image": "This step is supported only by recorded answers, so it has no video image.",
        },
    }[language]
    template = """<!doctype html>
<html lang="__LANG__">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>__TITLE__</title>
  <style>
    :root{color-scheme:light;--ink:#172033;--muted:#596579;--bg:#f3f5f7;--paper:#fff;--line:#d6dce5;--blue:#165dff;--green:#087443;--green-soft:#e9f6ef;--amber:#8a5800;--amber-soft:#fff5d9}
    *{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.6;letter-spacing:0}
    button,a{font:inherit}.topbar{position:sticky;top:0;z-index:10;background:var(--paper);border-bottom:1px solid var(--line)}.topbar-inner{width:min(1440px,calc(100% - 32px));margin:auto;padding:18px 0;display:flex;align-items:center;justify-content:space-between;gap:18px}.topbar h1{margin:0;font-size:1.35rem}.topbar p{margin:3px 0 0;color:var(--muted);font-size:.92rem}.save{min-height:44px;padding:10px 16px;border:0;border-radius:6px;background:var(--green);color:#fff;font-weight:750;cursor:pointer}.save:disabled{opacity:.55;cursor:wait}
    .layout{width:min(1440px,calc(100% - 32px));margin:0 auto;display:grid;grid-template-columns:280px minmax(0,1fr);gap:24px;padding:28px 0 48px}.sidebar{align-self:start;position:sticky;top:108px}.sidebar h2,.workspace h2{margin:0 0 12px;font-size:1rem}.step-list{display:grid;gap:8px}.step-button{width:100%;padding:12px;text-align:left;border:1px solid var(--line);border-radius:6px;background:var(--paper);color:var(--ink);cursor:pointer}.step-button[aria-current="true"]{border-color:var(--blue);box-shadow:inset 4px 0 0 var(--blue)}.step-button strong{display:block}.step-button span{display:block;margin-top:3px;color:var(--muted);font-size:.84rem}
    .workspace{min-width:0}.intro{padding:18px 20px;border-left:5px solid var(--amber);background:var(--amber-soft);margin-bottom:22px}.intro h2{color:var(--amber)}.intro p{margin:0;color:#5b4a25}.step-heading{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin-bottom:14px}.step-heading h2{font-size:1.35rem;margin:0}.step-heading p{margin:3px 0 0;color:var(--muted)}.nav{display:flex;gap:8px}.nav button{min-height:40px;padding:8px 12px;border:1px solid var(--line);border-radius:6px;background:var(--paper);cursor:pointer}.nav button:disabled{opacity:.45;cursor:not-allowed}
    .selected-preview{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(220px,.7fr);gap:18px;margin-bottom:24px;padding-bottom:24px;border-bottom:1px solid var(--line)}.selected-preview img{display:block;width:100%;aspect-ratio:16/9;object-fit:contain;background:#111;border-radius:6px}.selected-copy{align-self:center}.selected-copy .label{color:var(--green);font-weight:800}.selected-copy h3{margin:6px 0;font-size:1.2rem}.selected-copy p{margin:5px 0;color:var(--muted)}
    .gallery-head{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:12px}.gallery-head h2{margin:0}.segmented{display:flex;padding:3px;border:1px solid var(--line);border-radius:7px;background:#e9edf2}.segmented button{min-height:36px;padding:7px 12px;border:0;border-radius:5px;background:transparent;color:var(--muted);cursor:pointer}.segmented button[aria-pressed="true"]{background:var(--paper);color:var(--ink);box-shadow:0 1px 4px rgba(23,32,51,.14)}
    .candidate-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.candidate{padding:0;border:2px solid transparent;border-radius:6px;background:var(--paper);overflow:hidden;cursor:pointer;text-align:left}.candidate:hover{border-color:#8eaae7}.candidate[aria-pressed="true"]{border-color:var(--green);box-shadow:0 0 0 2px rgba(8,116,67,.16)}.candidate img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#111}.candidate-meta{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:10px 11px}.candidate-meta strong{font-size:.88rem}.candidate-meta span{color:var(--muted);font-size:.8rem}.chosen{color:var(--green)!important;font-weight:750}
    .status{position:fixed;right:20px;bottom:20px;max-width:min(420px,calc(100% - 40px));padding:13px 16px;border-radius:6px;background:#172033;color:#fff;box-shadow:0 8px 28px rgba(23,32,51,.22)}.status.success{background:var(--green)}.status.error{background:#a2322b}.status[hidden]{display:none}.manual-link{display:inline-block;margin-top:10px;color:#fff;font-weight:750}.empty{padding:24px;background:var(--paper);border:1px solid var(--line)}
    @media(max-width:980px){.layout{grid-template-columns:1fr}.sidebar{position:static}.step-list{grid-template-columns:repeat(2,minmax(0,1fr))}.candidate-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
    @media(max-width:640px){.topbar{position:static}.topbar-inner{align-items:flex-start;flex-direction:column}.save{width:100%}.layout{padding-top:18px}.sidebar{min-width:0;overflow:hidden}.step-list{display:flex;overflow-x:auto;gap:10px;padding-bottom:8px;scroll-snap-type:x proximity}.step-button{min-width:250px;scroll-snap-align:start}.candidate-grid{grid-template-columns:1fr}.selected-preview{grid-template-columns:1fr}.step-heading,.gallery-head{align-items:flex-start;flex-direction:column}.segmented{width:100%}.segmented button{flex:1}.nav{width:100%}.nav button{flex:1}}
    @media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
  </style>
</head>
<body>
  <header class="topbar"><div class="topbar-inner"><div><h1>__TITLE__</h1><p>__LEAD__</p></div><button id="save" class="save" type="button">__SAVE__</button></div></header>
  <main class="layout">
    <aside class="sidebar"><h2>__STEPS__</h2><div id="step-list" class="step-list"></div></aside>
    <section class="workspace">
      <div class="intro"><h2>__GUIDE__</h2><p>__GUIDE_TEXT__</p></div>
      <div id="content"><p>__LOADING__</p></div>
    </section>
  </main>
  <div id="status" class="status" hidden></div>
  <script>
    const token=__TOKEN_JSON__;
    const labels=__LABELS_JSON__;
    let state=null;
    let activeIndex=0;
    let galleryMode="nearby";
    const selected={};
    const original={};
    const request=(url,options={})=>fetch(url,{...options,headers:{...(options.headers||{}),"X-Manual-Frame-Picker-Token":token}});
    const formatTime=(seconds)=>{const minutes=Math.floor(seconds/60);const remainder=(seconds-minutes*60).toFixed(1).padStart(4,"0");return `${minutes}:${remainder}`;};
    const escapeText=(value)=>String(value).replace(/[&<>"']/g,(char)=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
    function notify(message,type="success",link=false){const element=document.getElementById("status");element.className=`status ${type}`;element.innerHTML=escapeText(message)+(link?`<br><a class="manual-link" href="/manual?token=${encodeURIComponent(token)}" target="_blank" rel="noopener">${escapeText(labels.manual)}</a>`:"");element.hidden=false;window.setTimeout(()=>{element.hidden=true;},link?8000:5000);}
    function renderSteps(){const list=document.getElementById("step-list");list.innerHTML=state.steps.map((step,index)=>`<button type="button" class="step-button" data-index="${index}" aria-current="${index===activeIndex}"><strong>${step.order}. ${escapeText(step.title)}</strong><span>${step.candidates.length} ${escapeText(labels.candidates)}</span></button>`).join("");list.querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>{activeIndex=Number(button.dataset.index);render();}));}
    function render(){renderSteps();const step=state.steps[activeIndex];const content=document.getElementById("content");if(!step||!step.candidates.length){content.innerHTML=`<div class="empty">${escapeText(labels.noImage)}</div>`;return;}const chosen=selected[step.order];const chosenFrame=step.candidates.find(frame=>frame.frame_id===chosen)||step.candidates[0];const nearby=[...step.candidates].sort((a,b)=>Math.abs(a.timestamp_seconds-chosenFrame.timestamp_seconds)-Math.abs(b.timestamp_seconds-chosenFrame.timestamp_seconds)).slice(0,7).sort((a,b)=>a.timestamp_seconds-b.timestamp_seconds);const visible=galleryMode==="nearby"?nearby:step.candidates;content.innerHTML=`<div class="step-heading"><div><h2>${step.order}. ${escapeText(step.title)}</h2><p>${escapeText(step.instruction)}</p></div><div class="nav"><button id="previous" type="button" ${activeIndex===0?"disabled":""}>${escapeText(labels.previous)}</button><button id="next" type="button" ${activeIndex===state.steps.length-1?"disabled":""}>${escapeText(labels.next)}</button></div></div><div class="selected-preview"><img src="${chosenFrame.image_url}" alt="${escapeText(step.title)}"><div class="selected-copy"><span class="label">${escapeText(labels.current)}</span><h3>${escapeText(labels.time)} ${formatTime(chosenFrame.timestamp_seconds)}</h3><p>${escapeText(labels.initial)}</p></div></div><div class="gallery-head"><h2>${escapeText(labels.candidates)}</h2><div class="segmented" aria-label="${escapeText(labels.candidates)}"><button id="nearby-mode" type="button" aria-pressed="${galleryMode==="nearby"}">${escapeText(labels.nearby)} (${nearby.length})</button><button id="all-mode" type="button" aria-pressed="${galleryMode==="all"}">${escapeText(labels.all)} (${step.candidates.length})</button></div></div><div class="candidate-grid">${visible.map(frame=>`<button type="button" class="candidate" data-frame-id="${frame.frame_id}" aria-pressed="${frame.frame_id===chosen}"><img src="${frame.image_url}" alt="${escapeText(step.title)} ${formatTime(frame.timestamp_seconds)}"><span class="candidate-meta"><strong>${escapeText(labels.time)} ${formatTime(frame.timestamp_seconds)}</strong><span class="${frame.frame_id===chosen?"chosen":""}">${frame.frame_id===chosen?escapeText(labels.current):""}</span></span></button>`).join("")}</div>`;const previous=document.getElementById("previous");const next=document.getElementById("next");if(previous)previous.addEventListener("click",()=>{activeIndex-=1;galleryMode="nearby";render();});if(next)next.addEventListener("click",()=>{activeIndex+=1;galleryMode="nearby";render();});document.getElementById("nearby-mode").addEventListener("click",()=>{galleryMode="nearby";render();});document.getElementById("all-mode").addEventListener("click",()=>{galleryMode="all";render();});content.querySelectorAll(".candidate").forEach(button=>button.addEventListener("click",()=>{selected[step.order]=button.dataset.frameId;render();}));}
    async function load(){try{const response=await request("/api/state");if(!response.ok)throw new Error("load");state=await response.json();state.steps.forEach(step=>{if(step.selected_frame_id){selected[step.order]=step.selected_frame_id;original[step.order]=step.selected_frame_id;}});render();}catch(error){document.getElementById("content").innerHTML=`<div class="empty">${escapeText(labels.error)}</div>`;}}
    document.getElementById("save").addEventListener("click",async()=>{const button=document.getElementById("save");const changes=state.steps.filter(step=>selected[step.order]&&selected[step.order]!==original[step.order]).map(step=>({order:step.order,frame_id:selected[step.order]}));if(!changes.length){notify(labels.unchanged);return;}button.disabled=true;button.textContent=labels.saving;try{const response=await request("/api/selections",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({selections:changes})});const payload=await response.json();if(!response.ok||!payload.ok)throw new Error(payload.error||"save");changes.forEach(change=>{original[change.order]=change.frame_id;});notify(labels.saved,"success",true);await load();}catch(error){notify(labels.error,"error");}finally{button.disabled=false;button.textContent=labels.save;}});
    load();
  </script>
</body>
</html>"""
    replacements = {
        "__LANG__": language,
        "__TITLE__": copy["title"],
        "__LEAD__": copy["lead"],
        "__SAVE__": copy["save"],
        "__STEPS__": copy["steps"],
        "__GUIDE__": copy["guide"],
        "__GUIDE_TEXT__": copy["guide_text"],
        "__LOADING__": copy["loading"],
        "__TOKEN_JSON__": json.dumps(token),
        "__LABELS_JSON__": json.dumps(copy, ensure_ascii=False).replace("</", "<\\/"),
    }
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    return template


__all__ = ["render_manual_frame_picker_ui"]
