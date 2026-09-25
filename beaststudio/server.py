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
from beastui.face import FaceEngine
from beastui.theme import load_theme, discover_enabled_pack_themes
from beastui.pack_content import discover_enabled_pack_boards, discover_enabled_pack_layouts
from beastui.facepacks import discover_enabled_face_profiles
from beastui.customization import (
    validate_dashboard_widgets, scalar_catalog, dashboard_history_keys, WIDGET_STYLES,
    validate_context_decks, validate_palette_overrides, validate_correlation_keys, validate_custom_boards,
    PALETTE_SLOTS, DEFAULT_CONTEXT_DECKS, MAX_DASHBOARD_WIDGETS,
)
from beastui.apps import AppRegistry
from beastui.qr_render import draw_qr, qr_backend_status
from beastui.experience_registry import (
    experience_renderer_catalog, experience_renderer_summary, render_experience_page,
)
from PIL import Image, ImageDraw
from .action_client import BeastActionClient
from .library_files import LibraryFileManager, LibraryFileError
from .update_policies import UpdatePolicyStore, UpdatePolicyError
from .pack_files import PackFileManager, PackFileError
from .experiences import compose_experience_draft, ExperienceDraftError
from beastcore.depot_catalog import DepotCatalogStore, DepotCatalogError
from beastcore.experience_dna import (
    BUILTIN_EXPERIENCE_DNA, LEGACY_REFERENCE_IDENTITIES, list_experience_families,
)


