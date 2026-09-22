from __future__ import annotations

import argparse
import io
import json
import os
import secrets
import tempfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from beastui.api_client import BeastAPI
from beastui.responsive import render_responsive_board
from beastui.engine import BeastUI
from beastui.theme import load_theme
from beastui.customization import (
    validate_dashboard_widgets, scalar_catalog, dashboard_history_keys, WIDGET_STYLES,
    validate_context_decks, validate_palette_overrides, validate_correlation_keys, validate_custom_boards,
    PALETTE_SLOTS, DEFAULT_CONTEXT_DECKS, MAX_DASHBOARD_WIDGETS,
)
from beastui.apps import AppRegistry
from .action_client import BeastActionClient
from .library_files import LibraryFileManager, LibraryFileError


HTML=r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Beast Studio</title><style>
:root{--bg:#070b10;--panel:#0e151e;--panel2:#121d28;--edge:#223749;--ink:#dceef4;--muted:#78909e;--accent:#35e6d0;--info:#65bfff;--warn:#ffbd57;--danger:#ff6b78;--ok:#79e395}
*{box-sizing:border-box}html,body{height:100%}body{margin:0;background:linear-gradient(145deg,#06090d,#0a1018);color:var(--ink);font:14px system-ui,-apple-system,Segoe UI,sans-serif;overflow:hidden}
header{height:58px;display:flex;align-items:center;padding:0 18px;border-bottom:1px solid var(--edge);background:#091019;gap:14px}header b{font-size:20px;letter-spacing:.08em;color:var(--accent)}header .sub{color:var(--muted)}#conn{margin-left:auto;font-size:12px;border:1px solid var(--edge);padding:5px 10px;border-radius:999px;color:var(--ok)}
main{display:grid;grid-template-columns:330px minmax(520px,1fr) 300px;height:calc(100vh - 58px)}aside{border-right:1px solid var(--edge);background:#0a1119;overflow:auto}.right{border-right:0;border-left:1px solid var(--edge)}.nav{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;padding:10px;position:sticky;top:0;background:#0a1119;z-index:2;border-bottom:1px solid var(--edge)}.tab{border:1px solid var(--edge);background:#0d1720;color:var(--muted);padding:8px;border-radius:8px;cursor:pointer}.tab.active{color:#04110f;background:var(--accent);border-color:var(--accent);font-weight:800}.section{padding:14px}.section.hidden{display:none}h3{margin:0 0 10px;font-size:12px;letter-spacing:.09em;color:var(--accent)}label{display:block;color:var(--muted);font-size:11px;margin:9px 0 4px}select,input,button{width:100%;background:#081019;color:var(--ink);border:1px solid var(--edge);border-radius:7px;padding:8px;font:inherit}input{padding:7px}button{cursor:pointer}button:hover{border-color:#476984}.primary{background:var(--accent);color:#04110f;border-color:var(--accent);font-weight:800}.row{display:grid;grid-template-columns:1fr 1fr;gap:7px}.group{border-top:1px solid var(--edge);padding-top:12px;margin-top:12px}
.preview{display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding:18px;background:radial-gradient(circle at 50% 12%,#142534,#06090e 67%);overflow:auto}.device{width:min(100%,960px);position:relative;margin-top:20px}.screenWrap{position:relative;width:100%}.deviceBadge{position:absolute;top:-24px;left:0;color:var(--muted);font-size:11px;letter-spacing:.08em}#screen{display:block;width:100%;aspect-ratio:3/2;object-fit:contain;border:1px solid #45657a;border-radius:9px;box-shadow:0 20px 55px #000a;background:#000}#layoutOverlay{position:absolute;inset:0;pointer-events:none}.layoutBox{position:absolute;border:2px solid var(--accent);background:#35e6d018;border-radius:5px;pointer-events:auto;cursor:move;user-select:none}.layoutBox.selected{border-color:var(--warn);background:#ffbd5720}.layoutBox.hiddenWidget{border-style:dashed;opacity:.55}.layoutBox .tag{position:absolute;left:2px;top:2px;background:#061017dd;color:var(--ink);font-size:9px;padding:1px 4px;border-radius:3px;max-width:calc(100% - 5px);overflow:hidden;white-space:nowrap}.layoutBox .resize{position:absolute;width:13px;height:13px;right:-2px;bottom:-2px;background:var(--warn);border-radius:3px;cursor:nwse-resize}.composeTools{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:9px}.geom{display:grid;grid-template-columns:repeat(4,1fr);gap:5px}.geom input{padding:5px}.widget.selected{border-color:var(--warn);box-shadow:0 0 0 1px #ffbd5744}.hint{width:min(100%,960px);margin-top:12px;color:var(--muted);font-size:11px;display:flex;justify-content:space-between}
.colorRow{display:grid;grid-template-columns:1fr 64px;gap:8px;align-items:center}.colorRow input[type=color]{height:34px;padding:2px}.deckApp{display:grid;grid-template-columns:24px 1fr 28px 28px;gap:5px;align-items:center;margin:4px 0}.deckApp button{padding:4px}.widget{border:1px solid var(--edge);border-radius:9px;padding:9px;margin:8px 0;background:var(--panel)}.widgetHead{display:flex;align-items:center;gap:8px}.slot{width:22px;height:22px;border-radius:50%;display:grid;place-items:center;background:#162635;color:var(--accent);font-size:11px;font-weight:700}.widget .grid{display:grid;grid-template-columns:1fr 90px;gap:7px}.mini{font-size:10px;color:var(--muted)}
.plugin{border:1px solid var(--edge);border-radius:9px;padding:9px;margin:7px 0;background:var(--panel)}.pluginTop{display:flex;gap:8px;align-items:center}.pluginName{font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1}.pill{font-size:10px;border:1px solid var(--edge);padding:2px 6px;border-radius:999px;color:var(--muted)}.pill.on{color:var(--ok);border-color:#315c48}.pill.integrated{color:var(--info)}.plugin button{margin-top:7px;padding:6px}.plugin button:disabled{opacity:.35;cursor:not-allowed}
.status{font-size:11px;color:var(--muted);margin-top:8px;white-space:pre-wrap}.arch{display:flex;flex-wrap:wrap;gap:5px}.badge{border:1px solid var(--edge);border-radius:999px;padding:3px 7px;color:var(--muted);font-size:10px}
@media(max-width:1050px){body{overflow:auto}main{height:auto;grid-template-columns:1fr}.preview{order:-1;min-height:420px}.right{border-left:0;border-top:1px solid var(--edge)}aside{border-right:0;border-bottom:1px solid var(--edge)}.device{max-width:720px}}
</style></head><body>
<header><b>BEAST STUDIO</b><span class="sub">Live compositor • layered customization • transactional controls</span><span id="conn">CONNECTING</span></header>
<main><aside><div class="nav"><button class="tab active" data-tab="visual">VISUAL</button><button class="tab" data-tab="dashboard">DASH</button><button class="tab" data-tab="decks">DECKS</button><button class="tab" data-tab="data">DATA</button><button class="tab" data-tab="plugins">PLUGINS</button><button class="tab" data-tab="search">SEARCH</button><button class="tab" data-tab="ops">OPS</button></div>
<section id="visual" class="section"><h3>VISUAL SYSTEM</h3><label>Theme</label><select id="theme"></select><label>Preview page</label><select id="page"></select><label>Output proof</label><select id="previewOutput"></select><div id="previewOutputNote" class="mini">480×320 is the validated reference layout.</div><div id="themeOpts" class="group"></div><div class="group"><h3>PALETTE OVERRIDES</h3><div class="mini">Theme-native defaults remain underneath. Change only the semantic color slots you want.</div><div id="palette"></div></div><div class="group"><h3>DATA RENDERERS</h3><div id="renderers"></div></div></section>
<section id="dashboard" class="section hidden"><h3>LIVE DASHBOARD COMPOSER</h3><div class="mini">Add, remove, drag, resize, overlap and hide real live instruments. The browser overlay and TFT share the same 12×8 grid; no fake data is introduced.</div><label>Composition</label><select id="boardSelect"></select><div class="composeTools"><button id="newBoard">+ NEW BOARD</button><button id="deleteBoard">DELETE BOARD</button></div><label>Board name</label><input id="boardLabel" maxlength="22" placeholder="Main Dashboard"><div class="composeTools"><button id="addWidget">+ ADD INSTRUMENT</button><button id="focusDashboard">EDIT ON PREVIEW</button></div><div id="dashWidgets"></div></section>
<section id="decks" class="section hidden"><h3>CONTEXT DECKS</h3><div class="mini">Curated launcher views keep a large app universe clean. ALL always remains available; a deck never hides capability from the system.</div><label>Edit deck</label><select id="deckSelect"></select><label>Deck label</label><input id="deckLabel" maxlength="18"><label><input id="deckActive" type="checkbox" style="width:auto"> Preferred deck</label><div id="deckApps" class="group"></div></section>
<section id="data" class="section hidden"><h3>CORRELATION LAB</h3><div class="mini">Compare the shape of two genuine persisted telemetry histories. Values are normalized only for plotting; source data is never altered.</div><label>Stream A</label><select id="corrA"></select><label>Stream B</label><select id="corrB"></select><div class="group"><h3>PROVENANCE</h3><div class="mini">On the TFT, long-press supported production instruments to open the Widget Inspector and see source, quality, age, units and history.</div></div></section>
<section id="plugins" class="section hidden"><h3>PLUGIN INTEGRATION</h3><div class="mini">Enabled state, Beast integration and safe transactional toggles. Changes are snapshotted, verified and rolled back on failure.</div><button id="refreshPlugins" style="margin-top:9px">REFRESH CATALOG</button><div id="pluginList"></div></section><section id="search" class="section hidden"><h3>UNIVERSAL BEAST SEARCH</h3><div class="mini">Search offline Field Library documents, BeastDex networks, Capture Vault, durable events and canonical telemetry from one place.</div><label>Search</label><input id="searchQuery" placeholder="GPS, display, network, capture…"><button id="runSearch" style="margin-top:8px">SEARCH BEAST</button><div class="group"><h3>FIELD LIBRARY IMPORT</h3><div class="mini">Import a manual, note, PDF, EPUB or ZIM into Beast’s offline library. Files are stored locally; indexing is automatic.</div><input id="libraryFile" type="file"><button id="uploadLibrary" style="margin-top:7px">IMPORT OFFLINE DOCUMENT</button></div><div id="searchResults" class="group"></div></section><section id="ops" class="section hidden"><h3>BEAST COMMAND CENTER</h3><div class="mini">Whole-platform state, services, tasks, displays and optional runtimes. Service restarts use the same audited Action Broker as the future Beast Operator.</div><button id="refreshOps" style="margin-top:9px">REFRESH OPERATIONS</button><div id="opsSummary" class="group"></div><div id="opsServices" class="group"></div><div id="opsBackups" class="group"></div><div id="opsSupport" class="group"></div><div id="opsTasks" class="group"></div></section>
</aside>
<section class="preview"><div class="device"><div id="displayBadge" class="deviceBadge">REFERENCE 480 × 320</div><div class="screenWrap"><img id="screen" alt="Exact Beastagotchi preview"><div id="layoutOverlay"></div></div></div><div class="hint"><span id="previewModeLabel">Exact Beast UI compositor</span><span id="previewMeta">draft not applied</span></div></section>
<aside class="right"><section class="section"><h3>DRAFT CONTROL</h3><div class="mini">Everything here is a draft until Apply. Preview uses current Beast Core telemetry and the same renderer as the physical TFT.</div><div class="group"><div class="row"><button id="undo">UNDO</button><button id="redo">REDO</button></div><button id="apply" class="primary" style="margin-top:8px">APPLY TO BEAST</button><button id="reset" style="margin-top:7px">RESET DRAFT</button><div id="status" class="status"></div></div><div class="group"><h3>NAMED VARIANTS</h3><input id="variantName" placeholder="My Field Setup" maxlength="64"><button id="saveVariant" style="margin-top:7px">SAVE CURRENT DRAFT</button><select id="variantList" style="margin-top:7px"></select><div class="row" style="margin-top:7px"><button id="loadVariant">LOAD</button><button id="deleteVariant">DELETE</button></div></div><div class="group"><h3>COMPOSITION PIPELINE</h3><div class="arch"><span class="badge">Live Data</span><span class="badge">Widget</span><span class="badge">Renderer</span><span class="badge">Layout</span><span class="badge">Theme</span><span class="badge">Animation</span></div><p class="mini">Dashboard binding, palettes, decks and saved variants now share the same draft → exact preview → atomic Apply path. Arbitrary drag/resize composition builds on this model.</p></div></section></aside></main>
<script>
let schema=null,base=null,draft=null,undo=[],redo=[],timer=null,plugins=[],variants=[],deckIndex=0,selectedWidget=0,activeTab="visual",dragState=null,boardEditorId="";const $=x=>document.getElementById(x);const TOKEN=new URLSearchParams(location.search).get('token')||'';
function clone(x){return JSON.parse(JSON.stringify(x))}function option(el,v,t){let o=document.createElement('option');o.value=v;o.textContent=t||v;el.appendChild(o)}function push(){undo.push(clone(draft));if(undo.length>60)undo.shift();redo=[]}
async function jfetch(url,opt={}){opt.headers={...(opt.headers||{}),'X-Beast-Studio-Token':TOKEN};let r=await fetch(url,opt);if(!r.ok)throw Error(await r.text());return r.json()}
function mutate(fn){push();fn();rebuild()}function queuePreview(){clearTimeout(timer);timer=setTimeout(preview,90)}
function setTab(id){activeTab=id;document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x.dataset.tab===id));['visual','dashboard','decks','data','plugins','search','ops'].forEach(x=>$(x).classList.toggle('hidden',x!==id));if(id==='plugins')loadPlugins();if(id==='ops')loadOps();if(id==='dashboard'){draft.page='dashboard';draft.preview_board_id=boardEditorId;queuePreview();renderLayoutOverlay()}else renderLayoutOverlay()}
document.querySelectorAll('.tab').forEach(x=>x.onclick=()=>setTab(x.dataset.tab));
function rebuild(){
 $('theme').innerHTML='';schema.themes.forEach(x=>option($('theme'),x.id,x.label));$('theme').value=draft.theme;
 $('page').innerHTML='';schema.pages.forEach(x=>option($('page'),x.id,x.title));$('page').value=draft.page||'home';
 draft.preview_output=draft.preview_output||'480x320';let po=$('previewOutput');po.innerHTML='';(schema.preview_outputs||[]).forEach(x=>option(po,x.id,x.label));po.value=draft.preview_output;po.onchange=()=>mutate(()=>draft.preview_output=po.value);updatePreviewOutputChrome();
 let box=$('themeOpts');box.innerHTML='<h3>THEME OPTIONS</h3>';let rows=schema.theme_options[draft.theme]||[];let opts=(draft.theme_options[draft.theme]||{});rows.forEach(r=>{let l=document.createElement('label');l.textContent=r.label;let s=document.createElement('select');r.values.forEach(v=>option(s,String(v)));s.value=String(opts[r.key]??r.default??r.values[0]);s.onchange=()=>mutate(()=>{draft.theme_options[draft.theme]=draft.theme_options[draft.theme]||{};draft.theme_options[draft.theme][r.key]=s.value});box.append(l,s)});
 let rr=$('renderers');rr.innerHTML='';Object.entries(schema.renderers).forEach(([pid,vals])=>{let l=document.createElement('label');l.textContent=pid.toUpperCase();let s=document.createElement('select');vals.forEach(v=>option(s,v));s.value=draft.renderers[pid]||vals[0];s.onchange=()=>mutate(()=>draft.renderers[pid]=s.value);rr.append(l,s)});
 rebuildDashboard();rebuildPalette();rebuildDecks();rebuildData();queuePreview();
}
function rebuildPalette(){let box=$('palette');box.innerHTML='';draft.palette_overrides=draft.palette_overrides||{};draft.palette_overrides[draft.theme]=draft.palette_overrides[draft.theme]||{};let baseColors=schema.theme_colors[draft.theme]||{};schema.palette_slots.forEach(slot=>{if(!baseColors[slot])return;let row=document.createElement('div');row.className='colorRow';let l=document.createElement('label');l.textContent=slot.toUpperCase();let c=document.createElement('input');c.type='color';c.value=draft.palette_overrides[draft.theme][slot]||baseColors[slot];c.oninput=()=>{draft.palette_overrides[draft.theme][slot]=c.value;queuePreview()};c.onchange=()=>{rebuild();};row.append(l,c);box.append(row)})}
function rebuildDecks(){draft.context_decks=draft.context_decks||clone(schema.default_context_decks||[]);if(!draft.context_decks.length)return;deckIndex=Math.max(0,Math.min(deckIndex,draft.context_decks.length-1));let sel=$('deckSelect');sel.innerHTML='';draft.context_decks.forEach((d,i)=>option(sel,String(i),d.label||d.id));sel.value=String(deckIndex);sel.onchange=()=>{deckIndex=Number(sel.value)||0;rebuildDecks()};let d=draft.context_decks[deckIndex];$('deckLabel').value=d.label||d.id;$('deckLabel').onchange=()=>mutate(()=>d.label=$('deckLabel').value.toUpperCase().slice(0,18));$('deckActive').checked=draft.active_context_deck===d.id;$('deckActive').onchange=()=>mutate(()=>draft.active_context_deck=$('deckActive').checked?d.id:'');let box=$('deckApps');box.innerHTML='<h3>DECK APPS</h3>';let ids=d.apps||[];[...schema.apps,...boardApps()].forEach(app=>{let row=document.createElement('div');row.className='deckApp';let ck=document.createElement('input');ck.type='checkbox';ck.checked=ids.includes(app.id);let title=document.createElement('span');title.textContent=app.title;let up=document.createElement('button');up.textContent='↑';let dn=document.createElement('button');dn.textContent='↓';ck.onchange=()=>mutate(()=>{let pos=d.apps.indexOf(app.id);if(ck.checked&&pos<0)d.apps.push(app.id);if(!ck.checked&&pos>=0)d.apps.splice(pos,1)});up.onclick=()=>mutate(()=>{let pos=d.apps.indexOf(app.id);if(pos>0){let x=d.apps[pos-1];d.apps[pos-1]=app.id;d.apps[pos]=x}});dn.onclick=()=>mutate(()=>{let pos=d.apps.indexOf(app.id);if(pos>=0&&pos<d.apps.length-1){let x=d.apps[pos+1];d.apps[pos+1]=app.id;d.apps[pos]=x}});row.append(ck,title,up,dn);box.append(row)})}
function rebuildData(){draft.correlation_keys=draft.correlation_keys||['system.cpu.total','system.temp.cpu_c'];[['corrA',0],['corrB',1]].forEach(([id,idx])=>{let s=$(id);s.innerHTML='';schema.dashboard_keys.forEach(r=>option(s,r.key,`${r.category||'Other'} · ${r.label||r.key}`));s.value=draft.correlation_keys[idx]||'';s.onchange=()=>mutate(()=>draft.correlation_keys[idx]=s.value)})}
function boardById(id){return (draft.custom_boards||[]).find(b=>b.id===id)||null}
function currentWidgetList(){let b=boardById(boardEditorId);return b?b.widgets:(draft.dashboard_widgets||[])}
function setCurrentWidgetList(rows){let b=boardById(boardEditorId);if(b)b.widgets=rows;else draft.dashboard_widgets=rows}
function boardApps(){return (draft.custom_boards||[]).map(b=>({id:`board:${b.id}`,title:b.label||b.id,category:'Boards',description:'User-composed live telemetry board'}))}
function rebuildBoardSelector(){draft.custom_boards=draft.custom_boards||[];if(boardEditorId&&!boardById(boardEditorId))boardEditorId='';let sel=$('boardSelect');sel.innerHTML='';option(sel,'','MAIN DASHBOARD');draft.custom_boards.forEach(b=>option(sel,b.id,`BOARD · ${b.label||b.id}`));sel.value=boardEditorId;sel.onchange=()=>{boardEditorId=sel.value;selectedWidget=0;draft.preview_board_id=boardEditorId;draft.page='dashboard';rebuildDashboard();queuePreview()};let b=boardById(boardEditorId);$('boardLabel').disabled=!b;$('deleteBoard').disabled=!b;$('boardLabel').value=b?(b.label||b.id):'Main Dashboard';$('boardLabel').onchange=()=>{if(!b)return;mutate(()=>b.label=$('boardLabel').value.trim().slice(0,22)||b.id)}}
function defaultWidget(i){let m=schema.dashboard_keys[i%schema.dashboard_keys.length]||{key:'system.cpu.total',label:'DATA',min:0,max:100};return {id:`instrument_${Date.now()}_${i}`,key:m.key,label:(m.label||'DATA').slice(0,18),style:'metric',visible:true,z:i,x:(i*2)%10,y:(Math.floor(i/5)*2)%6,w:4,h:3,min:m.min,max:m.max}}
function geomInput(card,label,key,w,i){let wrap=document.createElement('div'),l=document.createElement('label'),inp=document.createElement('input');l.textContent=label;inp.type='number';inp.value=w[key]??0;inp.min=key==='x'||key==='y'?0:2;inp.max=key==='x'||key==='w'?12:8;inp.onchange=()=>mutate(()=>draft.dashboard_widgets[i][key]=Number(inp.value));wrap.append(l,inp);card.append(wrap)}
function rebuildDashboard(){rebuildBoardSelector();let box=$('dashWidgets');box.innerHTML='';let widgets=currentWidgetList();if(selectedWidget>=widgets.length)selectedWidget=Math.max(0,widgets.length-1);widgets.forEach((w,i)=>{let card=document.createElement('div');card.className='widget'+(i===selectedWidget?' selected':'');card.onclick=e=>{if(e.target.tagName==='BUTTON'||e.target.tagName==='SELECT'||e.target.tagName==='INPUT')return;selectedWidget=i;rebuildDashboard();renderLayoutOverlay()};let head=document.createElement('div');head.className='widgetHead';let slot=document.createElement('span');slot.className='slot';slot.textContent=i+1;let title=document.createElement('b');title.textContent=w.label||`INSTRUMENT ${i+1}`;let vis=document.createElement('input');vis.type='checkbox';vis.style.width='auto';vis.checked=w.visible!==false;vis.title='Visible';vis.onchange=()=>mutate(()=>currentWidgetList()[i].visible=vis.checked);head.append(slot,title,vis);card.appendChild(head);
 let l1=document.createElement('label');l1.textContent='Live data source';let src=document.createElement('select');schema.dashboard_keys.forEach(r=>option(src,r.key,`${r.category||'Other'} · ${r.label||r.key}`));src.value=w.key;src.onchange=()=>mutate(()=>{let m=schema.dashboard_keys.find(x=>x.key===src.value)||{};let x=currentWidgetList()[i];x.key=src.value;x.label=(m.label||src.value.split('.').pop()).slice(0,18);if(m.min!==undefined)x.min=m.min;if(m.max!==undefined)x.max=m.max});card.append(l1,src);
 let grid=document.createElement('div');grid.className='grid';let a=document.createElement('div'),b=document.createElement('div');let ll=document.createElement('label');ll.textContent='Label';let inp=document.createElement('input');inp.value=w.label||'';inp.maxLength=18;inp.onchange=()=>mutate(()=>currentWidgetList()[i].label=inp.value);a.append(ll,inp);let ls=document.createElement('label');ls.textContent='Renderer';let sty=document.createElement('select');schema.widget_styles.forEach(v=>option(sty,v,v.toUpperCase()));sty.value=w.style||'metric';sty.onchange=()=>mutate(()=>currentWidgetList()[i].style=sty.value);b.append(ls,sty);grid.append(a,b);card.append(grid);
 let geom=document.createElement('div');geom.className='geom';[['X','x'],['Y','y'],['W','w'],['H','h']].forEach(([lab,key])=>{let q=document.createElement('div'),l=document.createElement('label'),v=document.createElement('input');l.textContent=lab;v.type='number';v.value=w[key]??0;v.min=(key==='x'||key==='y')?0:2;v.max=(key==='x'||key==='w')?12:8;v.onchange=()=>mutate(()=>currentWidgetList()[i][key]=Number(v.value));q.append(l,v);geom.append(q)});card.append(geom);
 let actions=document.createElement('div');actions.className='row';let front=document.createElement('button');front.textContent='BRING FRONT';front.onclick=()=>mutate(()=>currentWidgetList()[i].z=Math.max(...currentWidgetList().map(x=>Number(x.z||0)),0)+1);let remove=document.createElement('button');remove.textContent='REMOVE';remove.onclick=()=>{if(!confirm(`Remove ${w.label||'this instrument'} from this draft?`))return;mutate(()=>{currentWidgetList().splice(i,1);selectedWidget=Math.max(0,i-1)})};actions.append(front,remove);card.append(actions);box.appendChild(card)});renderLayoutOverlay()}
function previewOutputInfo(){let id=(draft&&draft.preview_output)||'480x320';return (schema.preview_outputs||[]).find(x=>x.id===id)||(schema.preview_outputs||[])[0]||{id:'480x320',width:480,height:320,reference:true,label:'REFERENCE 480 × 320'}}
function updatePreviewOutputChrome(){if(!draft||!schema)return;let x=previewOutputInfo(),ref=!!x.reference;$('screen').style.aspectRatio=`${x.width}/${x.height}`;$('displayBadge').textContent=(ref?'REFERENCE ':'COMPATIBILITY ')+`${x.width} × ${x.height}`;$('previewModeLabel').textContent=ref?'Exact Beast UI compositor':'Compatibility-scaled output proof';$('previewOutputNote').textContent=ref?'480×320 is the validated reference layout.':'Compatibility scaling only — this is not yet a responsive larger-screen layout.'}
function renderLayoutOverlay(){let ov=$('layoutOverlay');if(!ov)return;ov.innerHTML='';if(activeTab!=='dashboard'||!draft||draft.page!=='dashboard'||!previewOutputInfo().reference){ov.style.display='none';return}ov.style.display='block';currentWidgetList().forEach((w,i)=>{let b=document.createElement('div');b.className='layoutBox'+(i===selectedWidget?' selected':'')+(w.visible===false?' hiddenWidget':'');let x=8+464*(Number(w.x||0)/12),y=43+225*(Number(w.y||0)/8),ww=464*(Number(w.w||4)/12)-4,hh=225*(Number(w.h||3)/8)-4;b.style.left=(x/480*100)+'%';b.style.top=(y/320*100)+'%';b.style.width=(Math.max(28,ww)/480*100)+'%';b.style.height=(Math.max(24,hh)/320*100)+'%';b.style.zIndex=1000+Number(w.z||0);let tag=document.createElement('span');tag.className='tag';tag.textContent=w.label||w.key||`#${i+1}`;let r=document.createElement('span');r.className='resize';b.append(tag,r);b.onpointerdown=e=>startLayoutDrag(e,i,e.target===r?'resize':'move');b.onclick=e=>{e.stopPropagation();selectedWidget=i;rebuildDashboard()};ov.append(b)})}
function startLayoutDrag(e,i,mode){e.preventDefault();e.stopPropagation();selectedWidget=i;push();let w=currentWidgetList()[i];dragState={i,mode,sx:e.clientX,sy:e.clientY,x:Number(w.x||0),y:Number(w.y||0),w:Number(w.w||4),h:Number(w.h||3)};e.currentTarget.setPointerCapture(e.pointerId);e.currentTarget.onpointermove=layoutDrag;e.currentTarget.onpointerup=endLayoutDrag;e.currentTarget.onpointercancel=endLayoutDrag;rebuildDashboard()}
function layoutDrag(e){if(!dragState)return;let rect=$('layoutOverlay').getBoundingClientRect(),dx=Math.round((e.clientX-dragState.sx)/rect.width*12),dy=Math.round((e.clientY-dragState.sy)/rect.height*8),w=currentWidgetList()[dragState.i];if(dragState.mode==='move'){w.x=Math.max(0,Math.min(12-dragState.w,dragState.x+dx));w.y=Math.max(0,Math.min(8-dragState.h,dragState.y+dy))}else{w.w=Math.max(2,Math.min(12-dragState.x,dragState.w+dx));w.h=Math.max(2,Math.min(8-dragState.y,dragState.h+dy))}renderLayoutOverlay();queuePreview()}
function endLayoutDrag(e){if(e.currentTarget){e.currentTarget.onpointermove=null;e.currentTarget.onpointerup=null;e.currentTarget.onpointercancel=null}dragState=null;rebuildDashboard();queuePreview()}
$('addWidget').onclick=()=>{let rows=currentWidgetList();if(rows.length>=schema.max_dashboard_widgets){$('status').textContent='Composition safety limit reached.';return}mutate(()=>{rows=currentWidgetList();rows.push(defaultWidget(rows.length));selectedWidget=rows.length-1;draft.page='dashboard';draft.preview_board_id=boardEditorId})};$('focusDashboard').onclick=()=>{draft.page='dashboard';draft.preview_board_id=boardEditorId;$('page').value='dashboard';queuePreview();renderLayoutOverlay()};$('newBoard').onclick=()=>{let name=prompt('Board name','My Board');if(!name)return;mutate(()=>{draft.custom_boards=draft.custom_boards||[];let baseId=name.toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_+|_+$/g,'').slice(0,32)||'board';let id=baseId,n=2;while(draft.custom_boards.some(b=>b.id===id)){id=baseId+'_'+n++}let widgets=[defaultWidget(0),defaultWidget(1),defaultWidget(2)];draft.custom_boards.push({id,label:name.slice(0,22),widgets});boardEditorId=id;draft.preview_board_id=id;draft.page='dashboard';selectedWidget=0})};$('deleteBoard').onclick=()=>{let b=boardById(boardEditorId);if(!b||!confirm(`Delete board ${b.label||b.id}?`))return;mutate(()=>{draft.custom_boards=draft.custom_boards.filter(x=>x.id!==boardEditorId);(draft.context_decks||[]).forEach(d=>d.apps=(d.apps||[]).filter(x=>x!==`board:${boardEditorId}`));boardEditorId='';draft.preview_board_id='';selectedWidget=0})}

async function preview(){try{$('conn').textContent='RENDERING';updatePreviewOutputChrome();let r=await fetch('/api/preview',{method:'POST',headers:{'content-type':'application/json','X-Beast-Studio-Token':TOKEN},body:JSON.stringify(draft)});if(!r.ok)throw Error(await r.text());let b=await r.blob();let old=$('screen').src;$('screen').src=URL.createObjectURL(b);if(old&&old.startsWith('blob:'))URL.revokeObjectURL(old);$('conn').textContent='LIVE';let po=previewOutputInfo();$('previewMeta').textContent=`${draft.theme} · ${draft.page}${boardEditorId?' · '+(boardById(boardEditorId)?.label||boardEditorId):''} · ${po.width}×${po.height}`;renderLayoutOverlay()}catch(e){$('conn').textContent='ERROR';$('status').textContent=e}}
async function loadPlugins(){try{let x=await jfetch('/api/plugins');plugins=x.items||[];renderPlugins()}catch(e){$('pluginList').innerHTML='<div class="status">Plugin catalog unavailable: '+e+'</div>'}}
function renderPlugins(){let box=$('pluginList');box.innerHTML='';plugins.forEach(p=>{let c=document.createElement('div');c.className='plugin';let top=document.createElement('div');top.className='pluginTop';let name=document.createElement('span');name.className='pluginName';name.textContent=p.name;let st=document.createElement('span');st.className='pill '+(p.enabled?'on':'');st.textContent=p.enabled?'ON':'OFF';let integ=document.createElement('span');integ.className='pill '+(!['config_only','isolated'].includes(p.integration)?'integrated':'');integ.textContent=p.integration||'config_only';top.append(name,st,integ);c.append(top);let meta=document.createElement('div');meta.className='mini';meta.textContent=`${p.role||'plugin'} · ${p.display_policy||''}${p.protected?' · protected':''}`;c.append(meta);let btn=document.createElement('button');btn.textContent=p.enabled?'DISABLE':'ENABLE';btn.disabled=!p.toggle_capable||p.protected||(p.legacy_display_owner&&!p.enabled);btn.onclick=()=>togglePlugin(p,btn);c.append(btn);box.append(c)});if(!plugins.length)box.innerHTML='<div class="status">No plugins reported yet.</div>'}
async function togglePlugin(p,btn){let wanted=!p.enabled;btn.disabled=true;$('status').textContent='Planning plugin change…';try{let plan=await jfetch('/api/plugin-plan',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({name:p.name,enabled:wanted})});let pp=plan.plan||{};if(!pp.allowed)throw Error((pp.blockers||['blocked']).join('; '));let msg=`${wanted?'Enable':'Disable'} ${p.name}?\n\nA config snapshot will be taken. Pwnagotchi will be restarted if required and the change will roll back automatically if health verification fails.`;if(!confirm(msg)){btn.disabled=false;return}let result=await jfetch('/api/plugin-toggle',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({name:p.name,enabled:wanted})});let row=result.action_row||{};$('status').textContent=`Plugin ${p.name}: ${row.status||result.error||'unknown'}`;await new Promise(r=>setTimeout(r,900));await loadPlugins()}catch(e){$('status').textContent='Plugin change failed: '+e;btn.disabled=false}}
async function createBackup(btn){if(!confirm('Create a Beast recovery backup now? It may contain private configuration.'))return;btn.disabled=true;$('status').textContent='Creating recovery backup…';try{let plan=await jfetch('/api/backup-plan',{method:'POST',headers:{'content-type':'application/json'},body:'{}'});if(!(plan.plan||{}).allowed)throw Error(((plan.plan||{}).blockers||['blocked']).join('; '));let r=await jfetch('/api/backup-create',{method:'POST',headers:{'content-type':'application/json'},body:'{}'});$('status').textContent=(r.action_row||{}).status==='success'?'Backup created.':'Backup failed.';await loadOps()}catch(e){$('status').textContent='Backup failed: '+e}finally{btn.disabled=false}}
async function createSupportBundle(btn){if(!confirm('Create a sanitized Beast support bundle? Nearby network identities, GPS coordinates, credentials, raw config and raw logs are excluded.'))return;btn.disabled=true;$('status').textContent='Creating sanitized support bundle…';try{let plan=await jfetch('/api/support-plan',{method:'POST',headers:{'content-type':'application/json'},body:'{}'});if(!(plan.plan||{}).allowed)throw Error(((plan.plan||{}).blockers||['blocked']).join('; '));let r=await jfetch('/api/support-create',{method:'POST',headers:{'content-type':'application/json'},body:'{}'});let row=r.action_row||{};$('status').textContent=row.status==='success'?'Support bundle created.':'Support bundle failed.';await loadOps()}catch(e){$('status').textContent='Support bundle failed: '+e}finally{btn.disabled=false}}
async function verifyBackup(name,btn){btn.disabled=true;$('status').textContent='Verifying '+name+'...';try{let x=await jfetch('/api/backup-inspect?name='+encodeURIComponent(name));let msg=x.ok?`VERIFIED / ${String(x.sha256||'').slice(0,12)}... / DB ${x.db_valid===true?'OK':x.db_valid===false?'FAIL':'N/A'}`:`NOT READY / ${(x.blockers||[x.error||'verification failed']).join('; ')}`;$('status').textContent=msg;if(x.ok)alert('Backup verified for restore staging.\n\nSHA-256: '+x.sha256+'\nDatabase: '+(x.db_valid===true?'OK':x.db_valid===false?'FAILED':'not present')+'\n\nNo restore was performed.')}catch(e){$('status').textContent='Backup verification failed: '+e}finally{btn.disabled=false}}
async function loadOps(){try{let x=await jfetch('/api/platform');let sum=$('opsSummary');sum.innerHTML='';let ov=x.overview||{};let c=document.createElement('div');c.className='widget';c.innerHTML=`<div class="widgetHead"><b>PLATFORM</b><span class="pill ${ov.state==='healthy'?'on':''}">${String(ov.state||'unknown').toUpperCase()}</span></div><div class="mini">${(ov.attention||[]).length} attention item(s) · ${(x.topology?.failures||[]).length} dependency failure(s) · ${(x.library?.total||0)} offline documents</div>`;sum.append(c);let svc=$('opsServices');svc.innerHTML='<h3>SERVICES</h3>';(x.services||[]).forEach(r=>{let d=document.createElement('div');d.className='plugin';let top=document.createElement('div');top.className='pluginTop';let name=document.createElement('span');name.className='pluginName';name.textContent=r.unit;let st=document.createElement('span');st.className='pill '+(r.active==='active'?'on':'');st.textContent=String(r.active||'unknown').toUpperCase();top.append(name,st);d.append(top);let meta=document.createElement('div');meta.className='mini';meta.textContent=`${r.sub||'--'} · pid ${r.pid||0}`;d.append(meta);if(['pwnagotchi.service','bettercap.service','gpsd.service','beast-ui.service'].includes(r.unit)){let b=document.createElement('button');b.textContent='RESTART';b.onclick=()=>restartService(r.unit,b);d.append(b)}svc.append(d)});let bk=$('opsBackups');bk.innerHTML='<h3>BACKUP / RECOVERY</h3>';let b=document.createElement('button');b.textContent='CREATE RECOVERY BACKUP';b.onclick=()=>createBackup(b);bk.append(b);(x.backups?.items||[]).slice(0,4).forEach(r=>{let d=document.createElement('div');d.className='plugin';d.style.marginTop='6px';let top=document.createElement('div');top.className='pluginTop';let n=document.createElement('span');n.className='pluginName';n.textContent=r.name||'backup';let st=document.createElement('span');st.className='pill '+(r.valid?'on':'');st.textContent=r.valid?'STRUCTURE OK':'CHECK';top.append(n,st);d.append(top);let meta=document.createElement('div');meta.className='mini';meta.textContent=String(r.size_human||r.size_bytes||'');d.append(meta);let vb=document.createElement('button');vb.textContent='VERIFY FOR RESTORE';vb.onclick=()=>verifyBackup(r.name,vb);d.append(vb);bk.append(d)});let sp=$('opsSupport');sp.innerHTML='<h3>SUPPORT / DIAGNOSTICS</h3><div class="mini">Creates a privacy-sanitized troubleshooting bundle. Network identities, GPS coordinates, credentials, raw config and raw logs are excluded.</div>';let sb=document.createElement('button');sb.textContent='CREATE SANITIZED SUPPORT BUNDLE';sb.style.marginTop='7px';sb.onclick=()=>createSupportBundle(sb);sp.append(sb);let jobs=$('opsTasks');jobs.innerHTML='<h3>TASK CENTER</h3>';((x.jobs||{}).items||[]).slice(0,8).forEach(r=>{let d=document.createElement('div');d.className='widget';let p=typeof r.progress==='number'?Math.round(r.progress*100)+'%':String(r.status||'').toUpperCase();d.innerHTML=`<div class="widgetHead"><span class="pluginName">${r.label||r.kind}</span><span class="pill ${r.status==='complete'?'on':''}">${p}</span></div><div class="mini">${r.detail||''}</div>`;jobs.append(d)});if(!((x.jobs||{}).items||[]).length)jobs.innerHTML+='<div class="status">No recorded background jobs yet.</div>'}catch(e){$('opsSummary').innerHTML='<div class="status">Operations unavailable: '+e+'</div>'}}
async function restartService(unit,btn){if(!confirm(`Restart ${unit}?`))return;btn.disabled=true;$('status').textContent='Planning service restart…';try{let plan=await jfetch('/api/service-plan',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({unit})});if(!(plan.plan||{}).allowed)throw Error(((plan.plan||{}).blockers||['blocked']).join('; '));let r=await jfetch('/api/service-restart',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({unit})});$('status').textContent=`${unit}: ${(r.action_row||{}).status||r.error||'unknown'}`;await new Promise(x=>setTimeout(x,1200));await loadOps()}catch(e){$('status').textContent='Service restart failed: '+e;btn.disabled=false}}
$('refreshOps').onclick=loadOps;

async function openLibraryDocument(id){try{let r=await fetch('/api/library-file?id='+encodeURIComponent(id),{headers:{'X-Beast-Studio-Token':TOKEN}});if(!r.ok)throw Error(await r.text());let b=await r.blob();let u=URL.createObjectURL(b);window.open(u,'_blank','noopener');setTimeout(()=>URL.revokeObjectURL(u),60000)}catch(e){$('status').textContent='Document open failed: '+e}}
async function uploadLibraryDocument(){let f=$('libraryFile').files[0];if(!f){$('status').textContent='Choose a Field Library file first.';return}let b=$('uploadLibrary');b.disabled=true;$('status').textContent='Importing '+f.name+'…';try{let r=await fetch('/api/library-upload?name='+encodeURIComponent(f.name),{method:'PUT',headers:{'X-Beast-Studio-Token':TOKEN,'Content-Type':'application/octet-stream'},body:f});let x=await r.json();if(!r.ok)throw Error(x.error||r.statusText);$('status').textContent=`Imported ${x.name}. Beast will index it automatically within about a minute.`;$('libraryFile').value=''}catch(e){$('status').textContent='Library import failed: '+e}finally{b.disabled=false}}
async function runUniversalSearch(){let q=$('searchQuery').value.trim();let box=$('searchResults');if(!q){box.innerHTML='<div class="status">Enter a search term.</div>';return}box.innerHTML='<div class="status">Searching local Beast data…</div>';try{let x=await jfetch('/api/search?q='+encodeURIComponent(q));box.innerHTML='';let groups=x.groups||{};Object.entries(groups).forEach(([name,rows])=>{let h=document.createElement('h3');h.textContent=name.toUpperCase();box.append(h);rows.forEach(r=>{let c=document.createElement('div');c.className='widget';let a=document.createElement('div');a.className='widgetHead';a.textContent=r.title||r.type||'result';let b=document.createElement('div');b.className='mini';b.textContent=r.subtitle||'';c.append(a,b);if(r.type==='document'&&r.data?.id){let o=document.createElement('button');o.textContent='OPEN LOCAL DOCUMENT';o.style.marginTop='7px';o.onclick=()=>openLibraryDocument(r.data.id);c.append(o)}box.append(c)})});if(!x.count)box.innerHTML='<div class="status">No local results.</div>'}catch(e){box.innerHTML='<div class="status">Search failed: '+e+'</div>'}}
$('runSearch').onclick=runUniversalSearch;$('uploadLibrary').onclick=uploadLibraryDocument;$('searchQuery').onkeydown=e=>{if(e.key==='Enter')runUniversalSearch()};

async function loadVariants(){try{variants=await jfetch('/api/variants');let s=$('variantList');s.innerHTML='';option(s,'','-- saved variants --');variants.forEach(v=>option(s,v.id,v.name||v.id))}catch(e){$('status').textContent='Variant list unavailable: '+e}}
$('saveVariant').onclick=async()=>{let name=$('variantName').value.trim();if(!name){$('status').textContent='Enter a variant name first.';return}try{let r=await jfetch('/api/variant-save',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({name,draft})});$('status').textContent='Saved variant: '+r.name;await loadVariants()}catch(e){$('status').textContent='Save variant failed: '+e}}
$('loadVariant').onclick=async()=>{let id=$('variantList').value;if(!id)return;try{push();draft=await jfetch('/api/variant-load',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id})});rebuild();$('status').textContent='Variant loaded into draft. Apply when ready.'}catch(e){$('status').textContent='Load failed: '+e}}
$('deleteVariant').onclick=async()=>{let id=$('variantList').value;if(!id)return;if(!confirm('Delete this saved variant?'))return;try{await jfetch('/api/variant-delete',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id})});await loadVariants();$('status').textContent='Variant deleted.'}catch(e){$('status').textContent='Delete failed: '+e}}
$('refreshPlugins').onclick=loadPlugins;$('theme').onchange=()=>mutate(()=>draft.theme=$('theme').value);$('page').onchange=()=>mutate(()=>draft.page=$('page').value);$('undo').onclick=()=>{if(!undo.length)return;redo.push(clone(draft));draft=undo.pop();rebuild()};$('redo').onclick=()=>{if(!redo.length)return;undo.push(clone(draft));draft=redo.pop();rebuild()};$('reset').onclick=()=>{push();draft=clone(base);rebuild()};$('apply').onclick=async()=>{try{await jfetch('/api/apply',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(draft)});base=clone(draft);undo=[];redo=[];$('status').textContent='Applied atomically. Physical Beast UI reloads the draft automatically.'}catch(e){$('status').textContent='Apply failed: '+e}};
(async()=>{try{schema=await jfetch('/api/schema');base=await jfetch('/api/preferences');draft=clone(base);rebuild();await loadVariants();$('conn').textContent='LIVE'}catch(e){$('conn').textContent='ERROR';$('status').textContent=e}})();
</script></body></html>
'''


class StudioState:
    def __init__(self,root: str,prefs: str,token_file: str) -> None:
        self.root=Path(root);self.prefs=Path(prefs);self.token_file=Path(token_file);self.api=BeastAPI();self.actions=BeastActionClient();self.token=self._token();self.variants_dir=self.prefs.parent/'variants'
        self.library_files=LibraryFileManager()

    def _token(self)->str:
        self.token_file.parent.mkdir(parents=True,exist_ok=True)
        if self.token_file.exists():return self.token_file.read_text().strip()
        tok=secrets.token_urlsafe(18);self.token_file.write_text(tok+'\n');os.chmod(self.token_file,0o600);return tok

    def preferences(self)->dict:
        try:obj=json.loads(self.prefs.read_text())
        except Exception:obj={}
        renderers=dict(obj.get('renderers') or {})
        for pid,vals in BeastUI.RENDERER_CHOICES.items():renderers.setdefault(pid,vals[0])
        app_ids=[a.id for a in AppRegistry().all()]
        decks=validate_context_decks(obj.get('context_decks'),app_ids=app_ids)
        active=str(obj.get('active_context_deck') or '')
        if active not in {d['id'] for d in decks}:active=''
        return {'theme':str(obj.get('theme') or 'classic'),'page':'home','preview_output':'480x320','renderers':renderers,'theme_options':dict(obj.get('theme_options') or {}),'dashboard_widgets':validate_dashboard_widgets(obj.get('dashboard_widgets')),'custom_boards':validate_custom_boards(obj.get('custom_boards')),'preview_board_id':'','context_decks':decks,'active_context_deck':active,'palette_overrides':validate_palette_overrides(obj.get('palette_overrides'),theme_ids=BeastUI.THEMES),'correlation_keys':validate_correlation_keys(obj.get('correlation_keys'))}

    def validate(self,obj: dict)->dict:
        if not isinstance(obj,dict):raise ValueError('draft must be an object')
        theme=str(obj.get('theme') or 'classic');tp=self.root/'themes'/f'{theme}.json'
        if not tp.exists():raise ValueError('unknown theme')
        page=str(obj.get('page') or 'home')
        preview_output=str(obj.get('preview_output') or '480x320')
        if preview_output not in {'480x320','640x480','800x480'}:preview_output='480x320'
        probe=BeastUI(root=str(self.root),output=str(Path(tempfile.gettempdir())/'beast-studio-probe.png'),theme_id=theme)
        if page not in probe.pages.IDS:raise ValueError('unknown page')
        renderers={}
        incoming=obj.get('renderers') or {}
        for pid,vals in probe.RENDERER_CHOICES.items():
            val=str(incoming.get(pid) or vals[0]);renderers[pid]=val if val in vals else vals[0]
        options={};raw=obj.get('theme_options') or {}
        if isinstance(raw,dict):
            for tid,tvals in raw.items():
                if not (self.root/'themes'/f'{tid}.json').exists() or not isinstance(tvals,dict):continue
                allowed={k:set(map(str,vals)) for k,_lab,vals in probe._theme_option_rows(tid)}
                clean={}
                for k,v in tvals.items():
                    if k in allowed and str(v) in allowed[k]:clean[k]=v
                options[str(tid)]=clean
        live_catalog=scalar_catalog(self.api.telemetry())
        widgets=validate_dashboard_widgets(obj.get('dashboard_widgets'),catalog=live_catalog)
        boards=validate_custom_boards(obj.get('custom_boards'),catalog=live_catalog)
        board_ids={str(b.get('id')) for b in boards}
        preview_board_id=str(obj.get('preview_board_id') or '')
        if preview_board_id not in board_ids:preview_board_id=''
        app_ids=[a.id for a in AppRegistry().all()]+[f"board:{b['id']}" for b in boards]
        decks=validate_context_decks(obj.get('context_decks'),app_ids=app_ids)
        active=str(obj.get('active_context_deck') or '')
        if active not in {d['id'] for d in decks}:active=''
        palette=validate_palette_overrides(obj.get('palette_overrides'),theme_ids=probe.THEMES)
        corr=validate_correlation_keys(obj.get('correlation_keys'),catalog=live_catalog)
        return {'theme':theme,'page':page,'preview_output':preview_output,'renderers':renderers,'theme_options':options,'dashboard_widgets':widgets,'custom_boards':boards,'preview_board_id':preview_board_id,'context_decks':decks,'active_context_deck':active,'palette_overrides':palette,'correlation_keys':corr}

    def schema(self)->dict:
        probe=BeastUI(root=str(self.root),output=str(Path(tempfile.gettempdir())/'beast-studio-schema.png'),theme_id='classic')
        themes=[];opts={}
        for tid in probe.THEMES:
            fp=self.root/'themes'/f'{tid}.json'
            if not fp.exists():continue
            th=load_theme(fp);themes.append({'id':tid,'label':th.label})
            defaults=probe.options_for_theme(tid);opts[tid]=[{'key':k,'label':lab,'values':vals,'default':defaults.get(k)} for k,lab,vals in probe._theme_option_rows(tid)]
        telemetry=scalar_catalog(self.api.telemetry())
        apps=[{'id':a.id,'title':a.title,'category':a.category,'description':a.description} for a in AppRegistry().all()]
        theme_colors={}
        for row in themes:
            th=load_theme(self.root/'themes'/f"{row['id']}.json")
            theme_colors[row['id']]={slot:'#%02x%02x%02x'%th.c(slot) for slot in PALETTE_SLOTS if slot in th.colors}
        return {'version':'0.18.0','themes':themes,'preview_outputs':[{'id':'480x320','label':'REFERENCE · 480 × 320','width':480,'height':320,'reference':True},{'id':'640x480','label':'COMPATIBILITY · 640 × 480','width':640,'height':480,'reference':False},{'id':'800x480','label':'COMPATIBILITY · 800 × 480','width':800,'height':480,'reference':False}],'pages':[{'id':x,'title':probe.pages.TITLES[x]} for x in probe.pages.IDS],'renderers':probe.RENDERER_CHOICES,'theme_options':opts,'dashboard_keys':telemetry,'widget_styles':list(WIDGET_STYLES),'palette_slots':list(PALETTE_SLOTS),'theme_colors':theme_colors,'apps':apps,'default_context_decks':[dict(x) for x in DEFAULT_CONTEXT_DECKS],'max_dashboard_widgets':MAX_DASHBOARD_WIDGETS}

    def preview(self,draft: dict)->bytes:
        cfg=self.validate(draft);live=self.api.live(24);state=live.get('state') if isinstance(live,dict) else {}
        preview_widgets=cfg['dashboard_widgets']
        if cfg.get('preview_board_id'):
            preview_widgets=next((b.get('widgets') or [] for b in cfg.get('custom_boards') or [] if b.get('id')==cfg['preview_board_id']),preview_widgets)
        hkeys=tuple(dict.fromkeys(['system.cpu.total','system.temp.cpu_c','system.memory.used_pct','wifi.ap_count','wifi.client_count',*dashboard_history_keys(preview_widgets)]))
        batch=self.api.history_batch(hkeys,64,channel_limit=90,expedition_points=256)
        with tempfile.TemporaryDirectory(prefix='beast-studio-') as td:
            dims={'480x320':(480,320),'640x480':(640,480),'800x480':(800,480)};physical=dims.get(cfg.get('preview_output'),(480,320))
            ui=BeastUI(root=str(self.root),output=str(Path(td)/'preview.png'),theme_id=cfg['theme'],physical_size=physical,display_mode='fit');ui.state=state if isinstance(state,dict) else {};ui.renderers=cfg['renderers'];ui.theme_options=cfg['theme_options'];ui.dashboard_widgets=cfg['dashboard_widgets'];ui.custom_boards=cfg['custom_boards'];ui.active_board_id=cfg.get('preview_board_id') or '';ui.context_decks=cfg['context_decks'];ui.active_context_deck=cfg['active_context_deck'];ui.palette_overrides=cfg['palette_overrides'];ui.correlation_keys=cfg['correlation_keys'];ui._apply_palette_overrides();ui.events=live.get('events') or [] if isinstance(live,dict) else []
            raw=(batch or {}).get('histories') or {};ui.histories={k:[x.get('value') for x in v if isinstance(x,dict)] for k,v in raw.items() if isinstance(v,list)};ui.aux={'channel_history':(batch or {}).get('channel_history') or [],'expedition':(batch or {}).get('expedition'),'telemetry':(batch or {}).get('telemetry') or []};ui.page=ui.pages.IDS.index(cfg['page']);logical=ui._compose(ui.page)
            if cfg['page']=='dashboard' and physical!=(480,320):
                label='DASHBOARD'
                if cfg.get('preview_board_id'):
                    label=next((str(b.get('label') or b.get('id')) for b in cfg.get('custom_boards') or [] if b.get('id')==cfg['preview_board_id']),'DASHBOARD')
                im=render_responsive_board(physical,ui.theme,ui.state,preview_widgets,label)
            else:
                im=ui.display_transform.to_physical(logical)
            bio=io.BytesIO();im.save(bio,format='PNG');return bio.getvalue()

    def apply(self,draft: dict)->dict:
        cfg=self.validate(draft);payload={'theme':cfg['theme'],'renderers':cfg['renderers'],'theme_options':cfg['theme_options'],'dashboard_widgets':cfg['dashboard_widgets'],'custom_boards':cfg['custom_boards'],'context_decks':cfg['context_decks'],'active_context_deck':cfg['active_context_deck'],'palette_overrides':cfg['palette_overrides'],'correlation_keys':cfg['correlation_keys']}
        self.prefs.parent.mkdir(parents=True,exist_ok=True)
        if self.prefs.exists():
            bdir=self.prefs.parent/'backups';bdir.mkdir(exist_ok=True);stamp=time.strftime('%Y%m%d-%H%M%S');(bdir/f'preferences-{stamp}.json').write_bytes(self.prefs.read_bytes())
            backups=sorted(bdir.glob('preferences-*.json'),key=lambda p:p.stat().st_mtime,reverse=True)
            for old in backups[12:]:old.unlink(missing_ok=True)
        tmp=self.prefs.with_suffix('.json.tmp');tmp.write_text(json.dumps(payload,indent=2)+'\n');os.replace(tmp,self.prefs)
        return {'ok':True,'theme':cfg['theme'],'applied_at':time.time()}

    @staticmethod
    def _variant_slug(name: str)->str:
        raw=''.join(c.lower() if c.isalnum() else '-' for c in str(name or '').strip())
        slug='-'.join(x for x in raw.split('-') if x)[:48]
        if not slug:raise ValueError('variant name required')
        return slug

    def variants(self)->list[dict]:
        self.variants_dir.mkdir(parents=True,exist_ok=True)
        out=[]
        for fp in sorted(self.variants_dir.glob('*.json')):
            try:obj=json.loads(fp.read_text());out.append({'id':fp.stem,'name':str(obj.get('_variant_name') or fp.stem),'theme':obj.get('theme'),'saved_at':obj.get('_saved_at')})
            except Exception:continue
        return out

    def save_variant(self,name: str,draft: dict)->dict:
        cfg=self.validate(draft);slug=self._variant_slug(name);self.variants_dir.mkdir(parents=True,exist_ok=True)
        payload={k:v for k,v in cfg.items() if k!='page'};payload['_variant_name']=str(name).strip()[:64];payload['_saved_at']=time.time()
        fp=self.variants_dir/f'{slug}.json';tmp=fp.with_suffix('.json.tmp');tmp.write_text(json.dumps(payload,indent=2)+'\n');os.replace(tmp,fp)
        return {'ok':True,'id':slug,'name':payload['_variant_name']}

    def load_variant(self,variant_id: str)->dict:
        slug=self._variant_slug(variant_id);fp=self.variants_dir/f'{slug}.json'
        if not fp.is_file():raise ValueError('variant not found')
        obj=json.loads(fp.read_text());base=self.preferences();base.update({k:v for k,v in obj.items() if not str(k).startswith('_')});return self.validate(base)

    def delete_variant(self,variant_id: str)->dict:
        slug=self._variant_slug(variant_id);fp=self.variants_dir/f'{slug}.json'
        if not fp.is_file():raise ValueError('variant not found')
        fp.unlink();return {'ok':True,'id':slug}

    def platform(self)->dict:
        return self.api.platform_bundle()

    def service_plan(self,obj: dict)->dict:
        return self.actions.plan('service.restart',{'unit':str(obj.get('unit') or '')})

    def service_restart(self,obj: dict)->dict:
        return self.actions.perform('service.restart',{'unit':str(obj.get('unit') or '')})

    def backup_plan(self)->dict:
        return self.actions.plan('backup.create',{})

    def backup_create(self)->dict:
        return self.actions.perform('backup.create',{})

    def backup_inspect(self,name: str)->dict:
        return self.api.backup_inspect(str(name or ''))

    def support_plan(self)->dict:
        return self.actions.plan('support.bundle',{})

    def support_create(self)->dict:
        return self.actions.perform('support.bundle',{})

    def universal_search(self, query: str)->dict:
        return self.api.search(str(query or ''),20)

    def field_library(self, query: str='')->dict:
        return self.api.library(str(query or ''),100)

    def library_item(self, doc_id: str)->dict:
        return self.api.library_item(str(doc_id or ''))

    def library_upload(self,name: str,data: bytes)->dict:
        return self.library_files.save(name,data)

    def library_file(self,doc_id: str):
        meta=self.library_item(doc_id)
        if not meta or meta.get('error'):raise LibraryFileError('library document not found')
        return self.library_files.read(str(meta.get('path') or ''))

    def plugins(self)->dict:
        return self.api.plugins()

    def plugin_plan(self,obj: dict)->dict:
        name=str(obj.get('name') or '')
        enabled=bool(obj.get('enabled'))
        return self.actions.plan('plugin.toggle',{'name':name,'enabled':enabled})

    def plugin_toggle(self,obj: dict)->dict:
        name=str(obj.get('name') or '')
        enabled=bool(obj.get('enabled'))
        return self.actions.perform('plugin.toggle',{'name':name,'enabled':enabled})


class Handler(BaseHTTPRequestHandler):
    server_version='BeastStudio/0.17'
    def log_message(self,fmt,*args):return
    @property
    def st(self)->StudioState:return self.server.studio
    def _auth(self)->bool:
        # Live preview can contain nearby network/field information, so every API
        # endpoint is paired-token protected. The static shell itself is harmless.
        return self.headers.get('X-Beast-Studio-Token','')==self.st.token
    def _send(self,status,body,ctype='application/json'):
        if not isinstance(body,(bytes,bytearray)):body=json.dumps(body,separators=(',',':'),default=str).encode()
        self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
    def do_GET(self):
        path=urlsplit(self.path).path
        if path=='/':return self._send(200,HTML.encode(),'text/html; charset=utf-8')
        if path.startswith('/api/') and not self._auth():return self._send(403,{'error':'paired Studio token required'})
        if path=='/api/schema':return self._send(200,self.st.schema())
        if path=='/api/preferences':return self._send(200,self.st.preferences())
        if path=='/api/plugins':return self._send(200,self.st.plugins())
        if path=='/api/platform':return self._send(200,self.st.platform())
        if path=='/api/backup-inspect':
            name=parse_qs(urlsplit(self.path).query).get('name',[''])[0]
            return self._send(200,self.st.backup_inspect(name))
        if path=='/api/search':
            q=parse_qs(urlsplit(self.path).query).get('q',[''])[0]
            return self._send(200,self.st.universal_search(q))
        if path=='/api/library':
            q=parse_qs(urlsplit(self.path).query).get('q',[''])[0]
            return self._send(200,self.st.field_library(q))
        if path=='/api/library-file':
            doc_id=parse_qs(urlsplit(self.path).query).get('id',[''])[0]
            try:
                data,ctype,name=self.st.library_file(doc_id)
                self.send_response(200);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('Content-Disposition',f'inline; filename="{name.replace(chr(34),"_")}"');self.end_headers();self.wfile.write(data);return
            except LibraryFileError as exc:return self._send(404,{'error':str(exc)})
        if path=='/api/variants':return self._send(200,self.st.variants())
        if path=='/api/token-hint':return self._send(200,{'paired':True})
        return self._send(404,{'error':'not found'})
    def do_PUT(self):
        path=urlsplit(self.path).path
        if path!='/api/library-upload':return self._send(404,{'error':'not found'})
        if not self._auth():return self._send(403,{'error':'paired Studio token required'})
        try:
            n=int(self.headers.get('Content-Length','0') or 0)
            if n<0 or n>64*1024*1024:raise LibraryFileError('invalid or oversized upload')
            name=parse_qs(urlsplit(self.path).query).get('name',[''])[0]
            data=self.rfile.read(n)
            if len(data)!=n:raise LibraryFileError('incomplete upload')
            return self._send(200,self.st.library_upload(name,data))
        except LibraryFileError as exc:return self._send(400,{'error':str(exc)})
        except Exception as exc:return self._send(500,{'error':type(exc).__name__})

    def do_POST(self):
        path=urlsplit(self.path).path
        try:n=min(int(self.headers.get('Content-Length','0') or 0),512_000);obj=json.loads(self.rfile.read(n) or b'{}')
        except Exception:return self._send(400,{'error':'invalid json'})
        try:
            if path in {'/api/preview','/api/apply'} and not self._auth():return self._send(403,{'error':'paired Studio token required'})
            if path in {'/api/plugin-plan','/api/plugin-toggle','/api/service-plan','/api/service-restart','/api/backup-plan','/api/backup-create','/api/support-plan','/api/support-create','/api/variant-save','/api/variant-load','/api/variant-delete'} and not self._auth():return self._send(403,{'error':'paired Studio token required'})
            if path=='/api/preview':return self._send(200,self.st.preview(obj),'image/png')
            if path=='/api/apply':return self._send(200,self.st.apply(obj))
            if path=='/api/service-plan':return self._send(200,self.st.service_plan(obj))
            if path=='/api/service-restart':return self._send(200,self.st.service_restart(obj))
            if path=='/api/backup-plan':return self._send(200,self.st.backup_plan())
            if path=='/api/backup-create':return self._send(200,self.st.backup_create())
            if path=='/api/support-plan':return self._send(200,self.st.support_plan())
            if path=='/api/support-create':return self._send(200,self.st.support_create())
            if path=='/api/plugin-plan':return self._send(200,self.st.plugin_plan(obj))
            if path=='/api/plugin-toggle':return self._send(200,self.st.plugin_toggle(obj))
            if path=='/api/variant-save':return self._send(200,self.st.save_variant(str(obj.get('name') or ''),obj.get('draft') if isinstance(obj.get('draft'),dict) else {}))
            if path=='/api/variant-load':return self._send(200,self.st.load_variant(str(obj.get('id') or '')))
            if path=='/api/variant-delete':return self._send(200,self.st.delete_variant(str(obj.get('id') or '')))
        except ValueError as exc:return self._send(400,{'error':str(exc)})
        except Exception as exc:return self._send(500,{'error':type(exc).__name__})
        return self._send(404,{'error':'not found'})


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True

def serve(host='0.0.0.0',port=8091,root='/opt/beast-ui',prefs='/var/lib/beastagotchi/ui/preferences.json',token_file='/var/lib/beastagotchi/ui/studio.token'):
    state=StudioState(root,prefs,token_file);srv=ReusableThreadingHTTPServer((host,int(port)),Handler);srv.studio=state;srv.serve_forever()

def main():
    p=argparse.ArgumentParser();p.add_argument('--host',default='0.0.0.0');p.add_argument('--port',type=int,default=8091);p.add_argument('--root',default='/opt/beast-ui');p.add_argument('--prefs',default='/var/lib/beastagotchi/ui/preferences.json');p.add_argument('--token-file',default='/var/lib/beastagotchi/ui/studio.token');a=p.parse_args();serve(a.host,a.port,a.root,a.prefs,a.token_file)