HTML=r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Beast Studio</title><style>
:root{--bg:#070b10;--panel:#0e151e;--panel2:#121d28;--edge:#223749;--ink:#dceef4;--muted:#78909e;--accent:#35e6d0;--info:#65bfff;--warn:#ffbd57;--danger:#ff6b78;--ok:#79e395}
*{box-sizing:border-box}html,body{height:100%}body{margin:0;background:linear-gradient(145deg,#06090d,#0a1018);color:var(--ink);font:14px system-ui,-apple-system,Segoe UI,sans-serif;overflow:hidden}
header{height:58px;display:flex;align-items:center;padding:0 18px;border-bottom:1px solid var(--edge);background:#091019;gap:14px}header b{font-size:20px;letter-spacing:.08em;color:var(--accent)}header .sub{color:var(--muted)}#conn{margin-left:auto;font-size:12px;border:1px solid var(--edge);padding:5px 10px;border-radius:999px;color:var(--ok)}
main{display:grid;grid-template-columns:330px minmax(520px,1fr) 300px;height:calc(100vh - 58px)}aside{border-right:1px solid var(--edge);background:#0a1119;overflow:auto}.right{border-right:0;border-left:1px solid var(--edge)}.nav{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;padding:10px;position:sticky;top:0;background:#0a1119;z-index:2;border-bottom:1px solid var(--edge)}.tab{border:1px solid var(--edge);background:#0d1720;color:var(--muted);padding:8px;border-radius:8px;cursor:pointer}.tab.active{color:#04110f;background:var(--accent);border-color:var(--accent);font-weight:800}.section{padding:14px}.section.hidden{display:none}h3{margin:0 0 10px;font-size:12px;letter-spacing:.09em;color:var(--accent)}label{display:block;color:var(--muted);font-size:11px;margin:9px 0 4px}select,input,button{width:100%;background:#081019;color:var(--ink);border:1px solid var(--edge);border-radius:7px;padding:8px;font:inherit}input{padding:7px}button{cursor:pointer}button:hover{border-color:#476984}.primary{background:var(--accent);color:#04110f;border-color:var(--accent);font-weight:800}.row{display:grid;grid-template-columns:1fr 1fr;gap:7px}.group{border-top:1px solid var(--edge);padding-top:12px;margin-top:12px}
.preview{display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding:18px;background:radial-gradient(circle at 50% 12%,#142534,#06090e 67%);overflow:auto}.device{width:min(100%,960px);position:relative;margin-top:20px}.screenWrap{position:relative;width:100%}.deviceBadge{position:absolute;top:-24px;left:0;color:var(--muted);font-size:11px;letter-spacing:.08em}#screen{display:block;width:100%;aspect-ratio:3/2;object-fit:contain;border:1px solid #45657a;border-radius:9px;box-shadow:0 20px 55px #000a;background:#000}#layoutOverlay{position:absolute;inset:0;pointer-events:none}.layoutBox{position:absolute;border:2px solid var(--accent);background:#35e6d018;border-radius:5px;pointer-events:auto;cursor:move;user-select:none}.layoutBox.selected{border-color:var(--warn);background:#ffbd5720}.layoutBox.hiddenWidget{border-style:dashed;opacity:.55}.layoutBox .tag{position:absolute;left:2px;top:2px;background:#061017dd;color:var(--ink);font-size:9px;padding:1px 4px;border-radius:3px;max-width:calc(100% - 5px);overflow:hidden;white-space:nowrap}.layoutBox .resize{position:absolute;width:13px;height:13px;right:-2px;bottom:-2px;background:var(--warn);border-radius:3px;cursor:nwse-resize}.composeTools{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:9px}.geom{display:grid;grid-template-columns:repeat(4,1fr);gap:5px}.geom input{padding:5px}.widget.selected{border-color:var(--warn);box-shadow:0 0 0 1px #ffbd5744}.hint{width:min(100%,960px);margin-top:12px;color:var(--muted);font-size:11px;display:flex;justify-content:space-between}
.colorRow{display:grid;grid-template-columns:1fr 64px;gap:8px;align-items:center}.colorRow input[type=color]{height:34px;padding:2px}.deckApp{display:grid;grid-template-columns:24px 1fr 28px 28px;gap:5px;align-items:center;margin:4px 0}.deckApp button{padding:4px}.widget{border:1px solid var(--edge);border-radius:9px;padding:9px;margin:8px 0;background:var(--panel)}.widgetHead{display:flex;align-items:center;gap:8px}.slot{width:22px;height:22px;border-radius:50%;display:grid;place-items:center;background:#162635;color:var(--accent);font-size:11px;font-weight:700}.widget .grid{display:grid;grid-template-columns:1fr 90px;gap:7px}.mini{font-size:10px;color:var(--muted)}
.plugin{border:1px solid var(--edge);border-radius:9px;padding:9px;margin:7px 0;background:var(--panel)}.pluginTop{display:flex;gap:8px;align-items:center}.pluginName{font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1}.pill{font-size:10px;border:1px solid var(--edge);padding:2px 6px;border-radius:999px;color:var(--muted)}.pill.on{color:var(--ok);border-color:#315c48}.pill.integrated{color:var(--info)}.plugin button{margin-top:7px;padding:6px}.plugin button:disabled{opacity:.35;cursor:not-allowed}
.status{font-size:11px;color:var(--muted);margin-top:8px;white-space:pre-wrap}.arch{display:flex;flex-wrap:wrap;gap:5px}.badge{border:1px solid var(--edge);border-radius:999px;padding:3px 7px;color:var(--muted);font-size:10px}
@media(max-width:1050px){body{overflow:auto}main{height:auto;grid-template-columns:1fr}.preview{order:-1;min-height:420px}.right{border-left:0;border-top:1px solid var(--edge)}aside{border-right:0;border-bottom:1px solid var(--edge)}.device{max-width:720px}}
</style></head><body>
<header><b>BEAST STUDIO</b><span class="sub">Live compositor • layered customization • transactional controls</span><span id="conn">CONNECTING</span></header>
<main><aside><div class="nav"><button class="tab active" data-tab="visual">VISUAL</button><button class="tab" data-tab="dashboard">DASH</button><button class="tab" data-tab="decks">DECKS</button><button class="tab" data-tab="data">DATA</button><button class="tab" data-tab="plugins">PLUGINS</button><button class="tab" data-tab="packs">PACKS</button><button class="tab" data-tab="roster">ROSTER</button><button class="tab" data-tab="capsules">CAPSULES</button><button class="tab" data-tab="global">GLOBAL</button><button class="tab" data-tab="search">SEARCH</button><button class="tab" data-tab="ops">OPS</button></div>
<section id="visual" class="section"><h3>VISUAL SYSTEM</h3><label>Theme</label><select id="theme"></select><label>Beast face</label><select id="faceProfile"></select><div class="mini">Built-in follows the active theme. Enabled Face Packs remain separate from personality/mood logic.</div><label>Face motion</label><select id="animationProfile"></select><div class="mini">Animation Packs add bounded declarative motion without video/frame decoding.</div><label>Preview page</label><select id="page"></select><label>Output proof</label><select id="previewOutput"></select><div id="previewOutputNote" class="mini">480×320 is the validated reference layout.</div><div id="themeOpts" class="group"></div><div class="group"><h3>PALETTE OVERRIDES</h3><div class="mini">Theme-native defaults remain underneath. Change only the semantic color slots you want.</div><div id="palette"></div></div><div class="group"><h3>DATA RENDERERS</h3><div id="renderers"></div></div></section>
<section id="dashboard" class="section hidden"><h3>LIVE DASHBOARD COMPOSER</h3><div class="mini">Add, remove, drag, resize, overlap and hide real live instruments. The browser overlay and TFT share the same 12×8 grid; no fake data is introduced.</div><div class="group"><h3>PACK LAYOUT TEMPLATES</h3><div id="packBoardInfo" class="mini"></div><select id="layoutTemplate"></select><button id="importLayout" style="margin-top:7px">IMPORT TEMPLATE AS EDITABLE BOARD</button></div><label>Composition</label><select id="boardSelect"></select><div class="composeTools"><button id="newBoard">+ NEW BOARD</button><button id="deleteBoard">DELETE BOARD</button></div><label>Board name</label><input id="boardLabel" maxlength="22" placeholder="Main Dashboard"><div class="composeTools"><button id="addWidget">+ ADD INSTRUMENT</button><button id="focusDashboard">EDIT ON PREVIEW</button></div><div id="dashWidgets"></div></section>
<section id="decks" class="section hidden"><h3>CONTEXT DECKS</h3><div class="mini">Curated launcher views keep a large app universe clean. ALL always remains available; a deck never hides capability from the system.</div><label>Edit deck</label><select id="deckSelect"></select><label>Deck label</label><input id="deckLabel" maxlength="18"><label><input id="deckActive" type="checkbox" style="width:auto"> Preferred deck</label><div id="deckApps" class="group"></div></section>
<section id="data" class="section hidden"><h3>CORRELATION LAB</h3><div class="mini">Compare the shape of two genuine persisted telemetry histories. Values are normalized only for plotting; source data is never altered.</div><label>Stream A</label><select id="corrA"></select><label>Stream B</label><select id="corrB"></select><div class="group"><h3>PROVENANCE</h3><div class="mini">On the TFT, long-press supported production instruments to open the Widget Inspector and see source, quality, age, units and history.</div></div></section>
<section id="plugins" class="section hidden"><h3>PLUGIN INTEGRATION</h3><div class="mini">Enabled state, Beast integration and safe transactional toggles. Changes are snapshotted, verified and rolled back on failure.</div><button id="refreshPlugins" style="margin-top:9px">REFRESH CATALOG</button><div id="pluginList"></div></section><section id="packs" class="section hidden"><h3>BEAST PACKS / UPDATE CENTER</h3><div class="mini">Local packages can be uploaded, verified, staged and transactionally installed. Safe content-only Packs can also be enabled without executing code or restarting services.</div><div class="group"><h3>DEPOT BROWSER</h3><div class="mini">Catalogs are discovery metadata only. Importing or browsing a catalog never trusts, downloads or installs a Pack.</div><input id="depotSearch" placeholder="Search packs, tags, authors…"><select id="depotType" style="margin-top:7px"><option value="">ALL PACK TYPES</option><option value="theme">THEME</option><option value="face">FACE</option><option value="animation">ANIMATION</option><option value="layout">LAYOUT</option><option value="board">BOARD</option><option value="audio">AUDIO</option><option value="data">DATA</option><option value="map">MAP</option></select><input id="depotFile" type="file" accept=".json" style="margin-top:7px"><button id="uploadDepot" style="margin-top:7px">IMPORT CATALOG JSON</button><div id="depotMeta" class="status"></div><div id="depotList"></div></div><div class="group"><h3>COMPILED EXPERIENCE DNA</h3><div class="mini">Live read-only plans compiled by Beast Core from the shared capability resolver, platform profile and trusted registered renderer coverage. Built-ins and enabled Mission Pack DNA may appear here. Preview is allowed; TFT activation remains locked.</div><div id="builtinExperienceList"></div></div><div class="group"><h3>MISSION EXPERIENCE PROFILES</h3><div class="mini">Mission Packs can compose installed Theme, Face, Animation, Board/Layout and Context Deck pieces without duplicating those assets. v0.19 previews these profiles; Apply is intentionally gated.</div><div id="experienceList"></div></div><div class="group"><h3>LOCAL PACK INTAKE</h3><input id="packFile" type="file" accept=".zip,.tgz,.tar.gz"><button id="uploadPack" style="margin-top:7px">UPLOAD + VERIFY + STAGE</button></div><button id="refreshPacks" style="margin-top:9px">REFRESH CATALOG</button><div id="packSummary" class="group"></div><div id="packList" class="group"></div><div id="packTransactions" class="group"></div><div id="updateList" class="group"></div></section><section id="roster" class="section hidden"><h3>BEAST ROSTER</h3>
<div class="mini">Every Beast and Monster keeps independent progression while resting. Each creature can also remember a preferred presentation. Wake-only leaves the UI untouched; wake + load preferred puts that setup into the Studio draft for review before Apply.</div>
<button id="rosterRefresh" style="margin-top:9px">REFRESH ROSTER</button>
<div id="rosterStatus" class="status"></div>
<div id="rosterList"></div>
<div class="group"><h3>LINEAGE SYNTHESIS</h3><div class="mini">Two distinct level-70+ Beast-class parents may create one v1 Monster. Parents are never consumed or reset. Preview the transaction first; creation is always explicit.</div>
<label>Parent A</label><select id="synthParentA"></select>
<label>Parent B</label><select id="synthParentB"></select>
<label>Monster name</label><input id="synthName" maxlength="64" placeholder="Nova">
<div class="row" style="margin-top:8px"><button id="synthPlan">PREVIEW SYNTHESIS</button><button id="synthCreate" class="primary">CREATE MONSTER</button></div>
<div id="synthStatus" class="status">Choose two eligible Beasts.</div></div>
<div class="group"><h3>HALL OF LEGENDS</h3><div class="mini">Level-100 creatures may be commemorated without forcing them to stay retired. Hall status is independent of active/resting state.</div><button id="hallRefresh">REFRESH HALL + ANCESTRY</button><div id="hallList"></div></div>
<div class="group"><h3>ANCESTRY TREE</h3><div class="mini">Persistent parent/child relationships and mutation lineage. This textual tree foundation will later feed a dedicated visual family-tree renderer.</div><div id="ancestryTree" class="status"></div></div>
</section>
<section id="capsules" class="section hidden"><h3>CAPSULE WORKSHOP</h3>
<div class="mini">Build an exact local preview of a privacy-curated Beast Capsule before sharing it. Export is read-only: this screen does not import, synthesize, publish, or mutate your roster.</div>
<div class="group"><h3>LINEAGE CAPSULE</h3>
<label>Creature</label><select id="capsuleBeast"></select>
<label><input id="capsuleName" type="checkbox" style="width:auto" checked> Include chosen creature name</label>
<label><input id="capsuleAppearance" type="checkbox" style="width:auto" checked> Include curated appearance traits</label>
<label><input id="capsuleAchievements" type="checkbox" style="width:auto"> Include earned achievement IDs</label>
<div class="mini">Achievement count can be present without IDs. Captures, credentials, exact location, logs, raw network history and local roster IDs are never part of the Lineage Capsule.</div>
<button id="capsuleBuild" class="primary" style="margin-top:9px">BUILD EXACT SHARE PREVIEW</button>
<div id="capsuleStatus" class="status">Nothing has been exported yet.</div></div>
<div class="group"><h3>QR TRANSPORT</h3>
<img id="capsuleQr" alt="Capsule QR frame" style="display:none;width:min(100%,420px);aspect-ratio:1/1;object-fit:contain;background:#fff;border:1px solid var(--edge);border-radius:8px">
<div class="row" style="margin-top:8px"><button id="capsulePrev">← PREV FRAME</button><button id="capsuleNext">NEXT FRAME →</button></div>
<div id="capsuleFrameStatus" class="status">Build a Capsule to generate QR-ready frames.</div></div>
<div class="group"><h3>EXACT SHARE SNAPSHOT</h3><div class="mini">This is the exact Capsule envelope currently represented by the QR frames. If a field is not shown here, it is not in this export.</div><pre id="capsulePreview" class="status" style="max-height:420px;overflow:auto;white-space:pre-wrap"></pre></div>
</section>
<section id="global" class="section hidden"><h3>GLOBAL INTERACTION</h3>
<div class="mini">Optional public/community layer. Local Beast data remains authoritative. No Global connector is configured in this milestone, so saving these settings performs no network upload.</div>
<div class="group"><h3>PUBLIC PROFILE</h3>
<label><input id="globalEnabled" type="checkbox" style="width:auto"> Enable a public Beast profile</label>
<label><input id="globalAuto" type="checkbox" style="width:auto"> Automatically queue public revisions when selected public data changes</label>
<label>Creatures to publish</label><select id="globalScope"><option value="active">ACTIVE CREATURE ONLY</option><option value="all">ALL PUBLIC-ELIGIBLE ROSTER CREATURES</option><option value="selected">ONLY SELECTED CREATURES</option></select>
<div id="globalCreatures"></div>
<label><input id="globalNames" type="checkbox" style="width:auto"> Public creature names</label>
<label><input id="globalLineage" type="checkbox" style="width:auto"> Lineage / kind / generation</label>
<label><input id="globalLevel" type="checkbox" style="width:auto"> Level and evolution stage</label>
<label><input id="globalEligible" type="checkbox" style="width:auto"> Lineage-synthesis eligibility</label>
<label><input id="globalMonsters" type="checkbox" style="width:auto"> Include Monsters</label>
<label><input id="globalAncestry" type="checkbox" style="width:auto"> Publish ancestry links between public creatures</label>
<label><input id="globalExperience" type="checkbox" style="width:auto"> Preferred Experience / Theme / Face / Motion identifiers</label>
<label><input id="globalTotals" type="checkbox" style="width:auto"> Public roster totals</label>
<label>Achievements</label><select id="globalAchievements"><option value="none">NONE</option><option value="selected">SELECTED IDS</option><option value="all">ALL EARNED ACHIEVEMENTS</option></select>
<input id="globalAchievementIds" placeholder="selected achievement IDs, comma separated">
<label><input id="globalUnlocks" type="checkbox" style="width:auto"> Selected global unlocks</label>
<input id="globalUnlockIds" placeholder="selected global unlock IDs, comma separated">
<div class="row" style="margin-top:9px"><button id="globalRefresh">REFRESH EXACT PREVIEW</button><button id="globalSave" class="primary">SAVE PRIVACY POLICY</button></div>
<div id="globalStatus" class="status"></div></div>
<div class="group"><h3>EXACT PUBLIC SNAPSHOT</h3><div class="mini">This is the sanitized JSON that a future Global connector would be allowed to send. Fields not shown here are not part of the public mirror.</div><pre id="globalPreview" class="status" style="max-height:420px;overflow:auto;white-space:pre-wrap"></pre></div>
</section>
<section id="search" class="section hidden"><h3>UNIVERSAL BEAST SEARCH</h3><div class="mini">Search offline Field Library documents, BeastDex networks, Capture Vault, durable events and canonical telemetry from one place.</div><label>Search</label><input id="searchQuery" placeholder="GPS, display, network, capture…"><button id="runSearch" style="margin-top:8px">SEARCH BEAST</button><div class="group"><h3>FIELD LIBRARY IMPORT</h3><div class="mini">Import a manual, note, PDF, EPUB or ZIM into Beast’s offline library. Files are stored locally; indexing is automatic.</div><input id="libraryFile" type="file"><button id="uploadLibrary" style="margin-top:7px">IMPORT OFFLINE DOCUMENT</button></div><div id="searchResults" class="group"></div></section><section id="ops" class="section hidden"><h3>BEAST COMMAND CENTER</h3><div class="mini">Whole-platform state, services, tasks, displays and optional runtimes. Service restarts use the same audited Action Broker as the future Beast Operator.</div><button id="refreshOps" style="margin-top:9px">REFRESH OPERATIONS</button><div id="opsSummary" class="group"></div><div id="opsResources" class="group"></div><div id="opsPresentation" class="group"></div><div id="opsIncidents" class="group"></div><div id="opsServices" class="group"></div><div id="opsBackups" class="group"></div><div id="opsSupport" class="group"></div><div id="opsTasks" class="group"></div></section>
</aside>
<section class="preview"><div class="device"><div id="displayBadge" class="deviceBadge">REFERENCE 480 × 320</div><div class="screenWrap"><img id="screen" alt="Exact Beastagotchi preview"><div id="layoutOverlay"></div></div></div><div class="hint"><span id="previewModeLabel">Exact Beast UI compositor</span><span id="previewMeta">draft not applied</span></div></section>
<aside class="right"><section class="section"><h3>DRAFT CONTROL</h3><div class="mini">Everything here is a draft until Apply. Preview uses current Beast Core telemetry and the same renderer as the physical TFT.</div><div class="group"><div class="row"><button id="undo">UNDO</button><button id="redo">REDO</button></div><button id="apply" class="primary" style="margin-top:8px">APPLY TO BEAST</button><button id="reset" style="margin-top:7px">RESET DRAFT</button><div id="status" class="status"></div></div><div class="group"><h3>NAMED VARIANTS</h3><input id="variantName" placeholder="My Field Setup" maxlength="64"><button id="saveVariant" style="margin-top:7px">SAVE CURRENT DRAFT</button><select id="variantList" style="margin-top:7px"></select><div class="row" style="margin-top:7px"><button id="loadVariant">LOAD</button><button id="deleteVariant">DELETE</button></div></div><div class="group"><h3>COMPOSITION PIPELINE</h3><div class="arch"><span class="badge">Live Data</span><span class="badge">Widget</span><span class="badge">Renderer</span><span class="badge">Layout</span><span class="badge">Theme</span><span class="badge">Animation</span></div><p class="mini">Dashboard binding, palettes, decks and saved variants now share the same draft → exact preview → atomic Apply path. Arbitrary drag/resize composition builds on this model.</p></div></section></aside></main>
<script>
let schema=null,base=null,draft=null,undo=[],redo=[],timer=null,plugins=[],variants=[],deckIndex=0,selectedWidget=0,activeTab="visual",dragState=null,boardEditorId="";const $=x=>document.getElementById(x);const TOKEN=new URLSearchParams(location.search).get('token')||'';
function clone(x){return JSON.parse(JSON.stringify(x))}function option(el,v,t){let o=document.createElement('option');o.value=v;o.textContent=t||v;el.appendChild(o)}function push(){undo.push(clone(draft));if(undo.length>60)undo.shift();redo=[]}
async function jfetch(url,opt={}){opt.headers={...(opt.headers||{}),'X-Beast-Studio-Token':TOKEN};let r=await fetch(url,opt);if(!r.ok)throw Error(await r.text());return r.json()}
function mutate(fn){push();fn();rebuild()}function queuePreview(){clearTimeout(timer);timer=setTimeout(preview,90)}
function setTab(id){activeTab=id;document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x.dataset.tab===id));['visual','dashboard','decks','data','plugins','packs','roster','capsules','global','search','ops'].forEach(x=>$(x).classList.toggle('hidden',x!==id));if(id==='plugins')loadPlugins();if(id==='packs')loadPacks();if(id==='roster')loadRoster();if(id==='capsules')loadCapsuleWorkshop();if(id==='global')loadGlobalProfile();if(id==='ops')loadOps();if(id==='dashboard'){draft.page='dashboard';draft.preview_board_id=boardEditorId;queuePreview();renderLayoutOverlay()}else renderLayoutOverlay()}
document.querySelectorAll('.tab').forEach(x=>x.onclick=()=>setTab(x.dataset.tab));
function rebuild(){
 $('theme').innerHTML='';schema.themes.forEach(x=>option($('theme'),x.id,x.label));$('theme').value=draft.theme;
 $('faceProfile').innerHTML='';(schema.face_profiles||[]).forEach(x=>option($('faceProfile'),x.id,x.source_pack?(x.label+' · '+x.source_pack):x.label));$('faceProfile').value=draft.face_profile||'builtin';
 $('animationProfile').innerHTML='';(schema.animation_profiles||[]).forEach(x=>option($('animationProfile'),x.id,x.source_pack?(x.label+' · '+x.source_pack):x.label));$('animationProfile').value=draft.animation_profile||'none';
 $('page').innerHTML='';schema.pages.forEach(x=>option($('page'),x.id,x.title));$('page').value=draft.page||'home';
 draft.preview_output=draft.preview_output||'480x320';let po=$('previewOutput');po.innerHTML='';(schema.preview_outputs||[]).forEach(x=>option(po,x.id,x.label));po.value=draft.preview_output;po.onchange=()=>mutate(()=>draft.preview_output=po.value);updatePreviewOutputChrome();
 let box=$('themeOpts');box.innerHTML='<h3>THEME OPTIONS</h3>';let rows=schema.theme_options[draft.theme]||[];let opts=(draft.theme_options[draft.theme]||{});rows.forEach(r=>{let l=document.createElement('label');l.textContent=r.label;let s=document.createElement('select');r.values.forEach(v=>option(s,String(v)));s.value=String(opts[r.key]??r.default??r.values[0]);s.onchange=()=>mutate(()=>{draft.theme_options[draft.theme]=draft.theme_options[draft.theme]||{};draft.theme_options[draft.theme][r.key]=s.value});box.append(l,s)});
 let rr=$('renderers');rr.innerHTML='';Object.entries(schema.renderers).forEach(([pid,vals])=>{let l=document.createElement('label');l.textContent=pid.toUpperCase();let s=document.createElement('select');vals.forEach(v=>option(s,v));s.value=draft.renderers[pid]||vals[0];s.onchange=()=>mutate(()=>draft.renderers[pid]=s.value);rr.append(l,s)});
 rebuildDashboard();rebuildPalette();rebuildDecks();rebuildData();rebuildPackLayouts();queuePreview();
}
function rebuildPalette(){let box=$('palette');box.innerHTML='';draft.palette_overrides=draft.palette_overrides||{};draft.palette_overrides[draft.theme]=draft.palette_overrides[draft.theme]||{};let baseColors=schema.theme_colors[draft.theme]||{};schema.palette_slots.forEach(slot=>{if(!baseColors[slot])return;let row=document.createElement('div');row.className='colorRow';let l=document.createElement('label');l.textContent=slot.toUpperCase();let c=document.createElement('input');c.type='color';c.value=draft.palette_overrides[draft.theme][slot]||baseColors[slot];c.oninput=()=>{draft.palette_overrides[draft.theme][slot]=c.value;queuePreview()};c.onchange=()=>{rebuild();};row.append(l,c);box.append(row)})}
function rebuildDecks(){draft.context_decks=draft.context_decks||clone(schema.default_context_decks||[]);if(!draft.context_decks.length)return;deckIndex=Math.max(0,Math.min(deckIndex,draft.context_decks.length-1));let sel=$('deckSelect');sel.innerHTML='';draft.context_decks.forEach((d,i)=>option(sel,String(i),d.label||d.id));sel.value=String(deckIndex);sel.onchange=()=>{deckIndex=Number(sel.value)||0;rebuildDecks()};let d=draft.context_decks[deckIndex];$('deckLabel').value=d.label||d.id;$('deckLabel').onchange=()=>mutate(()=>d.label=$('deckLabel').value.toUpperCase().slice(0,18));$('deckActive').checked=draft.active_context_deck===d.id;$('deckActive').onchange=()=>mutate(()=>draft.active_context_deck=$('deckActive').checked?d.id:'');let box=$('deckApps');box.innerHTML='<h3>DECK APPS</h3>';let ids=d.apps||[];[...schema.apps,...boardApps()].forEach(app=>{let row=document.createElement('div');row.className='deckApp';let ck=document.createElement('input');ck.type='checkbox';ck.checked=ids.includes(app.id);let title=document.createElement('span');title.textContent=app.title;let up=document.createElement('button');up.textContent='↑';let dn=document.createElement('button');dn.textContent='↓';ck.onchange=()=>mutate(()=>{let pos=d.apps.indexOf(app.id);if(ck.checked&&pos<0)d.apps.push(app.id);if(!ck.checked&&pos>=0)d.apps.splice(pos,1)});up.onclick=()=>mutate(()=>{let pos=d.apps.indexOf(app.id);if(pos>0){let x=d.apps[pos-1];d.apps[pos-1]=app.id;d.apps[pos]=x}});dn.onclick=()=>mutate(()=>{let pos=d.apps.indexOf(app.id);if(pos>=0&&pos<d.apps.length-1){let x=d.apps[pos+1];d.apps[pos+1]=app.id;d.apps[pos]=x}});row.append(ck,title,up,dn);box.append(row)})}
function rebuildData(){draft.correlation_keys=draft.correlation_keys||['system.cpu.total','system.temp.cpu_c'];[['corrA',0],['corrB',1]].forEach(([id,idx])=>{let s=$(id);s.innerHTML='';schema.dashboard_keys.forEach(r=>option(s,r.key,`${r.category||'Other'} · ${r.label||r.key}`));s.value=draft.correlation_keys[idx]||'';s.onchange=()=>mutate(()=>draft.correlation_keys[idx]=s.value)})}
function rebuildPackLayouts(){let sel=$('layoutTemplate'),btn=$('importLayout'),info=$('packBoardInfo');if(!sel||!btn)return;sel.innerHTML='';let layouts=schema.pack_layouts||[];option(sel,'',layouts.length?'SELECT A PACK TEMPLATE':'NO ENABLED LAYOUT PACKS');layouts.forEach(x=>option(sel,x.id,(x.label||x.id)+' · '+(x.source_pack||'')));btn.disabled=!layouts.length;info.textContent=(schema.pack_boards||[]).length+' read-only Pack board(s) available in the Beast launcher · '+layouts.length+' reusable layout template(s)';}
function uniqueBoardId(label){let base=String(label||'board').toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_+|_+$/g,'').slice(0,32)||'board',id=base,n=2;while((draft.custom_boards||[]).some(b=>b.id===id)){id=(base+'_'+n++).slice(0,40)}return id}
function importPackLayout(){let id=$('layoutTemplate').value,row=(schema.pack_layouts||[]).find(x=>x.id===id);if(!row)return;mutate(()=>{draft.custom_boards=draft.custom_boards||[];let bid=uniqueBoardId(row.label||row.local_id||'pack_layout');draft.custom_boards.push({id:bid,label:String(row.label||'Pack Layout').slice(0,22),widgets:clone(row.widgets||[])});boardEditorId=bid;draft.preview_board_id=bid;draft.page='dashboard';selectedWidget=0});$('status').textContent='Pack layout imported as an editable personal board. The original Pack template remains read-only.'}
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
$('importLayout').onclick=importPackLayout;$('rosterRefresh').onclick=async()=>{await loadRoster();await loadHall()};$('hallRefresh').onclick=loadHall;$('synthPlan').onclick=previewSynthesis;$('synthCreate').onclick=createSynthesis;$('capsuleBuild').onclick=buildCapsulePreview;$('capsulePrev').onclick=()=>showCapsuleFrame(capsuleFrame-1);$('capsuleNext').onclick=()=>showCapsuleFrame(capsuleFrame+1);
$('globalRefresh').onclick=loadGlobalProfile;$('globalSave').onclick=saveGlobalPolicy;$('globalScope').onchange=()=>drawGlobalRoster(globalPolicyFromForm());$('addWidget').onclick=()=>{let rows=currentWidgetList();if(rows.length>=schema.max_dashboard_widgets){$('status').textContent='Composition safety limit reached.';return}mutate(()=>{rows=currentWidgetList();rows.push(defaultWidget(rows.length));selectedWidget=rows.length-1;draft.page='dashboard';draft.preview_board_id=boardEditorId})};$('focusDashboard').onclick=()=>{draft.page='dashboard';draft.preview_board_id=boardEditorId;$('page').value='dashboard';queuePreview();renderLayoutOverlay()};$('newBoard').onclick=()=>{let name=prompt('Board name','My Board');if(!name)return;mutate(()=>{draft.custom_boards=draft.custom_boards||[];let baseId=name.toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_+|_+$/g,'').slice(0,32)||'board';let id=baseId,n=2;while(draft.custom_boards.some(b=>b.id===id)){id=baseId+'_'+n++}let widgets=[defaultWidget(0),defaultWidget(1),defaultWidget(2)];draft.custom_boards.push({id,label:name.slice(0,22),widgets});boardEditorId=id;draft.preview_board_id=id;draft.page='dashboard';selectedWidget=0})};$('deleteBoard').onclick=()=>{let b=boardById(boardEditorId);if(!b||!confirm(`Delete board ${b.label||b.id}?`))return;mutate(()=>{draft.custom_boards=draft.custom_boards.filter(x=>x.id!==boardEditorId);(draft.context_decks||[]).forEach(d=>d.apps=(d.apps||[]).filter(x=>x!==`board:${boardEditorId}`));boardEditorId='';draft.preview_board_id='';selectedWidget=0})}

async function preview(){try{$('conn').textContent='RENDERING';updatePreviewOutputChrome();let r=await fetch('/api/preview',{method:'POST',headers:{'content-type':'application/json','X-Beast-Studio-Token':TOKEN},body:JSON.stringify(draft)});if(!r.ok)throw Error(await r.text());let b=await r.blob();let old=$('screen').src;$('screen').src=URL.createObjectURL(b);if(old&&old.startsWith('blob:'))URL.revokeObjectURL(old);$('conn').textContent='LIVE';let po=previewOutputInfo();$('previewMeta').textContent=`${draft.theme} · ${draft.page}${boardEditorId?' · '+(boardById(boardEditorId)?.label||boardEditorId):''} · ${po.width}×${po.height}`;renderLayoutOverlay()}catch(e){$('conn').textContent='ERROR';$('status').textContent=e}}
async function loadPlugins(){try{let x=await jfetch('/api/plugins');plugins=x.items||[];renderPlugins()}catch(e){$('pluginList').innerHTML='<div class="status">Plugin catalog unavailable: '+e+'</div>'}}
function renderPlugins(){let box=$('pluginList');box.innerHTML='';plugins.forEach(p=>{let c=document.createElement('div');c.className='plugin';let top=document.createElement('div');top.className='pluginTop';let name=document.createElement('span');name.className='pluginName';name.textContent=p.name;let st=document.createElement('span');st.className='pill '+(p.enabled?'on':'');st.textContent=p.enabled?'ON':'OFF';let integ=document.createElement('span');integ.className='pill '+(!['config_only','isolated'].includes(p.integration)?'integrated':'');integ.textContent=p.integration||'config_only';top.append(name,st,integ);c.append(top);let meta=document.createElement('div');meta.className='mini';meta.textContent=`${p.role||'plugin'} · ${p.display_policy||''}${p.protected?' · protected':''}`;c.append(meta);let btn=document.createElement('button');btn.textContent=p.enabled?'DISABLE':'ENABLE';btn.disabled=!p.toggle_capable||p.protected||(p.legacy_display_owner&&!p.enabled);btn.onclick=()=>togglePlugin(p,btn);c.append(btn);box.append(c)});if(!plugins.length)box.innerHTML='<div class="status">No plugins reported yet.</div>'}
async function togglePlugin(p,btn){let wanted=!p.enabled;btn.disabled=true;$('status').textContent='Planning plugin change…';try{let plan=await jfetch('/api/plugin-plan',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({name:p.name,enabled:wanted})});let pp=plan.plan||{};if(!pp.allowed)throw Error((pp.blockers||['blocked']).join('; '));let msg=`${wanted?'Enable':'Disable'} ${p.name}?\n\nA config snapshot will be taken. Pwnagotchi will be restarted if required and the change will roll back automatically if health verification fails.`;if(!confirm(msg)){btn.disabled=false;return}let result=await jfetch('/api/plugin-toggle',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({name:p.name,enabled:wanted})});let row=result.action_row||{};$('status').textContent=`Plugin ${p.name}: ${row.status||result.error||'unknown'}`;await new Promise(r=>setTimeout(r,900));await loadPlugins()}catch(e){$('status').textContent='Plugin change failed: '+e;btn.disabled=false}}
async function stageUpdate(r,btn){btn.disabled=true;try{let x=await jfetch('/api/update-stage-plan',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({component:r.id})});let plan=x.plan||{};if(!plan.allowed)throw Error((plan.blockers||['blocked']).join('; '));let a=plan.asset||{};if(!confirm('Download and SHA-256 verify '+(a.name||'release archive')+' for '+(r.label||r.id)+'?\n\nThis only stages the verified archive. It will not install or restart anything.'))return;let out=await jfetch('/api/update-stage',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({component:r.id,asset_name:a.name||''})});let row=out.action_row||{};$('status').textContent=row.status==='success'?'Verified update staged.':'Update staging failed.';await new Promise(r=>setTimeout(r,400));await loadPacks()}catch(e){$('status').textContent='Update staging failed: '+e}finally{btn.disabled=false}}
async function applyPackUpdate(r,btn){btn.disabled=true;try{
  let x=await jfetch('/api/update-pack-plan',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({component:r.id})});
  let plan=x.plan||{};if(!plan.allowed)throw Error((plan.blockers||['blocked']).join('; '));
  let to=plan.available_version||r.available_version||'?';
  if(!confirm('Apply verified Beast Pack update for '+(r.label||r.id)+' → '+to+'?\n\nThe release will be SHA-256 verified, re-inspected as a Beast Pack, transactionally installed to the inert registry, checked, and rolled back automatically if probation fails. It will NOT activate the pack or restart services.'))return;
  let out=await jfetch('/api/update-pack-apply',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({component:r.id})});
  let row=out.action_row||{};$('status').textContent=row.status==='success'?'Verified Beast Pack update installed to inert registry.':'Pack update failed / rolled back.';
  await new Promise(q=>setTimeout(q,500));await loadPacks();
}catch(e){$('status').textContent='Pack update failed: '+e}finally{btn.disabled=false}}
async function setUpdatePolicy(component,policy,select){select.disabled=true;try{await jfetch('/api/update-policy',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({component,policy})});$('status').textContent=`Update policy saved: ${component} → ${policy}`;await new Promise(r=>setTimeout(r,250));await loadPacks()}catch(e){$('status').textContent='Policy save failed: '+e}finally{select.disabled=false}}
async function uploadPack(){let f=$('packFile').files[0];if(!f){$('status').textContent='Choose a Beast Pack archive first.';return}let btn=$('uploadPack');btn.disabled=true;try{$('status').textContent='Uploading '+f.name+'…';let r=await fetch('/api/pack-upload?name='+encodeURIComponent(f.name),{method:'PUT',headers:{'X-Beast-Studio-Token':TOKEN},body:f});if(!r.ok)throw Error(await r.text());let up=await r.json();let inspect=await jfetch('/api/pack-inspect',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({name:up.name})});let row=inspect.action_row||{};if(row.status!=='success')throw Error(row.result?.error||'inspection failed');let m=row.result?.manifest||{};if(!confirm('Verified '+(m.label||m.id||up.name)+' v'+(m.version||'?')+'.\n\nStage this pack? Staging does not execute or install it.'))return;let staged=await jfetch('/api/pack-stage',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({name:up.name,replace:true})});let sr=staged.action_row||{};$('status').textContent=sr.status==='success'?'Pack verified and staged.':'Pack staging failed.';await new Promise(r=>setTimeout(r,400));await loadPacks()}catch(e){$('status').textContent='Pack intake failed: '+e}finally{btn.disabled=false}}
$('uploadPack').onclick=uploadPack;
async function installPack(p,btn){btn.disabled=true;try{let x=await jfetch('/api/pack-install-plan',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:p.id})});let plan=x.plan||{};if(!plan.allowed)throw Error((plan.blockers||['blocked']).join('; '));let warning=(plan.warnings||[]).join('\n');if(!confirm('Install '+(p.label||p.id)+' v'+(p.version||'?')+' into Beast\'s managed registry?\n\nNo code will execute and no service will restart.'+(warning?'\n\n'+warning:'')))return;let r=await jfetch('/api/pack-install',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:p.id})});let row=r.action_row||{};$('status').textContent=row.status==='success'?'Pack installed to inert registry.':'Pack install failed.';await new Promise(r=>setTimeout(r,500));await loadPacks()}catch(e){$('status').textContent='Pack install failed: '+e}finally{btn.disabled=false}}
async function togglePackActivation(p,btn){btn.disabled=true;let wanted=!p.enabled;try{
  let endpoint=wanted?'/api/pack-activate-plan':'/api/pack-deactivate-plan';
  let execEndpoint=wanted?'/api/pack-activate':'/api/pack-deactivate';
  let x=await jfetch(endpoint,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:p.id})});
  let plan=x.plan||{};if(!plan.allowed)throw Error((plan.blockers||['blocked']).join('; '));
  if(!confirm((wanted?'Enable ':'Disable ')+(p.label||p.id)+'?\n\nThis content-only activation does not execute Pack code or restart services.'))return;
  let out=await jfetch(execEndpoint,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:p.id})});
  let row=out.action_row||{};$('status').textContent=row.status==='success'?(wanted?'Pack enabled.':'Pack disabled.'):'Pack activation change failed.';
  await new Promise(q=>setTimeout(q,500));await loadPacks();
}catch(e){$('status').textContent='Pack activation failed: '+e}finally{btn.disabled=false}}
async function rollbackPack(tx,btn){btn.disabled=true;try{let x=await jfetch('/api/pack-rollback-plan',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({transaction_id:tx.id})});let plan=x.plan||{};if(!plan.allowed)throw Error((plan.blockers||['blocked']).join('; '));if(!confirm('Roll back '+(tx.pack_id||'this pack')+' transaction '+tx.id+'?'))return;let r=await jfetch('/api/pack-rollback',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({transaction_id:tx.id})});let row=r.action_row||{};$('status').textContent=row.status==='success'?'Pack rollback complete.':'Pack rollback failed.';await new Promise(r=>setTimeout(r,500));await loadPacks()}catch(e){$('status').textContent='Rollback failed: '+e}finally{btn.disabled=false}}
let depotCache=[];
function renderDepot(localPacks=[]){let q=String($('depotSearch')?.value||'').trim().toLowerCase(),type=String($('depotType')?.value||'');let box=$('depotList');if(!box)return;box.innerHTML='';let installed=new Map((localPacks||[]).map(x=>[String(x.id||''),x]));let rows=depotCache.filter(r=>{if(type&&r.pack_type!==type)return false;if(!q)return true;let hay=[r.id,r.label,r.description,r.author,...(r.tags||[])].join(' ').toLowerCase();return hay.includes(q)});rows.slice(0,80).forEach(r=>{let local=installed.get(String(r.id||''));let d=document.createElement('div');d.className='plugin';let top=document.createElement('div');top.className='pluginTop';let n=document.createElement('span');n.className='pluginName';n.textContent=r.label||r.id;let pill=document.createElement('span');pill.className='pill '+(local?'on':'');pill.textContent=local?'LOCAL '+String(local.version||'?'):'DISCOVER';top.append(n,pill);d.append(top);let meta=document.createElement('div');meta.className='mini';meta.textContent=(r.pack_type||'pack')+' · catalog v'+(r.version||'?')+' · '+(r.author||'unknown author')+' · '+(r.catalog||'catalog');d.append(meta);if(r.description){let desc=document.createElement('div');desc.className='mini';desc.textContent=r.description;d.append(desc)}let src=document.createElement('div');src.className='status';src.textContent='Source metadata: '+(r.source?.repository||'--')+' · catalog listing does NOT grant trust';d.append(src);box.append(d)});if(!rows.length)box.innerHTML='<div class="status">No catalog entries match this filter.</div>'}
async function loadDepot(localPacks=[]){try{let x=await jfetch('/api/depot');depotCache=x.items||[];$('depotMeta').textContent=(x.catalog_count||0)+' catalog(s) · '+(x.count||0)+' entries · '+(x.conflicts||[]).length+' duplicate-ID conflict(s) · remote refresh '+(x.remote_refresh_enabled?'enabled':'not yet enabled');renderDepot(localPacks)}catch(e){depotCache=[];$('depotMeta').textContent='Depot catalogs unavailable: '+e;renderDepot(localPacks)}}
async function uploadDepot(){let f=$('depotFile').files[0];if(!f){$('status').textContent='Choose a Depot catalog JSON first.';return}let btn=$('uploadDepot');btn.disabled=true;try{let r=await fetch('/api/depot-upload?name='+encodeURIComponent(f.name),{method:'PUT',headers:{'X-Beast-Studio-Token':TOKEN,'Content-Type':'application/json'},body:f});let x=await r.json();if(!r.ok)throw Error(x.error||r.statusText);$('status').textContent='Imported '+x.name+' · '+x.count+' valid Pack entries. Catalog does not grant trust.';$('depotFile').value='';await loadPacks()}catch(e){$('status').textContent='Depot import failed: '+e}finally{btn.disabled=false}}
$('uploadDepot').onclick=uploadDepot;$('depotSearch').oninput=()=>renderDepot(window._localPackRows||[]);$('depotType').onchange=()=>renderDepot(window._localPackRows||[]);
async function previewExperience(r,btn){btn.disabled=true;try{
  let out=await jfetch('/api/experience-draft',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:r.id})});
  draft=clone(out.draft);undo=[];redo=[];rebuild();setTab('visual');
  $('status').textContent='Experience loaded into draft only. '+(out.warnings||[]).join(' · ')+(out.warnings&&out.warnings.length?' · ':'')+'Review the live preview, adjust anything you want, then use APPLY TO BEAST if you want to keep it.';
}catch(e){$('status').textContent='Experience preview failed: '+e}finally{btn.disabled=false}}

async function previewCompiledExperience(plan,page,btn){btn.disabled=true;try{
  let id=plan.experience_id||'',renderer=plan.renderer_experience_id||id,src=plan.source||{};
  let r=await fetch('/api/experience-preview',{method:'POST',headers:{'X-Beast-Studio-Token':TOKEN,'content-type':'application/json'},body:JSON.stringify({id:renderer,page})});
  if(!r.ok){let t=await r.text();throw Error(t||r.statusText)}
  let blob=await r.blob(),old=$('screen').dataset.objectUrl||'';if(old)URL.revokeObjectURL(old);
  let url=URL.createObjectURL(blob);$('screen').dataset.objectUrl=url;$('screen').src=url;
  $('previewModeLabel').textContent='Experience DNA renderer';
  $('previewMeta').textContent=(plan.label||id).toUpperCase()+' · '+page.toUpperCase()+(renderer!==id?' · RENDERER '+renderer.toUpperCase():'')+' · Core read-only plan';
  $('status').textContent='Previewing '+(plan.label||id)+' / '+page+(src.kind==='pack'?' from Pack '+(src.pack_id||''):'')+'. Nothing was applied and TFT ownership remains unchanged.';
}catch(e){$('status').textContent='Compiled Experience preview failed: '+e}finally{btn.disabled=false}}

async function planTryOnTft(plan,page,btn){btn.disabled=true;try{
  let x=await jfetch('/api/experience-try-plan',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:plan.experience_id,page,duration_sec:90})});
  let blockers=x.blockers||[],warnings=x.warnings||[];
  $('status').textContent=(x.plan_ready?'TRY ON TFT plan ready':'TRY ON TFT remains locked')+' · '+(blockers.length?blockers.join(' · '):'no planning blockers')+(warnings.length?' · '+warnings[0]:'');
}catch(e){$('status').textContent='TRY ON TFT plan failed: '+e}finally{btn.disabled=false}}

function renderBuiltinExperiences(plan){
  let box=$('builtinExperienceList');if(!box)return;box.innerHTML='';
  let rows=(plan&&plan.items)||[];
  rows.forEach(r=>{let d=document.createElement('div');d.className='plugin';let cov=r.page_coverage||{},variant=r.variant||{},caps=r.capabilities||{},ready=!!r.ready_for_preview;
    let top=document.createElement('div');top.className='pluginTop';let n=document.createElement('span');n.className='pluginName';n.textContent=r.label||r.experience_id;let pill=document.createElement('span');pill.className='pill '+(ready?'on':'');pill.textContent=ready?'PREVIEW READY':'NO HOME PROOF';top.append(n,pill);d.append(top);
    let src=r.source||{},sourceLabel=src.kind==='pack'?'PACK '+String(src.pack_id||'').toUpperCase():'BUILT-IN';
    let meta=document.createElement('div');meta.className='mini';meta.textContent=sourceLabel+' · '+(variant.visual_family||'experience')+' · '+(variant.quality_variant||'full')+' · '+(variant.display_class||'unknown')+' display'+(r.renderer_experience_id?' · renderer '+r.renderer_experience_id:'');d.append(meta);
    let pages=document.createElement('div');pages.className='mini';pages.textContent='Implemented: '+((cov.implemented||[]).join(', ')||'none')+' · Missing preferred: '+((cov.missing_preferred||[]).join(', ')||'none');d.append(pages);
    let missing=(caps.optional_missing||[]);if(missing.length){let m=document.createElement('div');m.className='status';m.textContent='Optional enrichments unavailable: '+missing.join(', ');d.append(m)}
    (cov.implemented||[]).forEach(page=>{let b=document.createElement('button');b.textContent='PREVIEW '+String(page).toUpperCase();b.onclick=()=>previewCompiledExperience(r,page,b);d.append(b)});
    if((cov.implemented||[]).includes('home')){let t=document.createElement('button');t.textContent='TRY ON TFT PLAN';t.onclick=()=>planTryOnTft(r,'home',t);d.append(t)}
    box.append(d)});
  if(!rows.length)box.innerHTML='<div class="status">Core Experience plans are not available yet.</div>';
}

let globalLocalRoster=[];
function csvList(v){return String(v||'').split(',').map(x=>x.trim()).filter(Boolean)}
function globalPolicyFromForm(){
  return {
    enabled:$('globalEnabled').checked,auto_sync:$('globalAuto').checked,roster_scope:$('globalScope').value,
    selected_creature_ids:[...document.querySelectorAll('#globalCreatures input[type=checkbox]:checked')].map(x=>x.value),
    publish_names:$('globalNames').checked,publish_lineage:$('globalLineage').checked,
    publish_level_stage:$('globalLevel').checked,publish_synthesis_eligibility:$('globalEligible').checked,
    publish_monsters:$('globalMonsters').checked,publish_ancestry:$('globalAncestry').checked,
    publish_experience:$('globalExperience').checked,publish_roster_totals:$('globalTotals').checked,
    publish_achievements:$('globalAchievements').value,selected_achievement_ids:csvList($('globalAchievementIds').value),
    publish_global_unlocks:$('globalUnlocks').checked,selected_global_unlock_ids:csvList($('globalUnlockIds').value)
  }
}
function drawGlobalRoster(policy){
  let box=$('globalCreatures');box.innerHTML='';globalLocalRoster.forEach(r=>{let lab=document.createElement('label');let c=document.createElement('input');c.type='checkbox';c.style.width='auto';c.value=r.id;c.checked=(policy.selected_creature_ids||[]).includes(r.id);lab.append(c,document.createTextNode(' '+(r.name||r.id)+' · '+String(r.kind||'BEAST').toUpperCase()+' · LV'+(r.level||1)+(r.active?' · ACTIVE':'')));box.append(lab)});box.style.display=$('globalScope').value==='selected'?'block':'none'
}
function fillGlobalPolicy(p){
  $('globalEnabled').checked=!!p.enabled;$('globalAuto').checked=!!p.auto_sync;$('globalScope').value=p.roster_scope||'active';
  $('globalNames').checked=!!p.publish_names;$('globalLineage').checked=!!p.publish_lineage;$('globalLevel').checked=!!p.publish_level_stage;
  $('globalEligible').checked=!!p.publish_synthesis_eligibility;$('globalMonsters').checked=!!p.publish_monsters;$('globalAncestry').checked=!!p.publish_ancestry;
  $('globalExperience').checked=!!p.publish_experience;$('globalTotals').checked=!!p.publish_roster_totals;$('globalAchievements').value=p.publish_achievements||'none';
  $('globalAchievementIds').value=(p.selected_achievement_ids||[]).join(', ');$('globalUnlocks').checked=!!p.publish_global_unlocks;$('globalUnlockIds').value=(p.selected_global_unlock_ids||[]).join(', ');
  drawGlobalRoster(p)
}
let capsuleExport=null,capsuleFrame=0,capsuleQrUrl='';
async function loadCapsuleWorkshop(){try{
  let x=await jfetch('/api/roster'),sel=$('capsuleBeast');sel.innerHTML='';
  let rows=x.items||[];if(!rows.length){option(sel,'','NO CREATURES AVAILABLE');$('capsuleBuild').disabled=true;$('capsuleStatus').textContent='No persistent Beast roster is available.';return}
  rows.forEach(r=>option(sel,r.id,(r.active?'★ ':'')+(r.name||r.id)+' · '+String(r.kind||'beast').toUpperCase()+' · LV '+(r.level||1)+' '+(r.stage||'')));
  let active=rows.find(r=>r.active)||rows[0];sel.value=active.id;$('capsuleBuild').disabled=false;
  if(!capsuleExport){$('capsuleStatus').textContent='Ready to build an exact read-only Lineage Capsule preview for '+(active.name||active.id)+'.'}
}catch(e){$('capsuleStatus').textContent='Capsule Workshop unavailable: '+e}}
function capsuleFrames(){return (((capsuleExport||{}).qr||{}).frames||[]).map(String)}
async function showCapsuleFrame(idx){
  let frames=capsuleFrames(),img=$('capsuleQr');if(!frames.length){img.style.display='none';$('capsuleFrameStatus').textContent='No QR frames are available.';return}
  capsuleFrame=((Number(idx)||0)%frames.length+frames.length)%frames.length;
  let frame=frames[capsuleFrame],stat=(capsuleExport||{}).studio_qr||{};
  if(!stat.available){img.style.display='none';$('capsuleFrameStatus').textContent='QR renderer unavailable on this Beast runtime. Text frames remain valid.';return}
  try{
    let r=await fetch('/api/capsule-qr',{method:'POST',headers:{'content-type':'application/json','X-Beast-Studio-Token':TOKEN},body:JSON.stringify({frame:frame})});
    if(!r.ok)throw Error(await r.text());let blob=await r.blob();if(capsuleQrUrl)URL.revokeObjectURL(capsuleQrUrl);capsuleQrUrl=URL.createObjectURL(blob);img.src=capsuleQrUrl;img.style.display='block';
    $('capsuleFrameStatus').textContent='FRAME '+(capsuleFrame+1)+' / '+frames.length+' · '+frame.length+' characters · BCQ1 transport · scan/share only';
  }catch(e){img.style.display='none';$('capsuleFrameStatus').textContent='QR render failed: '+e}
}
async function buildCapsulePreview(){
  let beast=$('capsuleBeast').value;if(!beast){$('capsuleStatus').textContent='Choose a creature first.';return}
  $('capsuleBuild').disabled=true;$('capsuleStatus').textContent='Building privacy-curated Capsule preview…';
  try{
    let x=await jfetch('/api/capsule-preview',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({
      beast_id:beast,include_name:$('capsuleName').checked,include_appearance:$('capsuleAppearance').checked,
      include_achievements:$('capsuleAchievements').checked,qr_chars:220
    })});
    capsuleExport=x;capsuleFrame=0;
    if(!x.ok)throw Error(x.error||'Capsule export failed');
    let env=x.envelope||{},payload=env.payload||{},privacy=env.privacy||{},integrity=env.integrity||{},frames=capsuleFrames();
    $('capsulePreview').textContent=JSON.stringify(env,null,2);
    $('capsuleStatus').textContent='EXACT PREVIEW · '+(payload.name||'NAME HIDDEN')+' · '+String(payload.kind||'beast').toUpperCase()+' · LV '+(payload.level??'--')+' '+(payload.stage||'')+
      ' · '+frames.length+' QR frame(s) · '+(x.encoded_chars||0)+' encoded chars · '+(integrity.authenticated?'SIGNED/AUTHENTICATED':'UNSIGNED · INTEGRITY ONLY')+
      '\nPrivacy: captures '+(privacy.captures_included?'INCLUDED':'NO')+' · credentials '+(privacy.credentials_included?'INCLUDED':'NO')+' · exact location '+(privacy.exact_location_included?'INCLUDED':'NO')+' · network history '+(privacy.network_history_included?'INCLUDED':'NO')+
      '\nNo import or publication was performed.';
    await showCapsuleFrame(0)
  }catch(e){capsuleExport=null;$('capsulePreview').textContent='';$('capsuleQr').style.display='none';$('capsuleStatus').textContent='Capsule preview failed: '+e}
  finally{$('capsuleBuild').disabled=false}
}
let rosterRows=[];
async function loadRoster(){try{
  let x=await jfetch('/api/roster');rosterRows=x.items||[];let box=$('rosterList');box.innerHTML='';
  (x.items||[]).forEach(r=>{let d=document.createElement('div');d.className='plugin';
    let active=!!r.active,eligible=!!r.synthesis_eligible,hasPref=!!r.has_preferred_presentation;
    d.innerHTML=`<div class="pluginTop"><span class="pluginName">${r.name||r.id}</span><span class="pill ${active?'on':''}">${active?'ACTIVE':String(r.status||'RESTING').toUpperCase()}</span></div>
      <div class="mini">${String(r.kind||'beast').toUpperCase()} · LV ${r.level||1} · ${r.stage||''} · ${r.lineage_id||'standard'} · GEN ${r.generation||0}</div>
      <div class="mini">${r.achievement_count||0} achievements${eligible?' · LINEAGE ELIGIBLE':''}${(r.parent_ids||[]).length?' · '+r.parent_ids.length+' recorded parents':''}</div>
      <div class="mini">${(r.memory_summary||{}).memory_count||0} memories · ${(r.memory_summary||{}).expedition_count||0} expeditions · ${(r.memory_summary||{}).rare_witness_count||0} rare witnesses</div>
      <div class="status">Preferred setup: ${hasPref?'SAVED':'not saved'}</div>`;
    if(active){let save=document.createElement('button');save.textContent=hasPref?'UPDATE PREFERRED FROM CURRENT DRAFT':'REMEMBER CURRENT DRAFT AS PREFERRED';save.onclick=()=>rememberRosterPresentation(r.id,r.name||r.id,save);d.append(save)}
    if(!active){let wake=document.createElement('button');wake.textContent='WAKE ONLY';wake.onclick=()=>switchRoster(r.id,r.name||r.id,wake,false);d.append(wake);
      if(hasPref){let restore=document.createElement('button');restore.textContent='WAKE + LOAD PREFERRED SETUP';restore.onclick=()=>switchRoster(r.id,r.name||r.id,restore,true);d.append(restore)}}
    if(hasPref){let clear=document.createElement('button');clear.textContent='FORGET PREFERRED SETUP';clear.onclick=()=>clearRosterPresentation(r.id,r.name||r.id,clear);d.append(clear)}
    box.append(d)
  });
  $('rosterStatus').textContent=(x.count||0)+' persistent creatures · '+((x.items||[]).filter(r=>r.active).length?'one active':'no active creature');
  let elig=rosterRows.filter(r=>r.synthesis_eligible),a=$('synthParentA'),b=$('synthParentB');a.innerHTML='';b.innerHTML='';
  option(a,'','SELECT ELIGIBLE BEAST');option(b,'','SELECT ELIGIBLE BEAST');
  elig.forEach(r=>{option(a,r.id,(r.name||r.id)+' · LV '+r.level+' '+r.stage);option(b,r.id,(r.name||r.id)+' · LV '+r.level+' '+r.stage)});
  $('synthPlan').disabled=elig.length<2;$('synthCreate').disabled=elig.length<2;

}catch(e){$('rosterStatus').textContent='Roster unavailable: '+e}}
async function loadHall(){try{
  let h=await jfetch('/api/roster-hall'),box=$('hallList');box.innerHTML='';
  let all=[...(h.inductees||[]),...(h.candidates||[])];
  if(!all.length)box.innerHTML='<div class="status">No level-100 Hall candidates yet.</div>';
  all.forEach(r=>{let d=document.createElement('div');d.className='plugin';let inducted=!!r.legend,m=r.memory_summary||{};
    d.innerHTML='<div class="pluginTop"><span class="pluginName">'+(r.name||r.id)+'</span><span class="pill '+(inducted?'on':'')+'">'+(inducted?'LEGEND':'LEVEL 100')+'</span></div>'+
      '<div class="mini">'+String(r.kind||'beast').toUpperCase()+' · '+(r.stage||'')+' · GEN '+(r.generation||0)+' · '+(r.achievement_count||0)+' achievements</div>'+
      '<div class="mini">'+(m.memory_count||0)+' memories · '+(m.expedition_count||0)+' expeditions · '+(m.rare_witness_count||0)+' rare witnesses · '+((r.children||[]).length)+' descendants</div>';
    let b=document.createElement('button');b.textContent=inducted?'REMOVE HALL MARK':'INDUCT INTO HALL';b.onclick=()=>setLegend(r.id,r.name||r.id,!inducted,b);d.append(b);box.append(d)});
  let g=h.graph||{},nodes={};(g.nodes||[]).forEach(n=>nodes[n.id]=n);let children={};(g.edges||[]).forEach(e=>(children[e.parent_id]=children[e.parent_id]||[]).push(e.child_id));
  let childSet=new Set((g.edges||[]).map(e=>e.child_id)),roots=(g.nodes||[]).filter(n=>!childSet.has(n.id));
  function line(id,depth,seen){if(seen.has(id))return '  '.repeat(depth)+'↳ [cycle blocked] '+id+'\n';seen=new Set(seen);seen.add(id);let n=nodes[id]||{id:id,name:id},mut=n.mutation?(' · ✦ '+(n.mutation.id||'mutation')):'';let out='  '.repeat(depth)+(depth?'↳ ':'')+(n.name||n.id)+' · '+String(n.kind||'beast').toUpperCase()+' · LV'+(n.level||1)+' '+(n.stage||'')+(n.legend?' · LEGEND':'')+mut+'\n';(children[id]||[]).forEach(c=>out+=line(c,depth+1,seen));return out}
  $('ancestryTree').textContent=roots.length?roots.map(r=>line(r.id,0,new Set())).join('\n'):'No ancestry links yet.';
}catch(e){$('hallList').innerHTML='<div class="status">Hall unavailable: '+e+'</div>'}}
async function setLegend(id,name,enabled,btn){let msg=enabled?('Induct '+name+' into the Hall of Legends?\n\nThis records a permanent milestone but does not retire or deactivate the creature.'):('Remove the Hall mark from '+name+'?\n\nIts level, memories and history remain untouched.');if(!confirm(msg))return;btn.disabled=true;try{let x=await jfetch('/api/roster-legend',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:id,enabled:enabled})});let row=x.action_row||{};$('rosterStatus').textContent=row.status==='success'?(enabled?'Legend inducted.':'Hall mark removed.'):'Hall change failed.';await loadRoster();await loadHall()}catch(e){$('rosterStatus').textContent='Hall change failed: '+e}finally{btn.disabled=false}}
async function previewSynthesis(){let a=$('synthParentA').value,b=$('synthParentB').value,name=$('synthName').value.trim()||'Monster';if(!a||!b){$('synthStatus').textContent='Choose two eligible Beasts.';return}try{
  let x=await jfetch('/api/roster-synthesis-plan',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({parent_a:a,parent_b:b,name:name})});
  let blockers=x.blockers||[];if(blockers.length){$('synthStatus').textContent='BLOCKED · '+blockers.join(' · ');return}
  let pa=x.parent_a||{},pb=x.parent_b||{},chance=Number(x.mutation_chance_basis_points||0)/100;
  $('synthStatus').textContent=`READY · ${pa.name} LV${pa.level} + ${pb.name} LV${pb.level} → ${name}, Monster LV1 · parents preserved · mutation chance ${chance.toFixed(2)}% · first successful synthesis unlocks Monstergotchi core`;
}catch(e){$('synthStatus').textContent='Synthesis preview failed: '+e}}
async function createSynthesis(){let a=$('synthParentA').value,b=$('synthParentB').value,name=$('synthName').value.trim()||'Monster';if(!a||!b){$('synthStatus').textContent='Choose two eligible Beasts.';return}
  let plan;try{plan=await jfetch('/api/roster-synthesis-plan',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({parent_a:a,parent_b:b,name:name})})}catch(e){$('synthStatus').textContent='Synthesis preview failed: '+e;return}
  if((plan.blockers||[]).length){$('synthStatus').textContent='BLOCKED · '+plan.blockers.join(' · ');return}
  let pa=plan.parent_a||{},pb=plan.parent_b||{};if(!confirm(`Create ${name} from ${pa.name} and ${pb.name}?\n\nBoth parents remain unchanged. The Monster starts at level 1. This v1 parent pair cannot be rerolled repeatedly.`))return;
  $('synthCreate').disabled=true;try{let x=await jfetch('/api/roster-synthesize',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({parent_a:a,parent_b:b,name:name})});let row=x.action_row||{},res=row.result||{},m=res.monster||{};if(row.status!=='success')throw Error(res.error||'synthesis failed');
    let h=((m.identity||{}).heritage||{}).generated||{},mut=h.mutation;$('synthStatus').textContent=`CREATED · ${m.name||name} · GEN ${m.generation||1} · ${m.stage||'Origin'} · ${mut?'MUTATION '+mut.id+' ('+mut.rarity+')':'no mutation'} · ancestry recorded`;await loadRoster();await loadGlobalProfile()
  }catch(e){$('synthStatus').textContent='Synthesis failed: '+e}finally{$('synthCreate').disabled=false}}
async function rememberRosterPresentation(id,name,btn){if(!confirm('Remember the current Studio draft as '+name+'\'s preferred setup?\n\nThis stores the preference but does not apply or change the physical UI.'))return;btn.disabled=true;try{
  let x=await jfetch('/api/roster-presentation',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:id,draft:draft,experience_id:window._loadedExperienceId||''})});
  $('rosterStatus').textContent=(x.action_row||{}).status==='success'?'Preferred setup saved for '+name+'.':'Could not save preferred setup.';await loadRoster()
}catch(e){$('rosterStatus').textContent='Save failed: '+e}finally{btn.disabled=false}}
async function clearRosterPresentation(id,name,btn){if(!confirm('Forget '+name+'\'s preferred setup?\n\nProgression/history are not affected.'))return;btn.disabled=true;try{
  let x=await jfetch('/api/roster-presentation-clear',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:id})});
  $('rosterStatus').textContent=(x.action_row||{}).status==='success'?'Preferred setup forgotten.':'Could not clear preferred setup.';await loadRoster()
}catch(e){$('rosterStatus').textContent='Clear failed: '+e}finally{btn.disabled=false}}
async function switchRoster(id,name,btn,loadPreferred){if(!confirm('Wake '+name+' and make it the active progression creature?'+(loadPreferred?'\n\nIts preferred setup will be loaded into the Studio draft for preview. Nothing changes on the physical UI until APPLY TO BEAST.':'\n\nYour current UI Experience will remain unchanged.')))return;btn.disabled=true;try{
  let x=await jfetch('/api/roster-switch',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:id})});
  let row=x.action_row||{};if(row.status!=='success')throw Error('switch failed');
  if(loadPreferred){let p=await jfetch('/api/roster-preferred?id='+encodeURIComponent(id));if(p.has_preferred_presentation&&p.presentation){push();draft=Object.assign(clone(draft),clone(p.presentation));window._loadedExperienceId=p.presentation.experience_id||'';rebuild();$('status').textContent='Loaded '+name+'\'s preferred setup into the Studio draft. Review it, then APPLY TO BEAST if desired.'}}
  $('rosterStatus').textContent='Active creature switched. Progression now follows '+name+'.';await loadRoster();await loadGlobalProfile()
}catch(e){$('rosterStatus').textContent='Switch failed: '+e}finally{btn.disabled=false}}

async function loadGlobalProfile(){try{let x=await jfetch('/api/global-profile');let p=x.policy||{};globalLocalRoster=x.local_roster||[];fillGlobalPolicy(p);$('globalPreview').textContent=JSON.stringify(x.snapshot||{},null,2);$('globalStatus').textContent='Network upload: disabled in this milestone · pending local revisions: '+((x.pending||[]).length)}catch(e){$('globalStatus').textContent='Global profile unavailable: '+e}}
async function saveGlobalPolicy(){let p=globalPolicyFromForm();if(p.enabled&&!confirm('Enable this public-profile privacy policy?\n\nNo network connector is configured yet, so nothing will be uploaded now. When a Global connector is added later, only the fields shown in the exact public snapshot will be eligible for upload.'))return;try{let x=await jfetch('/api/global-policy',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({policy:p})});let row=x.action_row||{},res=row.result||{};$('globalPreview').textContent=JSON.stringify(res.snapshot||{},null,2);$('globalStatus').textContent=row.status==='success'?'Privacy policy saved locally. No network upload was performed.':'Could not save Global policy.';await loadGlobalProfile()}catch(e){$('globalStatus').textContent='Global policy save failed: '+e}}
async function loadPacks(){try{
  let [x,prefs,hist,experiencePlans]=await Promise.all([jfetch('/api/platform'),jfetch('/api/update-policies'),jfetch('/api/pack-history'),jfetch('/api/experiences')]);
  let packs=x.packs||{},updates=x.updates||{};window._localPackRows=packs.items||[];renderBuiltinExperiences(experiencePlans);await loadDepot(window._localPackRows);
  let ex=$('experienceList');ex.innerHTML='';let missions=x.missions||{};(missions.items||[]).filter(r=>r.experience).forEach(r=>{let d=document.createElement('div');d.className='plugin';let ready=!!r.requirements_met;d.innerHTML=`<div class="pluginTop"><span class="pluginName">${r.label||r.id}</span><span class="pill ${ready?'on':''}">${ready?'READY':'NEEDS INPUTS'}</span></div><div class="mini">${r.description||''}</div><div class="mini">Theme ${r.theme||'—'} · Face ${r.face_profile||'—'} · Motion ${r.animation_profile||'—'} · Board ${r.board||r.layout||'—'} · Deck ${r.deck||'—'}</div><div class="status">${r.source_pack?'Pack '+r.source_pack+' · ':''}loads into the Studio draft; nothing changes until APPLY TO BEAST</div>`;let eb=document.createElement('button');eb.textContent='LOAD EXPERIENCE INTO PREVIEW';eb.disabled=!ready;eb.onclick=()=>previewExperience(r,eb);d.append(eb);ex.append(d)});if(!(missions.items||[]).some(r=>r.experience))ex.innerHTML='<div class="status">No Experience profiles available yet.</div>';
  let sum=$('packSummary');sum.innerHTML='';
  let c=document.createElement('div');c.className='widget';
  c.innerHTML=`<div class="widgetHead"><b>DEPOT FOUNDATION</b><span class="pill">${packs.count||0} PACKS</span></div><div class="mini">${packs.enabled_count||0} enabled · ${packs.staged_count||0} staged · ${packs.compatible_count||0} requirements-ready · ${packs.error_count||0} manifest errors</div><div class="mini">Registry install: ${packs.executor_enabled?'ENABLED':'LOCKED'} · activation ${packs.activation_enabled?'ENABLED':'LOCKED'} · ${packs.executor_reason||''}</div>`;
  sum.append(c);

  let box=$('packList');box.innerHTML='<h3>LOCAL PACK CATALOG</h3>';
  (packs.items||[]).forEach(r=>{let d=document.createElement('div');d.className='plugin';let ready=!!r.requirements_met;d.innerHTML=`<div class="pluginTop"><span class="pluginName">${r.label||r.id}</span><span class="pill ${ready?'on':''}">${String(r.lifecycle||'unknown').toUpperCase()}</span></div><div class="mini">${r.pack_type||'pack'} · v${r.version||'?'} · resource ${r.resource_class||'--'} · thermal ${r.thermal_class||'--'}</div><div class="mini">${r.description||''}</div>`;if((r.blockers||[]).length){let b=document.createElement('div');b.className='status';b.style.color='var(--warn)';b.textContent=(r.blockers||[]).join(' · ');d.append(b)}if(r.origin==='staged'&&String(r.lifecycle)==='verified'){let btn=document.createElement('button');btn.textContent='INSTALL TO MANAGED REGISTRY';btn.disabled=!ready;btn.onclick=()=>installPack(r,btn);d.append(btn)}if(r.origin!=='staged'&&['theme','face','animation','audio','layout','board','data','map'].includes(String(r.pack_type||''))){let ab=document.createElement('button');ab.textContent=r.enabled?'DISABLE CONTENT PACK':'ENABLE CONTENT PACK';ab.onclick=()=>togglePackActivation(r,ab);d.append(ab)}box.append(d)});
  if(!(packs.items||[]).length)box.innerHTML+='<div class="status">No optional Beast Packs installed or staged yet. The base platform remains self-contained.</div>';

  let tx=$('packTransactions');tx.innerHTML='<h3>INSTALL / ROLLBACK HISTORY</h3>';let txrows=(hist.items||[]);if(!txrows.length)tx.innerHTML+='<div class="status">No pack transactions yet.</div>';txrows.slice(0,8).forEach(r=>{let d=document.createElement('div');d.className='plugin';d.innerHTML=`<div class="pluginTop"><span class="pluginName">${r.pack_id||'pack'} · ${r.version||'?'}</span><span class="pill ${r.status==='installed'?'on':''}">${String(r.status||'unknown').toUpperCase()}</span></div><div class="mini">${r.id||''} · activation ${r.activation_performed?'yes':'no'}</div>`;if(r.status==='installed'&&(!r.had_previous||r.rollback_payload_retained)){let btn=document.createElement('button');btn.textContent='ROLL BACK';btn.onclick=()=>rollbackPack(r,btn);d.append(btn)}tx.append(d)});

  let up=$('updateList');up.innerHTML='<h3>UPDATE POLICIES</h3><div class="mini">Trusted release metadata and SHA-256 staging are live. Beast Packs can use transactional inert-registry updates with rollback; core, Theme Manager and Pwnagotchi remain stage-only until dedicated rollback adapters pass validation.</div>';
  let saved=(prefs||{}).policies||{};
  (updates.components||[]).forEach(r=>{let d=document.createElement('div');d.className='plugin';let top=document.createElement('div');top.className='pluginTop';let n=document.createElement('span');n.className='pluginName';n.textContent=`${r.label||r.id} · ${r.installed_version||'unknown'}`;let st=document.createElement('span');st.className='pill '+(r.compatibility==='compatible'?'on':'');st.textContent=String(r.last_result||'not_checked').toUpperCase();top.append(n,st);d.append(top);let meta=document.createElement('div');meta.className='mini';meta.textContent=`${r.kind||'component'} · ${r.source_type||'unknown'}${r.source?' · '+r.source:''} · ${r.source_trusted?'trusted':'untrusted'}`;d.append(meta);let ver=document.createElement('div');ver.className='mini';ver.textContent=r.update_available===true?`Update available: ${r.available_version||'?'}${r.verification_available?' · SHA-256 path found':' · verification asset missing'}`:r.available_version?`Latest: ${r.available_version}`:'No release metadata cached yet';d.append(ver);let sel=document.createElement('select');['manual','notify','auto_stage','auto_install'].forEach(v=>option(sel,v,v.replace('_',' ').toUpperCase()));sel.value=saved[r.id]||r.policy||'notify';sel.onchange=()=>setUpdatePolicy(r.id,sel.value,sel);d.append(sel);if(r.auto_stage_eligible){let sb=document.createElement('button');sb.textContent='STAGE VERIFIED UPDATE';sb.onclick=()=>stageUpdate(r,sb);d.append(sb);if(r.auto_install_eligible&&String(r.id||'').startsWith('pack:')){let ab=document.createElement('button');ab.textContent='APPLY VERIFIED PACK UPDATE';ab.onclick=()=>applyPackUpdate(r,ab);d.append(ab)}}if((r.blockers||[]).length){let b=document.createElement('div');b.className='status';b.style.color='var(--warn)';b.textContent=(r.blockers||[]).join(' · ');d.append(b)}up.append(d)});
  let auto=x.update_automation||{};let gate=document.createElement('div');gate.className='status';gate.textContent=`Metadata: ${updates.check_state||'--'} · ${updates.update_available_count||0} update(s) · trusted ${updates.trusted_component_count||0}/${updates.component_count||0} · dock trigger ${updates.auto_trigger_ready?'ready':'not ready'} · automation ${auto.status||'--'} · pack auto-install ${auto.auto_install_executor_enabled?'enabled':'locked'}${auto.auto_install_scope?' ('+auto.auto_install_scope+')':''}`;up.append(gate);
}catch(e){$('packSummary').innerHTML='<div class="status">Pack/update catalog unavailable: '+e+'</div>'}}
$('refreshPacks').onclick=loadPacks;

async function createBackup(btn){if(!confirm('Create a Beast recovery backup now? It may contain private configuration.'))return;btn.disabled=true;$('status').textContent='Creating recovery backup…';try{let plan=await jfetch('/api/backup-plan',{method:'POST',headers:{'content-type':'application/json'},body:'{}'});if(!(plan.plan||{}).allowed)throw Error(((plan.plan||{}).blockers||['blocked']).join('; '));let r=await jfetch('/api/backup-create',{method:'POST',headers:{'content-type':'application/json'},body:'{}'});$('status').textContent=(r.action_row||{}).status==='success'?'Backup created.':'Backup failed.';await loadOps()}catch(e){$('status').textContent='Backup failed: '+e}finally{btn.disabled=false}}
async function createSupportBundle(btn){if(!confirm('Create a sanitized Beast support bundle? Nearby network identities, GPS coordinates, credentials, raw config and raw logs are excluded.'))return;btn.disabled=true;$('status').textContent='Creating sanitized support bundle…';try{let plan=await jfetch('/api/support-plan',{method:'POST',headers:{'content-type':'application/json'},body:'{}'});if(!(plan.plan||{}).allowed)throw Error(((plan.plan||{}).blockers||['blocked']).join('; '));let r=await jfetch('/api/support-create',{method:'POST',headers:{'content-type':'application/json'},body:'{}'});let row=r.action_row||{};$('status').textContent=row.status==='success'?'Support bundle created.':'Support bundle failed.';await loadOps()}catch(e){$('status').textContent='Support bundle failed: '+e}finally{btn.disabled=false}}
async function verifyBackup(name,btn){btn.disabled=true;$('status').textContent='Verifying '+name+'...';try{let x=await jfetch('/api/backup-inspect?name='+encodeURIComponent(name));let msg=x.ok?`VERIFIED / ${String(x.sha256||'').slice(0,12)}... / DB ${x.db_valid===true?'OK':x.db_valid===false?'FAIL':'N/A'}`:`NOT READY / ${(x.blockers||[x.error||'verification failed']).join('; ')}`;$('status').textContent=msg;if(x.ok)alert('Backup verified for restore staging.\n\nSHA-256: '+x.sha256+'\nDatabase: '+(x.db_valid===true?'OK':x.db_valid===false?'FAILED':'not present')+'\n\nNo restore was performed.')}catch(e){$('status').textContent='Backup verification failed: '+e}finally{btn.disabled=false}}
async function loadOps(){try{
let x=await jfetch('/api/platform');
let sum=$('opsSummary');sum.innerHTML='';
let ov=x.overview||{};
let c=document.createElement('div');c.className='widget';
c.innerHTML=`<div class="widgetHead"><b>PLATFORM</b><span class="pill ${ov.state==='healthy'?'on':''}">${String(ov.state||'unknown').toUpperCase()}</span></div><div class="mini">${(ov.attention||[]).length} attention item(s) · ${(x.topology?.failures||[]).length} dependency failure(s) · ${(x.library?.total||0)} offline documents</div>`;
sum.append(c);

let res=$('opsResources');res.innerHTML='<h3>PERFORMANCE / THERMAL</h3><div class="mini">Measured attribution. Beast tries to remove duplicate/background work before the governor sheds visible features.</div>';
let th=x.thermal||{},pf=x.performance||{},gv=x.governor||{};
let therm=document.createElement('div');therm.className='widget';
let throttle=gv.throttle_current?'THROTTLING':gv.throttle_history_seen?'THROTTLE SEEN':'NO THROTTLE';
therm.innerHTML=`<div class="widgetHead"><b>PI LOAD</b><span class="pill ${gv.throttle_current?'':'on'}">${throttle}</span></div>
<div class="mini">CPU ${fmt(th.cpu_total_pct,'%')} · TEMP ${fmt(th.cpu_temp_c,'°C')} · RAM ${fmt(th.memory_used_pct,'%')} · LOAD ${fmt(th.load_1m,'')}</div>
<div class="mini">ARM ${fmt(th.arm_clock_mhz,' MHz')} · CORE ${fmt(th.core_clock_mhz,' MHz')} · GPU MEM ${fmt(th.gpu_mem_mb,' MB')}</div>
<div class="mini">Governor ${String(gv.mode||'--')} · budget ${fmt(gv.budget_pct,'%')} · UI cap ${fmt(gv.fps_cap,' fps')} · reason ${String(gv.reason||'nominal')}</div>`;
res.append(therm);
let totals=document.createElement('div');totals.className='widget';
totals.innerHTML=`<div class="widgetHead"><b>ATTRIBUTED COST</b><span class="pill">${pf.process_count||0} GROUPS</span></div>
<div class="mini">Beast ${fmt(pf.beast_cpu_pct,'% CPU')} · platform services ${fmt(pf.platform_services_cpu_pct,'% CPU')} · tracked RSS ${fmt(pf.tracked_rss_mb,' MB')}</div>
<div class="mini">UI render ${fmt(pf.ui?.avg_render_ms,' ms')} · FB write ${fmt(pf.ui?.avg_fb_write_ms,' ms')} · write ratio ${fmt(pf.framebuffer?.write_ratio_pct,'%')}</div>`;
res.append(totals);
(pf.processes||[]).forEach(r=>{let d=document.createElement('div');d.className='plugin';d.innerHTML=`<div class="pluginTop"><span class="pluginName">${r.label||r.id}</span><span class="pill">${fmt(r.cpu_pct,'% CPU')}</span></div><div class="mini">${fmt(r.rss_mb,' MB RSS')} · PID ${(r.pids||[]).join(', ')||'--'}</div>`;res.append(d)});

let ps=$('opsPresentation');ps.innerHTML='<h3>PRESENTATION OWNERSHIP</h3><div class="mini">Read-only in this milestone. Physical handoff stays disabled until Native / Theme Manager / Beast owner adapters pass validation.</div>';
let pr=x.presentation||{};let pc=document.createElement('div');pc.className='widget';
pc.innerHTML=`<div class="widgetHead"><b>DISPLAY / TOUCH OWNER</b><span class="pill ${pr.conflict_count?'':'on'}">${pr.conflict_count?pr.conflict_count+' CONFLICT':'CLEAR'}</span></div>
<div class="mini">Desired: ${pr.desired_owner||'--'} · Active: ${pr.active_owner||'unknown'} · State: ${pr.status||'--'}</div>
<div class="mini">Available: ${(pr.available_owners||[]).join(' · ')||'--'}</div>
<div class="mini">Theme Manager: ${pr.theme_manager_installed?'installed':'not detected'} / ${pr.theme_manager_enabled?'enabled':'disabled'} · managed handoff ${pr.theme_manager_managed_handoff_supported?'yes':'not yet'}</div>
<div class="mini">Executor: ${pr.executor_enabled?'ENABLED':'LOCKED'}${pr.executor_reason?' · '+pr.executor_reason:''}</div>`;
ps.append(pc);
(pr.conflicts||[]).forEach(msg=>{let d=document.createElement('div');d.className='status';d.style.color='var(--warn)';d.textContent='⚠ '+msg;ps.append(d)});

let inc=$('opsIncidents');inc.innerHTML='<h3>BLACK BOX / INCIDENTS</h3>';
let incidents=(x.incidents?.items||[]).slice(0,6);
if(!incidents.length)inc.innerHTML+='<div class="status">No recent incidents.</div>';
incidents.forEach(r=>{let d=document.createElement('div');d.className='widget';let sev=String(r.severity||'info').toLowerCase();d.innerHTML=`<div class="widgetHead"><span class="pluginName">${r.title||r.kind||r.type||'Incident'}</span><span class="pill ${r.status==='resolved'?'on':''}">${String(r.status||sev).toUpperCase()}</span></div><div class="mini">${r.detail||r.summary||''}</div>`;inc.append(d)});

let svc=$('opsServices');svc.innerHTML='<h3>SERVICES</h3>';
(x.services||[]).forEach(r=>{let d=document.createElement('div');d.className='plugin';let top=document.createElement('div');top.className='pluginTop';let name=document.createElement('span');name.className='pluginName';name.textContent=r.unit;let st=document.createElement('span');st.className='pill '+(r.active==='active'?'on':'');st.textContent=String(r.active||'unknown').toUpperCase();top.append(name,st);d.append(top);let meta=document.createElement('div');meta.className='mini';meta.textContent=`${r.sub||'--'} · pid ${r.pid||0}`;d.append(meta);if(['pwnagotchi.service','bettercap.service','gpsd.service','beast-ui.service'].includes(r.unit)){let b=document.createElement('button');b.textContent='RESTART';b.onclick=()=>restartService(r.unit,b);d.append(b)}svc.append(d)});

let bk=$('opsBackups');bk.innerHTML='<h3>BACKUP / RECOVERY</h3>';let b=document.createElement('button');b.textContent='CREATE RECOVERY BACKUP';b.onclick=()=>createBackup(b);bk.append(b);(x.backups?.items||[]).slice(0,4).forEach(r=>{let d=document.createElement('div');d.className='plugin';d.style.marginTop='6px';let top=document.createElement('div');top.className='pluginTop';let n=document.createElement('span');n.className='pluginName';n.textContent=r.name||'backup';let st=document.createElement('span');st.className='pill '+(r.valid?'on':'');st.textContent=r.valid?'STRUCTURE OK':'CHECK';top.append(n,st);d.append(top);let meta=document.createElement('div');meta.className='mini';meta.textContent=String(r.size_human||r.size_bytes||'');d.append(meta);let vb=document.createElement('button');vb.textContent='VERIFY FOR RESTORE';vb.onclick=()=>verifyBackup(r.name,vb);d.append(vb);bk.append(d)});

let sp=$('opsSupport');sp.innerHTML='<h3>SUPPORT / DIAGNOSTICS</h3><div class="mini">Creates a privacy-sanitized troubleshooting bundle. Network identities, GPS coordinates, credentials, raw config and raw logs are excluded.</div>';let sb=document.createElement('button');sb.textContent='CREATE SANITIZED SUPPORT BUNDLE';sb.style.marginTop='7px';sb.onclick=()=>createSupportBundle(sb);sp.append(sb);

let jobs=$('opsTasks');jobs.innerHTML='<h3>TASK CENTER</h3>';((x.jobs||{}).items||[]).slice(0,8).forEach(r=>{let d=document.createElement('div');d.className='widget';let p=typeof r.progress==='number'?Math.round(r.progress*100)+'%':String(r.status||'').toUpperCase();d.innerHTML=`<div class="widgetHead"><span class="pluginName">${r.label||r.kind}</span><span class="pill ${r.status==='complete'?'on':''}">${p}</span></div><div class="mini">${r.detail||''}</div>`;jobs.append(d)});if(!((x.jobs||{}).items||[]).length)jobs.innerHTML+='<div class="status">No recorded background jobs yet.</div>'
}catch(e){$('opsSummary').innerHTML='<div class="status">Operations unavailable: '+e+'</div>'}}
function fmt(v,suffix=''){if(v===null||v===undefined||v==='')return '--';let n=Number(v);return Number.isFinite(n)?(Math.abs(n)>=100?Math.round(n):Math.round(n*10)/10)+suffix:String(v)+suffix}

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
$('refreshPlugins').onclick=loadPlugins;$('theme').onchange=()=>mutate(()=>draft.theme=$('theme').value);$('faceProfile').onchange=()=>mutate(()=>draft.face_profile=$('faceProfile').value);$('animationProfile').onchange=()=>mutate(()=>draft.animation_profile=$('animationProfile').value);$('page').onchange=()=>mutate(()=>draft.page=$('page').value);$('undo').onclick=()=>{if(!undo.length)return;redo.push(clone(draft));draft=undo.pop();rebuild()};$('redo').onclick=()=>{if(!redo.length)return;undo.push(clone(draft));draft=redo.pop();rebuild()};$('reset').onclick=()=>{push();draft=clone(base);rebuild()};$('apply').onclick=async()=>{try{await jfetch('/api/apply',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(draft)});base=clone(draft);undo=[];redo=[];$('status').textContent='Applied atomically. Physical Beast UI reloads the draft automatically.'}catch(e){$('status').textContent='Apply failed: '+e}};
(async()=>{try{schema=await jfetch('/api/schema');base=await jfetch('/api/preferences');draft=clone(base);rebuild();await loadVariants();await loadRoster();await loadHall();await loadGlobalProfile();$('conn').textContent='LIVE'}catch(e){$('conn').textContent='ERROR';$('status').textContent=e}})();
</script></body></html>
'''


class StudioState:
    def __init__(self,root: str,prefs: str,token_file: str) -> None:
        self.root=Path(root);self.prefs=Path(prefs);self.token_file=Path(token_file);self.api=BeastAPI();self.actions=BeastActionClient();self.token=self._token();self.variants_dir=self.prefs.parent/'variants'
        self.library_files=LibraryFileManager()
        self.update_policies=UpdatePolicyStore(self.prefs.parent/'update_policies.json')
        self.depot=DepotCatalogStore()

    def _token(self)->str:
        self.token_file.parent.mkdir(parents=True,exist_ok=True)
        if self.token_file.exists():return self.token_file.read_text().strip()
        tok=secrets.token_urlsafe(18);self.token_file.write_text(tok+'\n');os.chmod(self.token_file,0o600);return tok

    def preferences(self)->dict:
        try:obj=json.loads(self.prefs.read_text())
        except Exception:obj={}
        renderers=dict(obj.get('renderers') or {})
        for pid,vals in BeastUI.RENDERER_CHOICES.items():renderers.setdefault(pid,vals[0])
        pack_boards=discover_enabled_pack_boards()
        app_ids=[a.id for a in AppRegistry().all()]+[f"board:{b['id']}" for b in pack_boards]
        decks=validate_context_decks(obj.get('context_decks'),app_ids=app_ids)
        active=str(obj.get('active_context_deck') or '')
        if active not in {d['id'] for d in decks}:active=''
        theme_ids=list(BeastUI.THEMES)+[x for x in discover_enabled_pack_themes() if x not in BeastUI.THEMES]
        face_ids={'builtin',*discover_enabled_face_profiles().keys()};face_profile=str(obj.get('face_profile') or 'builtin');face_profile=face_profile if face_profile in face_ids else 'builtin'
        anim_ids={'none',*FaceEngine().animation_profiles.keys()};animation_profile=str(obj.get('animation_profile') or 'none');animation_profile=animation_profile if animation_profile in anim_ids else 'none'
        return {'theme':str(obj.get('theme') or 'classic'),'face_profile':face_profile,'animation_profile':animation_profile,'page':'home','preview_output':'480x320','renderers':renderers,'theme_options':dict(obj.get('theme_options') or {}),'dashboard_widgets':validate_dashboard_widgets(obj.get('dashboard_widgets')),'custom_boards':validate_custom_boards(obj.get('custom_boards')),'preview_board_id':'','context_decks':decks,'active_context_deck':active,'palette_overrides':validate_palette_overrides(obj.get('palette_overrides'),theme_ids=theme_ids),'correlation_keys':validate_correlation_keys(obj.get('correlation_keys'))}

    def validate(self,obj: dict)->dict:
        if not isinstance(obj,dict):raise ValueError('draft must be an object')
        theme=str(obj.get('theme') or 'classic')
        page=str(obj.get('page') or 'home')
        preview_output=str(obj.get('preview_output') or '480x320')
        if preview_output not in {'480x320','640x480','800x480'}:preview_output='480x320'
        probe=BeastUI(root=str(self.root),output=str(Path(tempfile.gettempdir())/'beast-studio-probe.png'),theme_id=theme)
        if theme not in probe.THEMES:raise ValueError('unknown theme')
        if page not in probe.pages.IDS:raise ValueError('unknown page')
        face_profile=str(obj.get('face_profile') or 'builtin');face_ids={x['id'] for x in probe.face.profile_options()};face_profile=face_profile if face_profile in face_ids else 'builtin'
        animation_profile=str(obj.get('animation_profile') or 'none');anim_ids={x['id'] for x in probe.face.animation_profile_options()};animation_profile=animation_profile if animation_profile in anim_ids else 'none'
        renderers={}
        incoming=obj.get('renderers') or {}
        for pid,vals in probe.RENDERER_CHOICES.items():
            val=str(incoming.get(pid) or vals[0]);renderers[pid]=val if val in vals else vals[0]
        options={};raw=obj.get('theme_options') or {}
        if isinstance(raw,dict):
            for tid,tvals in raw.items():
                if not probe._theme_path(tid) or not isinstance(tvals,dict):continue
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
        pack_boards=discover_enabled_pack_boards(catalog=live_catalog)
        app_ids=[a.id for a in AppRegistry().all()]+[f"board:{b['id']}" for b in boards]+[f"board:{b['id']}" for b in pack_boards]
        decks=validate_context_decks(obj.get('context_decks'),app_ids=app_ids)
        active=str(obj.get('active_context_deck') or '')
        if active not in {d['id'] for d in decks}:active=''
        palette=validate_palette_overrides(obj.get('palette_overrides'),theme_ids=probe.THEMES)
        corr=validate_correlation_keys(obj.get('correlation_keys'),catalog=live_catalog)
        return {'theme':theme,'face_profile':face_profile,'animation_profile':animation_profile,'page':page,'preview_output':preview_output,'renderers':renderers,'theme_options':options,'dashboard_widgets':widgets,'custom_boards':boards,'preview_board_id':preview_board_id,'context_decks':decks,'active_context_deck':active,'palette_overrides':palette,'correlation_keys':corr}

    def schema(self)->dict:
        probe=BeastUI(root=str(self.root),output=str(Path(tempfile.gettempdir())/'beast-studio-schema.png'),theme_id='classic')
        themes=[];opts={}
        for tid in probe.THEMES:
            fp=probe._theme_path(tid)
            if not fp or not fp.exists():continue
            th=load_theme(fp);themes.append({'id':tid,'label':th.label})
            defaults=probe.options_for_theme(tid);opts[tid]=[{'key':k,'label':lab,'values':vals,'default':defaults.get(k)} for k,lab,vals in probe._theme_option_rows(tid)]
        telemetry=scalar_catalog(self.api.telemetry())
        face_profiles=probe.face.profile_options();animation_profiles=probe.face.animation_profile_options()
        pack_boards=discover_enabled_pack_boards(catalog=telemetry);pack_layouts=discover_enabled_pack_layouts(catalog=telemetry)
        apps=[{'id':a.id,'title':a.title,'category':a.category,'description':a.description} for a in AppRegistry().all()]
        apps.extend({'id':f"board:{b['id']}",'title':b.get('label') or b['id'],'category':'Boards','description':f"Read-only board from Pack {b.get('source_pack') or ''}"} for b in pack_boards)
        theme_colors={}
        for row in themes:
            th=load_theme(probe._theme_path(row["id"]))
            theme_colors[row['id']]={slot:'#%02x%02x%02x'%th.c(slot) for slot in PALETTE_SLOTS if slot in th.colors}
        return {'version':'0.18.0','themes':themes,'preview_outputs':[{'id':'480x320','label':'REFERENCE · 480 × 320','width':480,'height':320,'reference':True},{'id':'640x480','label':'COMPATIBILITY · 640 × 480','width':640,'height':480,'reference':False},{'id':'800x480','label':'COMPATIBILITY · 800 × 480','width':800,'height':480,'reference':False}],'pages':[{'id':x,'title':probe.pages.TITLES[x]} for x in probe.pages.IDS],'renderers':probe.RENDERER_CHOICES,'theme_options':opts,'dashboard_keys':telemetry,'widget_styles':list(WIDGET_STYLES),'palette_slots':list(PALETTE_SLOTS),'theme_colors':theme_colors,'apps':apps,'default_context_decks':[dict(x) for x in DEFAULT_CONTEXT_DECKS],'max_dashboard_widgets':MAX_DASHBOARD_WIDGETS,'pack_boards':pack_boards,'pack_layouts':pack_layouts,'face_profiles':face_profiles,'animation_profiles':animation_profiles,'experience_families':list_experience_families(),'experience_dna':[row.as_dict() for row in BUILTIN_EXPERIENCE_DNA.values()],'legacy_reference_identities':sorted(LEGACY_REFERENCE_IDENTITIES),'experience_renderers':experience_renderer_catalog(),'experience_page_coverage':experience_renderer_summary()}

    def preview(self,draft: dict)->bytes:
        cfg=self.validate(draft);live=self.api.live(24);state=live.get('state') if isinstance(live,dict) else {}
        preview_widgets=cfg['dashboard_widgets']
        if cfg.get('preview_board_id'):
            preview_widgets=next((b.get('widgets') or [] for b in cfg.get('custom_boards') or [] if b.get('id')==cfg['preview_board_id']),preview_widgets)
        hkeys=tuple(dict.fromkeys(['system.cpu.total','system.temp.cpu_c','system.memory.used_pct','wifi.ap_count','wifi.client_count',*dashboard_history_keys(preview_widgets)]))
        batch=self.api.history_batch(hkeys,64,channel_limit=90,expedition_points=256)
        with tempfile.TemporaryDirectory(prefix='beast-studio-') as td:
            dims={'480x320':(480,320),'640x480':(640,480),'800x480':(800,480)};physical=dims.get(cfg.get('preview_output'),(480,320))
            ui=BeastUI(root=str(self.root),output=str(Path(td)/'preview.png'),theme_id=cfg['theme'],physical_size=physical,display_mode='fit');ui.face_profile_pref=cfg['face_profile'];ui.animation_profile_pref=cfg['animation_profile'];ui.face.set_profile(cfg['face_profile']);ui.face.set_animation_profile(cfg['animation_profile']);ui.state=state if isinstance(state,dict) else {};ui.renderers=cfg['renderers'];ui.theme_options=cfg['theme_options'];ui.dashboard_widgets=cfg['dashboard_widgets'];ui.custom_boards=cfg['custom_boards'];ui.active_board_id=cfg.get('preview_board_id') or '';ui.context_decks=cfg['context_decks'];ui.active_context_deck=cfg['active_context_deck'];ui.palette_overrides=cfg['palette_overrides'];ui.correlation_keys=cfg['correlation_keys'];ui._apply_palette_overrides();ui.events=live.get('events') or [] if isinstance(live,dict) else []
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
        cfg=self.validate(draft);payload={'theme':cfg['theme'],'face_profile':cfg['face_profile'],'animation_profile':cfg['animation_profile'],'renderers':cfg['renderers'],'theme_options':cfg['theme_options'],'dashboard_widgets':cfg['dashboard_widgets'],'custom_boards':cfg['custom_boards'],'context_decks':cfg['context_decks'],'active_context_deck':cfg['active_context_deck'],'palette_overrides':cfg['palette_overrides'],'correlation_keys':cfg['correlation_keys']}
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

    def experience_preview(self,obj: dict)->bytes:
        experience_id=str(obj.get("id") or "").strip().lower()
        page_id=str(obj.get("page") or "home").strip().lower()
        if not experience_id:
            raise ExperienceDraftError("Experience id required")
        live=self.api.live(24)
        state=live.get("state") if isinstance(live,dict) else {}
        if not isinstance(state,dict):
            state={}
        try:
            im=render_experience_page(experience_id,page_id,state)
        except KeyError as exc:
            raise ExperienceDraftError(str(exc))
        bio=io.BytesIO()
        im.save(bio,format="PNG")
        return bio.getvalue()

    def experience_draft(self,obj: dict)->dict:
        mission_id=str(obj.get('id') or '')
        platform=self.platform();missions=((platform or {}).get('missions') or {}).get('items') or []
        mission=next((m for m in missions if isinstance(m,dict) and str(m.get('id') or '')==mission_id),None)
        if mission is None:raise ExperienceDraftError('Experience not found')
        return compose_experience_draft(self.preferences(),mission,self.schema())

    def roster_hall(self)->dict:
        row=self.actions.plan('roster.hall',{})
        return row.get('plan',row) if isinstance(row,dict) else {}

    def roster_legend(self,obj: dict)->dict:
        return self.actions.perform('roster.legend_set',{'id':str(obj.get('id') or ''),'enabled':bool(obj.get('enabled',True))})

    def roster_synthesis_plan(self,obj: dict)->dict:
        return self.actions.plan('roster.synthesis_plan',{
            'parent_a':str(obj.get('parent_a') or ''),
            'parent_b':str(obj.get('parent_b') or ''),
            'name':str(obj.get('name') or 'Monster'),
        })

    def roster_synthesize(self,obj: dict)->dict:
        return self.actions.perform('roster.synthesize',{
            'parent_a':str(obj.get('parent_a') or ''),
            'parent_b':str(obj.get('parent_b') or ''),
            'name':str(obj.get('name') or 'Monster'),
        })

    def roster_snapshot(self)->dict:
        row=self.actions.plan('roster.snapshot',{})
        return row.get('plan',row) if isinstance(row,dict) else {"items":[]}

    def roster_switch(self,obj: dict)->dict:
        return self.actions.perform('roster.switch',{'id':str(obj.get('id') or '')})

    def roster_preferred(self,obj: dict)->dict:
        row=self.actions.plan('roster.presentation_get',{'id':str(obj.get('id') or '')})
        return row.get('plan',row) if isinstance(row,dict) else {}

    def roster_remember_presentation(self,obj: dict)->dict:
        beast_id=str(obj.get('id') or '')
        draft=obj.get('draft') if isinstance(obj.get('draft'),dict) else self.preferences()
        cfg=self.validate(draft)
        payload={k:cfg[k] for k in (
            'theme','face_profile','animation_profile','renderers','theme_options','dashboard_widgets',
            'custom_boards','context_decks','active_context_deck','palette_overrides','correlation_keys'
        )}
        experience_id=str(obj.get('experience_id') or '').strip()
        if experience_id:payload['experience_id']=experience_id
        return self.actions.perform('roster.presentation_set',{'id':beast_id,'presentation':payload})

    def roster_clear_presentation(self,obj: dict)->dict:
        return self.actions.perform('roster.presentation_clear',{'id':str(obj.get('id') or '')})

    def capsule_preview(self,obj: dict)->dict:
        row=self.api.capsule_export(
            capsule_type="lineage",
            beast_id=str(obj.get("beast_id") or "") or None,
            include_name=bool(obj.get("include_name",True)),
            include_achievements=bool(obj.get("include_achievements",False)),
            include_appearance=bool(obj.get("include_appearance",True)),
            qr_chars=max(128,min(900,int(obj.get("qr_chars") or 220))),
        )
        if not isinstance(row,dict):
            row={"ok":False,"error":"Capsule export returned no data"}
        row=dict(row)
        row["studio_qr"]=qr_backend_status()
        row["import_performed"]=False
        row["publish_performed"]=False
        return row

    def capsule_qr_png(self,obj: dict)->bytes:
        frame=str(obj.get("frame") or "")
        if not frame.startswith("BCQ1|"):
            raise ValueError("QR frame must be a BCQ1 Capsule transport frame")
        if len(frame)>3000:
            raise ValueError("QR frame is oversized")
        if not qr_backend_status().get("available"):
            raise ValueError("QR renderer dependency is not installed")
        im=Image.new("RGB",(512,512),(255,255,255))
        draw_qr(ImageDraw.Draw(im),(0,0,511,511),frame,error_correction="M")
        out=io.BytesIO();im.save(out,format="PNG",optimize=True)
        return out.getvalue()

    def global_profile(self)->dict:
        row=self.actions.plan('global.preview',{})
        return row.get('plan',row) if isinstance(row,dict) else {}

    def global_policy_set(self,obj: dict)->dict:
        return self.actions.perform('global.policy_set',{'policy':obj.get('policy') if isinstance(obj.get('policy'),dict) else {}})

    def platform(self)->dict:
        return self.api.platform_bundle()

    def experiences(self)->dict:
        return self.api.experiences()

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

    def depot_catalog(self,query: str='',pack_type: str='')->dict:
        return self.depot.combined(query,pack_type)

    def depot_upload(self,name: str,data: bytes)->dict:
        return self.depot.save(name,data)

    def pack_upload(self,name: str,data: bytes)->dict:
        return self.pack_files.save(name,data)

    def pack_inspect(self,obj: dict)->dict:
        return self.actions.perform('pack.inspect',{'name':str(obj.get('name') or '')})

    def pack_stage(self,obj: dict)->dict:
        return self.actions.perform('pack.stage',{'name':str(obj.get('name') or ''),'replace':bool(obj.get('replace',False))})

    def pack_install_plan(self,obj: dict)->dict:
        return self.actions.plan('pack.install',{'id':str(obj.get('id') or '')})

    def pack_install(self,obj: dict)->dict:
        return self.actions.perform('pack.install',{'id':str(obj.get('id') or '')})

    def pack_rollback_plan(self,obj: dict)->dict:
        return self.actions.plan('pack.rollback',{'transaction_id':str(obj.get('transaction_id') or '')})

    def pack_rollback(self,obj: dict)->dict:
        return self.actions.perform('pack.rollback',{'transaction_id':str(obj.get('transaction_id') or '')})

    def pack_activate_plan(self,obj: dict)->dict:
        return self.actions.plan('pack.activate',{'id':str(obj.get('id') or '')})

    def pack_activate(self,obj: dict)->dict:
        return self.actions.perform('pack.activate',{'id':str(obj.get('id') or '')})

    def pack_deactivate_plan(self,obj: dict)->dict:
        return self.actions.plan('pack.deactivate',{'id':str(obj.get('id') or '')})

    def pack_deactivate(self,obj: dict)->dict:
        return self.actions.perform('pack.deactivate',{'id':str(obj.get('id') or '')})

    def pack_history(self)->dict:
        row=self.actions.plan('pack.history',{'limit':30})
        return row.get('plan',row) if isinstance(row,dict) else {'items':[]}

    def presentation_plan(self,obj: dict)->dict:
        return self.actions.plan('presentation.plan',{'target':str(obj.get('target') or '')})

    def experience_try_plan(self,obj: dict)->dict:
        return self.actions.plan('experience.try_on_tft_plan',{
            'id':str(obj.get('id') or ''),
            'page':str(obj.get('page') or 'home'),
            'duration_sec':int(obj.get('duration_sec') or 90),
        })

    def update_stage_plan(self,obj: dict)->dict:
        return self.actions.plan('update.stage',{'component':str(obj.get('component') or ''),'asset_name':str(obj.get('asset_name') or '')})

    def update_stage(self,obj: dict)->dict:
        return self.actions.perform('update.stage',{'component':str(obj.get('component') or ''),'asset_name':str(obj.get('asset_name') or '')})

    def update_pack_plan(self,obj: dict)->dict:
        return self.actions.plan('update.pack_apply',{'component':str(obj.get('component') or '')})

    def update_pack_apply(self,obj: dict)->dict:
        return self.actions.perform('update.pack_apply',{'component':str(obj.get('component') or '')})

    def update_policy_snapshot(self)->dict:
        return self.update_policies.load()

    def set_update_policy(self,obj: dict)->dict:
        return self.update_policies.set_policy(str(obj.get('component') or ''),str(obj.get('policy') or ''))



class Handler(BaseHTTPRequestHandler):
    server_version='BeastStudio/0.19'
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
        if path=='/api/experiences':return self._send(200,self.st.experiences())
        if path=='/api/global-profile':return self._send(200,self.st.global_profile())
        if path=='/api/roster':return self._send(200,self.st.roster_snapshot())
        if path=='/api/roster-hall':return self._send(200,self.st.roster_hall())
        if path=='/api/roster-preferred':
            rid=parse_qs(urlsplit(self.path).query).get('id',[''])[0];return self._send(200,self.st.roster_preferred({'id':rid}))
        if path=='/api/update-policies':return self._send(200,self.st.update_policy_snapshot())
        if path=='/api/pack-history':return self._send(200,self.st.pack_history())
        if path=='/api/depot':
            qs=parse_qs(urlsplit(self.path).query);return self._send(200,self.st.depot_catalog(qs.get('q',[''])[0],qs.get('type',[''])[0]))
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
        if path not in {'/api/library-upload','/api/pack-upload','/api/depot-upload'}:return self._send(404,{'error':'not found'})
        if not self._auth():return self._send(403,{'error':'paired Studio token required'})
        try:
            n=int(self.headers.get('Content-Length','0') or 0)
            limit=128*1024*1024 if path=='/api/pack-upload' else (1024*1024 if path=='/api/depot-upload' else 64*1024*1024)
            if n<0 or n>limit:raise ValueError('invalid or oversized upload')
            name=parse_qs(urlsplit(self.path).query).get('name',[''])[0]
            data=self.rfile.read(n)
            if len(data)!=n:raise ValueError('incomplete upload')
            if path=='/api/pack-upload':result=self.st.pack_upload(name,data)
            elif path=='/api/depot-upload':result=self.st.depot_upload(name,data)
            else:result=self.st.library_upload(name,data)
            return self._send(200,result)
        except (LibraryFileError,PackFileError,DepotCatalogError,ValueError) as exc:return self._send(400,{'error':str(exc)})
        except Exception as exc:return self._send(500,{'error':type(exc).__name__})

    def do_POST(self):
        path=urlsplit(self.path).path
        try:n=min(int(self.headers.get('Content-Length','0') or 0),512_000);obj=json.loads(self.rfile.read(n) or b'{}')
        except Exception:return self._send(400,{'error':'invalid json'})
        try:
            if path in {'/api/preview','/api/apply'} and not self._auth():return self._send(403,{'error':'paired Studio token required'})
            if path in {'/api/plugin-plan','/api/plugin-toggle','/api/service-plan','/api/service-restart','/api/backup-plan','/api/backup-create','/api/support-plan','/api/support-create','/api/variant-save','/api/variant-load','/api/variant-delete','/api/update-policy','/api/pack-inspect','/api/pack-stage','/api/pack-install-plan','/api/pack-install','/api/pack-rollback-plan','/api/pack-rollback','/api/pack-activate-plan','/api/pack-activate','/api/pack-deactivate-plan','/api/pack-deactivate','/api/update-stage-plan','/api/update-stage','/api/update-pack-plan','/api/update-pack-apply','/api/experience-draft','/api/experience-preview','/api/experience-try-plan','/api/global-policy','/api/roster-switch','/api/roster-presentation','/api/roster-presentation-clear','/api/roster-synthesis-plan','/api/roster-synthesize','/api/roster-legend','/api/presentation-plan','/api/capsule-preview','/api/capsule-qr'} and not self._auth():return self._send(403,{'error':'paired Studio token required'})
            if path=='/api/preview':return self._send(200,self.st.preview(obj),'image/png')
            if path=='/api/capsule-preview':return self._send(200,self.st.capsule_preview(obj))
            if path=='/api/capsule-qr':return self._send(200,self.st.capsule_qr_png(obj),'image/png')
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
            if path=='/api/update-policy':return self._send(200,self.st.set_update_policy(obj))
            if path=='/api/pack-inspect':return self._send(200,self.st.pack_inspect(obj))
            if path=='/api/pack-stage':return self._send(200,self.st.pack_stage(obj))
            if path=='/api/pack-install-plan':return self._send(200,self.st.pack_install_plan(obj))
            if path=='/api/pack-install':return self._send(200,self.st.pack_install(obj))
            if path=='/api/pack-rollback-plan':return self._send(200,self.st.pack_rollback_plan(obj))
            if path=='/api/pack-rollback':return self._send(200,self.st.pack_rollback(obj))
            if path=='/api/pack-activate-plan':return self._send(200,self.st.pack_activate_plan(obj))
            if path=='/api/pack-activate':return self._send(200,self.st.pack_activate(obj))
            if path=='/api/pack-deactivate-plan':return self._send(200,self.st.pack_deactivate_plan(obj))
            if path=='/api/pack-deactivate':return self._send(200,self.st.pack_deactivate(obj))
            if path=='/api/update-stage-plan':return self._send(200,self.st.update_stage_plan(obj))
            if path=='/api/update-stage':return self._send(200,self.st.update_stage(obj))
            if path=='/api/update-pack-plan':return self._send(200,self.st.update_pack_plan(obj))
            if path=='/api/update-pack-apply':return self._send(200,self.st.update_pack_apply(obj))
            if path=='/api/experience-preview':return self._send(200,self.st.experience_preview(obj),'image/png')
            if path=='/api/experience-draft':return self._send(200,self.st.experience_draft(obj))
            if path=='/api/experience-try-plan':return self._send(200,self.st.experience_try_plan(obj))
            if path=='/api/global-policy':return self._send(200,self.st.global_policy_set(obj))
            if path=='/api/roster-switch':return self._send(200,self.st.roster_switch(obj))
            if path=='/api/roster-synthesis-plan':return self._send(200,self.st.roster_synthesis_plan(obj))
            if path=='/api/roster-synthesize':return self._send(200,self.st.roster_synthesize(obj))
            if path=='/api/roster-legend':return self._send(200,self.st.roster_legend(obj))
            if path=='/api/roster-presentation':return self._send(200,self.st.roster_remember_presentation(obj))
            if path=='/api/roster-presentation-clear':return self._send(200,self.st.roster_clear_presentation(obj))
            if path=='/api/presentation-plan':return self._send(200,self.st.presentation_plan(obj))
        except (ValueError,UpdatePolicyError,ExperienceDraftError) as exc:return self._send(400,{'error':str(exc)})
        except Exception as exc:return self._send(500,{'error':type(exc).__name__})
        return self._send(404,{'error':'not found'})


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True

def serve(host='0.0.0.0',port=8091,root='/opt/beast-ui',prefs='/var/lib/beastagotchi/ui/preferences.json',token_file='/var/lib/beastagotchi/ui/studio.token'):
    state=StudioState(root,prefs,token_file);srv=ReusableThreadingHTTPServer((host,int(port)),Handler);srv.studio=state;srv.serve_forever()

def main():
    p=argparse.ArgumentParser();p.add_argument('--host',default='0.0.0.0');p.add_argument('--port',type=int,default=8091);p.add_argument('--root',default='/opt/beast-ui');p.add_argument('--prefs',default='/var/lib/beastagotchi/ui/preferences.json');p.add_argument('--token-file',default='/var/lib/beastagotchi/ui/studio.token');a=p.parse_args();serve(a.host,a.port,a.root,a.prefs,a.token_file)
