from __future__ import annotations

import json
import logging
import math
import os
import threading
import time
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .backgrounds import draw_background, draw_foreground_effects
from .controls import rows_for, hint_for, TOUCH_ZONES
from .hitbox import hit, expanded_hitbox, MIN_TARGET, NORMAL_TARGET, PRIMARY_TARGET
from .datafeed import DataFeed
from .face import FaceEngine
from .framebuffer import FrameBuffer
from .scene_runtime import SceneRuntime
from .scene_compositor import compositor_cache_telemetry
from .display import DisplayTransform
from .input import TouchInput
from .pages import Pages
from .reactions import ReactionGovernor
from .theme import load_theme, discover_enabled_pack_themes
from .pack_content import discover_enabled_pack_boards
from .rare_overlay import render_rare_overlay, acknowledge_rare_event
from .monster_reveal import render_monster_reveal, reveal_active
from .pwn_native import NativePwnFrameSource
from .native_effects import apply_native_effects, palette_color
from .widgets import panel
from .design import TOKENS
from . import __version__ as UI_VERSION
from .apps import AppRegistry, AppDefinition, APPS, OPTIONAL_APPS
from .qr_render import draw_qr, qr_backend_status
from .customization import (
    validate_dashboard_widgets, dashboard_history_keys, validate_context_decks,
    validate_palette_overrides, validate_correlation_keys, validate_custom_boards, PALETTE_SLOTS, dashboard_widget_box,
)

log = logging.getLogger('beastui')


class BeastUI:
    W,H=TOKENS.canvas_w,TOKENS.canvas_h; HEADER_H=TOKENS.header_h; FOOTER_Y=TOKENS.footer_y
    THEMES=['pwn_native_raw','pwn_native_dark','pwn_native_light','pwn_native_chroma','pwn_dark','pwn_light','pwn_chroma','classic','matrix','starcore','blackice','hunter','minimal','synthwave','amber_tactical','ghost_minimal','cyberpunk','wopr_norad','lcars','retro_crt']
    RENDERER_CHOICES={
        'recon':['radar','polar','bars','signal'],
        'spectrum':['bars','line','heatmap','radar','area','polar','histogram','donut','waveform','waterfall'],
        'captures':['bars','donut','radial','timeline'],
        'system':['line','area','waveform','histogram','waterfall'],
    }
    # 2x2 launcher geometry keeps every visible card and navigation action at
    # or above the validated 48px resistive-touch target.
    APP_PAGE_SIZE=4
    APP_CARD_BOXES=(
        (16,94,236,152),(244,94,464,152),
        (16,158,236,216),(244,158,464,216),
    )
    APP_CAT_PREV=(12,40,72,88)
    APP_CAT_NEXT=(408,40,468,88)
    APP_NAV_PREV=(12,224,154,274)
    APP_NAV_CLOSE=(162,224,318,274)
    APP_NAV_NEXT=(326,224,468,274)
    # Platform browsers use the same proven 50px bottom action geometry as
    # the app launcher. The prior 36px buttons looked acceptable off-screen
    # but were below the reference resistive-touch minimum.
    PLATFORM_PAGE_SIZE=3
    PLATFORM_NAV_PREV=(12,224,154,274)
    PLATFORM_NAV_CLOSE=(162,224,318,274)
    PLATFORM_NAV_NEXT=(326,224,468,274)
    PLATFORM_SPECIAL_CLOSE=(326,224,468,274)
    CONTROL_APP_BOX=(352,40,468,88)
    CONTROL_QUICK_BOXES=(
        (16,96,236,174),(244,96,464,174),
        (16,180,236,258),(244,180,464,258),
    )
    CAPSULE_QR_BOX=(16,54,222,260)
    CAPSULE_PREV=(232,224,304,274)
    CAPSULE_CLOSE=(308,224,382,274)
    CAPSULE_NEXT=(386,224,464,274)

    def __init__(self,root='/opt/beast-ui',framebuffer='/dev/fb1',output=None,theme_id='classic', *, physical_size=None, display_mode='fit', display_resample='bilinear'):
        self.root=Path(root); self.output=output
        self.pref_path=Path('/var/lib/beastagotchi/ui/preferences.json') if output is None else None
        self._pref_sig=None;self._pref_check_at=0.0
        # Off-screen renders must honor the requested theme and must never leak
        # preferences between tests/renders.
        pref=self._load_prefs() if self.pref_path is not None else {}
        theme_id=str(pref.get('theme') or theme_id)
        self._builtin_theme_ids=list(type(self).THEMES)
        self.theme_paths={tid:self.root/'themes'/f'{tid}.json' for tid in self._builtin_theme_ids if (self.root/'themes'/f'{tid}.json').is_file()}
        for tid,path in discover_enabled_pack_themes().items():
            if tid not in self.theme_paths:self.theme_paths[tid]=path
        self.THEMES=list(self.theme_paths)
        if theme_id not in self.theme_paths:theme_id='classic'
        self.theme=load_theme(self.theme_paths[theme_id])
        self.renderers=dict(pref.get('renderers') or {})
        for _pid,_choices in self.RENDERER_CHOICES.items():
            self.renderers.setdefault(_pid,_choices[0])
        self.theme_options=dict(pref.get('theme_options') or {})
        self.dashboard_widgets=validate_dashboard_widgets(pref.get('dashboard_widgets'))
        self.custom_boards=validate_custom_boards(pref.get('custom_boards'))
        self.pack_boards=discover_enabled_pack_boards()
        self.face_profile_pref=str(pref.get('face_profile') or 'builtin');self.animation_profile_pref=str(pref.get('animation_profile') or 'none')
        self.face=FaceEngine(profile_id=self.face_profile_pref,animation_profile_id=self.animation_profile_pref); self.pages=Pages(self.face); self.page=0; self.phase=0.0; self.phase_override=None
        self.scene_runtime=SceneRuntime()
        self.apps=self._build_app_registry()
        _app_ids=[a.id for a in self.apps.all()]
        self.context_decks=validate_context_decks(pref.get('context_decks'),app_ids=_app_ids)
        self.active_context_deck=str(pref.get('active_context_deck') or '')
        if self.active_context_deck not in {d['id'] for d in self.context_decks}:self.active_context_deck=''
        self.palette_overrides=validate_palette_overrides(pref.get('palette_overrides'),theme_ids=self.THEMES)
        self.correlation_keys=validate_correlation_keys(pref.get('correlation_keys'))
        self._apply_palette_overrides()
        self.state={}; self.events=[]; self.histories={}; self.aux={}; self.data_error=None;self._capability_app_sig=None
        self.stop_event=threading.Event(); self.dirty=threading.Event(); self.drawer=False; self.help_overlay=False; self.touch_zones_overlay=False
        self.theme_library=False; self.theme_detail=None; self.theme_detail_page=0; self.theme_library_offset=0; self.achievements_overlay=False
        self.visualizer_overlay=False; self.visualizer_offset=0
        self.app_launcher=False; self.app_offset=0; self.app_category_idx=0; self.active_board_id='' 
        if self.active_context_deck:
            _cats=self._app_categories();_label=next((k for k,v in self._deck_category_map().items() if v.get('id')==self.active_context_deck),None)
            if _label in _cats:self.app_category_idx=_cats.index(_label)
        self.telemetry_overlay=False; self.telemetry_offset=0
        self.widget_inspector_overlay=False; self.widget_inspector_key=None
        self.correlation_overlay=False
        self.plugins_overlay=False; self.plugins_offset=0
        self.beastdex_overlay=False; self.beastdex_offset=0; self.beastdex_detail=None
        self.capture_vault_overlay=False; self.capture_vault_offset=0; self.capture_vault_detail=None
        self.performance_overlay=False; self.performance_offset=0
        self.capsule_share_overlay=False; self.capsule_share={}; self.capsule_frame_idx=0; self.capsule_loading=False
        self.studio_overlay=False
        self.platform_overlay=None; self.platform_offset=0
        self.achievement_tab='achievements'; self.achievement_filter='all'; self.achievement_sort='progress'; self.achievement_offset=0; self.achievement_detail=None
        self._theme_preview_original=None; self._theme_preview_options=None
        _physical=tuple(physical_size or (self.W,self.H))
        self.display_transform=DisplayTransform((self.W,self.H),_physical,mode=display_mode,resample=display_resample,background=self.theme.c('bg'))
        self.fb=FrameBuffer(framebuffer,int(_physical[0]),int(_physical[1]),output=output); self.touch=None; self.fonts=self._fonts(); self.feed=None
        self.native_source=NativePwnFrameSource(os.environ.get('BEAST_PWN_FRAME_PATH', NativePwnFrameSource.DEFAULT_PATH))
        cfg=self.root/'config'/'touch.json'
        if output is None and cfg.exists():
            try:self.touch=TouchInput(str(cfg),self._on_physical_input)
            except Exception:self.touch=None
        self.last_render=0.0; self.last_input=None; self.last_input_at=0.0
        self.touching=False; self.button_flash=None; self.button_flash_at=0.0; self.transition=None; self.monster_reveal_dismissed_id=None; self._monster_reveal_was_active=False
        self.test_mode_path=Path('/run/beastagotchi/ui-test-mode'); self.runtime_path=Path('/run/beastagotchi/ui-runtime.json'); self.rare_preview_path=Path('/var/lib/beastagotchi/ui/rare_preview.json')
        self._render_samples=[]; self._compose_samples=[]; self._write_samples=[]; self._frame_count=0; self._runtime_started=time.monotonic()
        self.reactions=ReactionGovernor(); self._last_reaction_id=None
        self._bg_cache=None;self._bg_cache_key=None;self._bg_cache_at=0.0

    def _theme_path(self,theme_id):
        return self.theme_paths.get(str(theme_id))

    def _refresh_theme_catalog(self):
        paths={tid:self.root/'themes'/f'{tid}.json' for tid in self._builtin_theme_ids if (self.root/'themes'/f'{tid}.json').is_file()}
        for tid,path in discover_enabled_pack_themes().items():
            if tid not in paths:paths[tid]=path
        changed=tuple(paths)!=tuple(getattr(self,'theme_paths',{}))
        current=getattr(getattr(self,'theme',None),'id',None)
        self.theme_paths=paths;self.THEMES=list(paths)
        if changed and hasattr(self,'palette_overrides'):
            self.palette_overrides=validate_palette_overrides(self.palette_overrides,theme_ids=self.THEMES)
        if current and current not in paths and paths.get('classic'):
            self.theme=load_theme(paths['classic']);self._bg_cache=None;self._bg_cache_key=None
            if getattr(self,'pref_path',None) is not None:self._save_prefs()
        return changed

    def _on_physical_input(self, kind, payload):
        """Translate physical touch coordinates into the logical Beast canvas."""
        if isinstance(payload, dict) and 'x' in payload and 'y' in payload:
            mapped=self.display_transform.to_logical_point(payload.get('x',0),payload.get('y',0))
            if mapped is None:
                # Touches in compatibility-mode letterbox/pillarbox bars are
                # deliberately ignored rather than mapped to an edge control.
                return
            payload=dict(payload);payload['physical_x']=payload.get('x');payload['physical_y']=payload.get('y');payload['x'],payload['y']=mapped
        self.on_input(kind,payload)

    def _all_boards(self):
        return list(getattr(self,'custom_boards',[]) or []) + list(getattr(self,'pack_boards',[]) or [])

    def _build_app_registry(self):
        extras=[]
        st=getattr(self,'state',{}) or {}
        if st.get('containers.runtime.available'):
            extras.append(OPTIONAL_APPS['containers'])
        if st.get('ai.local.available'):
            extras.append(OPTIONAL_APPS['ai_operator'])
        if st.get('display.external_connected'):
            extras.append(OPTIONAL_APPS['command_center'])
        for board in self._all_boards():
            bid=str(board.get('id') or '')
            if not bid:continue
            desc='Read-only Beast Pack live telemetry board' if board.get('source_pack') else 'User-composed live telemetry board'
            extras.append(AppDefinition(f'board:{bid}',str(board.get('label') or bid),'Boards','board',bid,desc,'info'))
        return AppRegistry((*APPS,*extras))

    def _active_dashboard_widgets(self):
        if self.active_board_id:
            for board in self._all_boards():
                if str(board.get('id'))==self.active_board_id:return list(board.get('widgets') or [])
        return list(self.dashboard_widgets or [])

    def _load_prefs(self):
        if self.pref_path is None:return {}
        try:return json.loads(self.pref_path.read_text())
        except Exception:return {}

    def _save_prefs(self):
        if self.pref_path is None:return
        try:
            self.pref_path.parent.mkdir(parents=True,exist_ok=True)
            self.pref_path.write_text(json.dumps({'theme':self.theme.id,'face_profile':self.face_profile_pref,'animation_profile':self.animation_profile_pref,'renderers':self.renderers,'theme_options':self.theme_options,'dashboard_widgets':self.dashboard_widgets,'custom_boards':self.custom_boards,'context_decks':self.context_decks,'active_context_deck':self.active_context_deck,'palette_overrides':self.palette_overrides,'correlation_keys':self.correlation_keys},indent=2)+'\n')
            st=self.pref_path.stat();self._pref_sig=(int(st.st_mtime_ns),int(st.st_size))
        except Exception as exc: log.warning('could not persist UI prefs: %s',exc)

    def _reload_external_prefs(self):
        """Apply Beast Studio preference writes without restarting the UI."""
        if self.pref_path is None:return
        now=time.monotonic()
        if now-self._pref_check_at<1.0:return
        self._pref_check_at=now
        try:
            st=self.pref_path.stat();sig=(int(st.st_mtime_ns),int(st.st_size))
            if sig==self._pref_sig:return
            obj=json.loads(self.pref_path.read_text())
            tid=str(obj.get('theme') or self.theme.id)
            self._refresh_theme_catalog();tp=self._theme_path(tid)
            if tp and tp.exists():self.theme=load_theme(tp);self._bg_cache=None;self._bg_cache_key=None
            self.face_profile_pref=str(obj.get('face_profile') or 'builtin');self.animation_profile_pref=str(obj.get('animation_profile') or 'none');self.face.refresh_profiles();self.face.refresh_animation_profiles();self.face.set_profile(self.face_profile_pref);self.face.set_animation_profile(self.animation_profile_pref)
            incoming=obj.get('renderers') or {}
            if isinstance(incoming,dict):
                for pid,choices in self.RENDERER_CHOICES.items():
                    val=str(incoming.get(pid) or self.renderers.get(pid) or choices[0])
                    if val in choices:self.renderers[pid]=val
            opts=obj.get('theme_options') or {}
            if isinstance(opts,dict):self.theme_options=opts
            self.dashboard_widgets=validate_dashboard_widgets(obj.get('dashboard_widgets'))
            self.custom_boards=validate_custom_boards(obj.get('custom_boards'))
            self.pack_boards=discover_enabled_pack_boards()
            self.apps=self._build_app_registry()
            if self.active_board_id and self.active_board_id not in {str(b.get('id')) for b in self._all_boards()}:self.active_board_id=''
            self.context_decks=validate_context_decks(obj.get('context_decks'),app_ids=[a.id for a in self.apps.all()])
            self.active_context_deck=str(obj.get('active_context_deck') or '')
            if self.active_context_deck not in {d['id'] for d in self.context_decks}:self.active_context_deck=''
            self.palette_overrides=validate_palette_overrides(obj.get('palette_overrides'),theme_ids=self.THEMES)
            self.correlation_keys=validate_correlation_keys(obj.get('correlation_keys'))
            self._apply_palette_overrides()
            if self.feed:self.feed.set_extra_history_keys(tuple(dashboard_history_keys(self._active_dashboard_widgets()))+tuple(self.correlation_keys))
            if not self.app_launcher and self.active_context_deck:
                _cats=self._app_categories();_label=next((k for k,v in self._deck_category_map().items() if v.get('id')==self.active_context_deck),None)
                if _label in _cats:self.app_category_idx=_cats.index(_label)
            self._pref_sig=sig;self.fb.reset_diff();self.dirty.set()
            self.button_flash='studio:applied';self.button_flash_at=time.monotonic()
        except FileNotFoundError:
            return
        except Exception as exc:
            log.warning('could not reload Beast Studio prefs: %s',exc)

    def _fonts(self):
        paths=['/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']; path=next((p for p in paths if os.path.exists(p)),None)
        def f(n):
            try:return ImageFont.truetype(path,n) if path else ImageFont.load_default()
            except Exception:return ImageFont.load_default()
        return {'micro':f(6),'tiny':f(7),'small':f(9),'body':f(11),'medium':f(13),'large':f(18),'title':f(16)}

    def _apply_palette_overrides(self):
        vals=(getattr(self,'palette_overrides',{}) or {}).get(self.theme.id,{})
        for slot,color in vals.items():
            if slot not in PALETTE_SLOTS:continue
            try:
                h=str(color).lstrip('#');self.theme.colors[slot]=tuple(int(h[i:i+2],16) for i in (0,2,4))
            except Exception:continue

    def set_theme(self,theme_id,persist=True):
        self._refresh_theme_catalog();p=self._theme_path(theme_id)
        if p and p.exists():
            self.theme=load_theme(p);self._apply_palette_overrides();self._bg_cache=None;self._bg_cache_key=None
            if persist:self._save_prefs()
            self.button_flash=f'theme:{theme_id}'; self.button_flash_at=time.monotonic(); self.dirty.set()


    def _is_native_theme(self):
        return self.theme.id in {'pwn_native_raw','pwn_native_dark','pwn_native_light','pwn_native_chroma'}

    def _native_mode(self):
        if self.theme.id=='pwn_native_raw': return 'raw'
        if self.theme.id=='pwn_native_light': return 'light'
        if self.theme.id=='pwn_native_chroma': return 'chroma'
        return 'dark'

    def _native_ink_color(self):
        if self.theme.id!='pwn_native_chroma':
            return self.theme.c('primary')
        opts=self.options_for_theme('pwn_native_chroma')
        if str(opts.get('ink_mode','mood'))=='mood':
            mood=str(self.state.get('pwnagotchi.mood') or 'awake').lower()
            return (self.theme.mood_colors or {}).get(mood, self.theme.c('primary'))
        return palette_color(str(opts.get('palette_mode','green')),self.phase,self.theme.c('primary'))

    def _native_idle(self):
        return self._is_native_theme() and not any((self.drawer,self.visualizer_overlay,self.theme_library,self.theme_detail,self.achievements_overlay,self.help_overlay,self.touch_zones_overlay,self.app_launcher,self.telemetry_overlay,self.plugins_overlay,self.beastdex_overlay,self.capture_vault_overlay,self.performance_overlay,self.studio_overlay,self.platform_overlay,self.widget_inspector_overlay,self.correlation_overlay))

    def options_for_theme(self,theme_id=None):
        tid=str(theme_id or self.theme.id)
        base={}
        if tid=='matrix':
            base={'layer_mode':'mixed','density':'dense','speed_mode':'fast','palette_mode':'green','accent_mix':'off','foreground_fraction':0.14,'primary_color':'green','secondary_color':'cyan','tertiary_color':'violet','quaternary_color':'amber','glyph_set':'mixed','trail_mode':'normal','reactions_enabled':'on'}
        elif tid=='pwn_native_chroma':
            base={'ink_mode':'mood','palette_mode':'green','glow_level':'soft','effect':'clean'}
        elif tid=='classic':
            base={'grid_density':'normal','scanline':'on','pulse_level':'subtle'}
        elif tid=='starcore':
            base={'star_density':'normal','twinkle':'normal','orbit':'on'}
        elif tid=='blackice':
            base={'frost_density':'normal','drift':'slow','crystal_overlay':'subtle'}
        elif tid=='hunter':
            base={'grid_density':'normal','reticle':'on','embers':'sparse'}
        elif tid=='minimal':
            base={'ambient':'off','panel_emphasis':'soft'}
        elif tid=='synthwave':
            base={'grid_density':'normal','sun':'half','horizon_glow':'soft','stars':'normal'}
        elif tid=='amber_tactical':
            base={'grid_density':'normal','scope':'on','sweep':'slow','brackets':'on'}
        elif tid=='ghost_minimal':
            base={'ambient':'soft','ghosts':'sparse','edge_trace':'on'}
        elif tid=='cyberpunk':
            base={'city':'on','glitch':'low','lanes':'normal','rain':'sparse'}
        elif tid=='wopr_norad':
            base={'grid_density':'normal','rings':'on','blips':'normal','sweep':'slow'}
        elif tid=='lcars':
            base={'stars':'normal','bands':'full','pulse':'soft'}
        elif tid=='retro_crt':
            base={'phosphor':'green','noise':'low','grid':'soft','bloom':'soft'}
        base.update(dict(self.theme_options.get(tid) or {}))
        return base

    def render_options_for_theme(self,theme_id=None):
        """Return transient, governor-limited options without mutating saved prefs."""
        tid=str(theme_id or self.theme.id);opts=dict(self.options_for_theme(tid))
        mode=str(self.state.get('governor.mode') or 'FULL').upper();opts['_governor_mode']=mode
        if mode=='FULL':return opts
        if mode=='GUARDED':
            if tid=='matrix' and opts.get('density') in {'storm','deluge'}:opts['density']='heavy'
            if tid=='starcore' and opts.get('star_density')=='nebula':opts['star_density']='dense'
            if tid=='blackice' and opts.get('frost_density')=='whiteout':opts['frost_density']='heavy'
            if tid=='hunter' and opts.get('embers')=='heavy':opts['embers']='normal'
            if tid=='synthwave' and opts.get('stars')=='dense':opts['stars']='normal'
            return opts
        if mode=='REDUCED':
            if tid=='matrix':opts.update({'density':'normal','speed_mode':'normal','trail_mode':'normal','foreground_fraction':'0.00'})
            elif tid=='starcore':opts.update({'star_density':'normal','twinkle':'low','orbit':'off'})
            elif tid=='blackice':opts.update({'frost_density':'normal','drift':'slow','crystal_overlay':'off'})
            elif tid=='hunter':opts.update({'grid_density':'light','reticle':'on','embers':'off'})
            elif tid=='synthwave':opts.update({'grid_density':'light','horizon_glow':'soft','stars':'sparse'})
            elif tid=='amber_tactical':opts.update({'grid_density':'light','sweep':'off'})
            elif tid=='ghost_minimal':opts.update({'ambient':'off','ghosts':'off'})
            elif tid=='cyberpunk':opts.update({'glitch':'off','rain':'off','lanes':'light'})
            elif tid=='wopr_norad':opts.update({'blips':'sparse','sweep':'off'})
            elif tid=='lcars':opts.update({'stars':'sparse','pulse':'off'})
            elif tid=='retro_crt':opts.update({'noise':'off','bloom':'off'})
            elif tid=='classic':opts.update({'grid_density':'light','pulse_level':'off'})
            return opts
        # SURVIVAL: preserve readability and identity, remove optional motion/load.
        if tid=='matrix':opts.update({'density':'sparse','speed_mode':'drift','trail_mode':'short','foreground_fraction':'0.00','accent_mix':'off'})
        elif tid=='starcore':opts.update({'star_density':'sparse','twinkle':'off','orbit':'off'})
        elif tid=='blackice':opts.update({'frost_density':'light','drift':'still','crystal_overlay':'off'})
        elif tid=='hunter':opts.update({'grid_density':'off','reticle':'on','embers':'off'})
        elif tid=='synthwave':opts.update({'grid_density':'off','horizon_glow':'off','stars':'off','sun':'half'})
        elif tid=='amber_tactical':opts.update({'grid_density':'off','scope':'on','sweep':'off','brackets':'on'})
        elif tid=='ghost_minimal':opts.update({'ambient':'off','ghosts':'off','edge_trace':'on'})
        elif tid=='cyberpunk':opts.update({'city':'on','glitch':'off','lanes':'off','rain':'off'})
        elif tid=='wopr_norad':opts.update({'grid_density':'light','rings':'on','blips':'off','sweep':'off'})
        elif tid=='lcars':opts.update({'stars':'off','bands':'full','pulse':'off'})
        elif tid=='retro_crt':opts.update({'noise':'off','grid':'off','bloom':'off'})
        elif tid=='classic':opts.update({'grid_density':'off','pulse_level':'off','scanline':'off'})
        elif tid=='minimal':opts.update({'ambient':'off'})
        return opts

    def _open_theme_detail(self,tid):
        self._theme_preview_original=self.theme.id
        self._theme_preview_options=json.loads(json.dumps(self.theme_options))
        self.theme_detail=str(tid); self.theme_detail_page=0; self.theme_library=False
        self.set_theme(tid,persist=False); self.dirty.set()

    def _cancel_theme_detail(self):
        if self._theme_preview_options is not None:self.theme_options=self._theme_preview_options
        if self._theme_preview_original:self.set_theme(self._theme_preview_original,persist=False)
        self.theme_detail=None; self.theme_detail_page=0; self.theme_library=True; self._theme_preview_original=None; self._theme_preview_options=None; self.dirty.set()

    def _apply_theme_detail(self):
        self._save_prefs(); self.theme_detail=None; self.theme_detail_page=0; self.theme_library=False; self.drawer=False
        self._theme_preview_original=None; self._theme_preview_options=None; self.button_flash='theme:applied'; self.button_flash_at=time.monotonic(); self.dirty.set()

    def _cycle_theme_option(self,key,values):
        self._step_theme_option(key,values,1)

    def _step_theme_option(self,key,values,delta):
        tid=self.theme.id; opts=dict(self.theme_options.get(tid) or {})
        current=str(opts.get(key) or self.options_for_theme(tid).get(key) or values[0])
        try:i=values.index(current)
        except ValueError:i=0
        opts[key]=values[(i+int(delta))%len(values)]
        self.theme_options[tid]=opts
        self.button_flash=f'option:{key}'
        self.button_flash_at=time.monotonic()
        self.dirty.set()

    MATRIX_PRIMARY_COLORS=['green','lime','cyan','blue','violet','magenta','red','orange','amber','yellow','white']
    MATRIX_ACCENT_COLORS=['off','green','lime','cyan','blue','violet','magenta','red','orange','amber','yellow','white']

    def _matrix_option_rows(self):
        opts=self.options_for_theme('matrix')
        rows=[
            ('layer_mode','LAYER',['background','mixed','foreground']),
            ('density','DENSITY',['sparse','light','normal','dense','heavy','storm','deluge']),
            ('speed_mode','SPEED',['drift','slow','normal','fast','fury','torrent']),
            ('trail_mode','TRAIL',['short','normal','long','extreme']),
            ('glyph_set','GLYPHS',['mixed','digits','binary','hex','symbols']),
            ('palette_mode','PALETTE',['green','cyan','violet','red','amber','rainbow','holiday','custom']),
        ]
        if str(opts.get('palette_mode','green'))=='custom':
            rows.extend([
                ('primary_color','PRIMARY',self.MATRIX_PRIMARY_COLORS),
                ('secondary_color','SECONDARY',self.MATRIX_ACCENT_COLORS),
                ('tertiary_color','TERTIARY',self.MATRIX_ACCENT_COLORS),
                ('quaternary_color','QUATERNARY',self.MATRIX_ACCENT_COLORS),
            ])
        rows.extend([
            ('accent_mix','ACCENTS',['off','sparse','medium','heavy','balanced']),
            ('foreground_fraction','FRONT %',['0.00','0.05','0.10','0.14','0.20','0.30','0.40','0.50']),
            ('reactions_enabled','REACTIONS',['on','off']),
        ])
        return rows

    @staticmethod
    def _native_chroma_option_rows():
        return [
            ('ink_mode','COLOR SOURCE',['mood','fixed']),
            ('palette_mode','FIXED COLOR',['green','cyan','amber','violet','red','white','rainbow']),
            ('glow_level','GLOW',['off','soft','strong']),
            ('effect','EFFECT',['clean','scanlines','vignette','grain','pulse','glitch','halo']),
        ]

    def _theme_option_rows(self,tid=None):
        tid=str(tid or self.theme.id)
        if tid=='matrix':return self._matrix_option_rows()
        if tid=='pwn_native_chroma':return self._native_chroma_option_rows()
        if tid=='classic':return [
            ('grid_density','GRID',['off','light','normal','dense']),
            ('scanline','SCANLINE',['on','off']),
            ('pulse_level','AMBIENT PULSE',['off','subtle','active']),
        ]
        if tid=='starcore':return [
            ('star_density','STARS',['sparse','normal','dense','nebula']),
            ('twinkle','TWINKLE',['off','low','normal','high']),
            ('orbit','ORBIT ARC',['on','off']),
        ]
        if tid=='blackice':return [
            ('frost_density','FROST',['light','normal','heavy','whiteout']),
            ('drift','DRIFT',['still','slow','normal','fast']),
            ('crystal_overlay','CRYSTALS',['off','subtle','active']),
        ]
        if tid=='hunter':return [
            ('grid_density','GRID',['off','light','normal','dense']),
            ('reticle','RETICLE',['on','off']),
            ('embers','EMBERS',['off','sparse','normal','heavy']),
        ]
        if tid=='minimal':return [
            ('ambient','AMBIENT',['off','soft']),
            ('panel_emphasis','PANELS',['soft','normal']),
        ]
        if tid=='synthwave':return [
            ('grid_density','GRID',['off','light','normal','dense']),
            ('sun','SUN',['off','half','full']),
            ('horizon_glow','HORIZON',['off','soft','hot']),
            ('stars','STARS',['off','sparse','normal','dense']),
        ]
        if tid=='amber_tactical':return [
            ('grid_density','GRID',['off','light','normal','dense']),
            ('scope','SCOPE',['on','off']),
            ('sweep','SWEEP',['off','slow','normal','fast']),
            ('brackets','BRACKETS',['on','off']),
        ]
        if tid=='ghost_minimal':return [
            ('ambient','AMBIENT',['off','soft']),
            ('ghosts','GHOSTS',['off','sparse','normal']),
            ('edge_trace','EDGE TRACE',['on','off']),
        ]
        if tid=='cyberpunk':return [
            ('city','CITY SILHOUETTE',['on','off']),('glitch','GLITCH',['off','low','normal','high']),('lanes','NEON LANES',['off','light','normal','dense']),('rain','DIGITAL RAIN',['off','sparse','normal','dense']),
        ]
        if tid=='wopr_norad':return [
            ('grid_density','GRID',['off','light','normal','dense']),('rings','RANGE RINGS',['on','off']),('blips','AMBIENT NODES',['off','sparse','normal','dense']),('sweep','AMBIENT SWEEP',['off','slow','normal','fast']),
        ]
        if tid=='lcars':return [
            ('stars','STARS',['off','sparse','normal','dense']),('bands','LCARS BANDS',['off','minimal','full']),('pulse','AMBIENT PULSE',['off','soft','normal','bright']),
        ]
        if tid=='retro_crt':return [
            ('phosphor','PHOSPHOR',['green','amber','white']),('noise','NOISE',['off','low','normal','high']),('grid','GRATICULE',['off','soft','normal','dense']),('bloom','BLOOM',['off','soft','strong']),
        ]
        return []

    @staticmethod
    def _rarity_rank(name):
        order=['common','uncommon','rare','epic','legendary','mythic']
        try:return order.index(str(name).lower())
        except ValueError:return -1

    def _achievement_rows(self):
        if self.achievement_tab=='awards':
            rows=list(self.state.get('progression.awards.catalog') or [])
        else:
            rows=list(self.state.get('progression.achievements.catalog') or [])
        rows=[dict(r) for r in rows if isinstance(r,dict)]
        filt=self.achievement_filter
        if filt=='unlocked': rows=[r for r in rows if r.get('unlocked')]
        elif filt=='locked': rows=[r for r in rows if not r.get('unlocked')]
        elif filt=='near': rows=[r for r in rows if (not r.get('unlocked')) and float(r.get('progress_pct') or 0)>=50.0]
        if self.achievement_sort=='rarity' and self.achievement_tab=='achievements':
            rows.sort(key=lambda r:(-self._rarity_rank(r.get('rarity')), not bool(r.get('unlocked')), str(r.get('label',''))))
        elif self.achievement_sort=='name':
            rows.sort(key=lambda r:str(r.get('label') or '').lower())
        else:
            rows.sort(key=lambda r:(bool(r.get('unlocked')), -float(r.get('progress_pct') or 0), str(r.get('label') or '')))
        return rows

    def _achievement_page_count(self):
        return max(1,(len(self._achievement_rows())+1)//2)

    def _cycle_achievement_filter(self):
        vals=['all','unlocked','locked','near']; cur=self.achievement_filter
        self.achievement_filter=vals[(vals.index(cur)+1)%len(vals)] if cur in vals else vals[0]
        self.achievement_offset=0; self.achievement_detail=None; self.dirty.set()

    def _cycle_achievement_sort(self):
        vals=['progress','rarity','name'] if self.achievement_tab=='achievements' else ['progress','name']
        cur=self.achievement_sort
        self.achievement_sort=vals[(vals.index(cur)+1)%len(vals)] if cur in vals else vals[0]
        self.achievement_offset=0; self.achievement_detail=None; self.dirty.set()

    def renderer_for(self,page_id):
        choices=self.RENDERER_CHOICES.get(str(page_id),['bars'])
        cur=str(self.renderers.get(page_id) or choices[0])
        return cur if cur in choices else choices[0]

    def cycle_renderer(self,page_id,delta=1):
        page_id=str(page_id); choices=self.RENDERER_CHOICES.get(page_id)
        if not choices:return
        cur=self.renderer_for(page_id)
        try:idx=choices.index(cur)
        except ValueError:idx=0
        nxt=choices[(idx+int(delta))%len(choices)]
        self.renderers[page_id]=nxt; self._save_prefs(); self.button_flash=f'renderer:{page_id}:{nxt}'; self.button_flash_at=time.monotonic(); self.dirty.set()

    def _change_page(self,delta,wrap=True):
        if not delta:return
        old=self.page; new=(old+int(delta))%len(self.pages.IDS) if wrap else max(0,min(len(self.pages.IDS)-1,old+int(delta)))
        if old==new:return
        self.page=new
        if self.pages.IDS[self.page] != 'dashboard':self.active_board_id=''
        self.transition={'old':old,'new':new,'direction':1 if delta>0 else -1,'started':time.monotonic(),'duration':0.24}; self.dirty.set()

    def _theme_hit(self,x,y):
        if not (62<=y<=178): return None
        col=0 if x<240 else 1; row=max(0,min(2,(y-62)//39)); idx=int(row)*2+col
        return self.THEMES[idx] if 0<=idx<len(self.THEMES) else None

    def on_input(self,kind,e):
        self.last_input=(kind,dict(e)); self.last_input_at=time.monotonic(); log.info('input kind=%s data=%s',kind,e)
        if kind in {'touch_down','drag'}: self.touching=True; self.dirty.set(); return
        if kind=='touch_up': self.touching=False; self.dirty.set(); return

        if kind=='tap' and reveal_active(self.state,dismissed_id=self.monster_reveal_dismissed_id):
            self.monster_reveal_dismissed_id=str(self.state.get('roster.monster_reveal.id') or '')
            self.dirty.set();return

        # Rare moments sit above every normal UI layer. A deliberate tap while
        # the cinematic is active is the only acknowledgement used for the
        # corresponding hidden achievement.
        if kind=='tap' and self.state.get('rare.moment.active'):
            if self.state.get('rare.preview.active'):
                self.button_flash='rare:preview'; self.button_flash_at=time.monotonic(); self.dirty.set(); return
            if acknowledge_rare_event(self.state):
                self.button_flash='rare:witnessed'; self.button_flash_at=time.monotonic(); self.dirty.set()
            return

        # Native Pwnagotchi profiles intentionally behave like the stock screen.
        # Beast Core, input monitoring and rare-event services remain alive, but
        # ordinary taps/swipes do not pretend the stock Pwnagotchi UI is touch-
        # aware. Long-press (or a downward vertical swipe) opens Beast controls.
        if self._native_idle():
            if kind=='long_press':
                self.drawer=True; self.dirty.set(); return
            if kind=='swipe' and e.get('axis')=='y' and e.get('dy',0)>30:
                self.drawer=True; self.dirty.set(); return
            if kind in {'tap','swipe'}:
                return

        if kind=='swipe':
            if self.app_launcher:
                axis=e.get('axis')
                if axis=='y':
                    rows=self._apps_current();step=self.APP_PAGE_SIZE if e.get('dy',0)<0 else -self.APP_PAGE_SIZE;maxoff=max(0,((len(rows)-1)//self.APP_PAGE_SIZE)*self.APP_PAGE_SIZE)
                    self.app_offset=max(0,min(maxoff,self.app_offset+step));self.dirty.set()
                elif axis=='x':
                    cats=self._app_categories();delta=1 if e.get('dx',0)<0 else -1;self.app_category_idx=(self.app_category_idx+delta)%len(cats);self.app_offset=0;self.dirty.set()
                return
            if self.capsule_share_overlay:
                if e.get('axis')=='x':
                    frames=((self.capsule_share.get('qr') or {}).get('frames') or []) if isinstance(self.capsule_share,dict) else []
                    if frames:
                        delta=1 if e.get('dx',0)<0 else -1
                        self.capsule_frame_idx=(self.capsule_frame_idx+delta)%len(frames)
                        self.dirty.set()
                elif e.get('axis')=='y' and e.get('dy',0)>30:
                    self.capsule_share_overlay=False;self.app_launcher=True;self.dirty.set()
                return
            if self.telemetry_overlay:
                if e.get('axis')=='y':
                    rows=list((self.aux.get('telemetry') or []));step=4 if e.get('dy',0)<0 else -4;maxoff=max(0,((len(rows)-1)//4)*4)
                    self.telemetry_offset=max(0,min(maxoff,self.telemetry_offset+step));self.dirty.set()
                return
            if self.widget_inspector_overlay or self.correlation_overlay:
                return
            if self.plugins_overlay:
                if e.get('axis')=='y':
                    rows=list(self.state.get('plugins.catalog') or []);step=3 if e.get('dy',0)<0 else -3;maxoff=max(0,((len(rows)-1)//3)*3)
                    self.plugins_offset=max(0,min(maxoff,self.plugins_offset+step));self.dirty.set()
                return
            if self.beastdex_overlay:
                if self.beastdex_detail is not None:
                    if e.get('axis')=='y' and e.get('dy',0)>30:self.beastdex_detail=None;self.dirty.set()
                elif e.get('axis')=='y':
                    rows=list(self.state.get('records.encounters.recent') or []);step=3 if e.get('dy',0)<0 else -3;maxoff=max(0,((len(rows)-1)//3)*3)
                    self.beastdex_offset=max(0,min(maxoff,self.beastdex_offset+step));self.dirty.set()
                return
            if self.capture_vault_overlay:
                if self.capture_vault_detail is not None:
                    if e.get('axis')=='y' and e.get('dy',0)>30:self.capture_vault_detail=None;self.dirty.set()
                elif e.get('axis')=='y':
                    rows=list(self.state.get('captures.recent') or []);step=3 if e.get('dy',0)<0 else -3;maxoff=max(0,((len(rows)-1)//3)*3)
                    self.capture_vault_offset=max(0,min(maxoff,self.capture_vault_offset+step));self.dirty.set()
                return
            if self.performance_overlay:
                if e.get('axis')=='y':
                    rows=list(self.state.get('performance.processes') or []);step=3 if e.get('dy',0)<0 else -3;maxoff=max(0,((len(rows)-1)//3)*3)
                    self.performance_offset=max(0,min(maxoff,self.performance_offset+step));self.dirty.set()
                return
            if self.platform_overlay:
                if e.get('axis')=='y' and self.platform_overlay not in {'topology','operations'}:
                    rows=self._platform_rows(self.platform_overlay);step=self.PLATFORM_PAGE_SIZE if e.get('dy',0)<0 else -self.PLATFORM_PAGE_SIZE;maxoff=max(0,((len(rows)-1)//self.PLATFORM_PAGE_SIZE)*self.PLATFORM_PAGE_SIZE)
                    self.platform_offset=max(0,min(maxoff,self.platform_offset+step));self.dirty.set()
                return
            if self.studio_overlay:
                if e.get('axis')=='y' and e.get('dy',0)>30:self.studio_overlay=False;self.app_launcher=True;self.dirty.set()
                return
            if self.theme_library:
                if e.get('axis')=='y':
                    step=2 if e.get('dy',0)<0 else -2
                    maxoff=max(0,((len(self.THEMES)-1)//2)*2)
                    self.theme_library_offset=max(0,min(maxoff,self.theme_library_offset+step)); self.dirty.set(); return
            if self.visualizer_overlay:
                if e.get('axis')=='y':
                    step=2 if e.get('dy',0)<0 else -2
                    maxoff=max(0,((len(self.RENDERER_CHOICES)-1)//2)*2)
                    self.visualizer_offset=max(0,min(maxoff,self.visualizer_offset+step));self.dirty.set()
                return
            if self.achievements_overlay:
                if self.achievement_detail:
                    if e.get('axis')=='y' and e.get('dy',0)>30:self.achievement_detail=None
                elif e.get('axis')=='y':
                    pages=self._achievement_page_count()
                    if e.get('dy',0)<-30:self.achievement_offset=min(max(0,(pages-1)*2),self.achievement_offset+2)
                    elif e.get('dy',0)>30:self.achievement_offset=max(0,self.achievement_offset-2)
                self.dirty.set(); return
            if self.help_overlay:
                if e.get('axis')=='y' and e.get('dy',0)<-30:self.help_overlay=False
            elif self.theme_detail:
                if e.get('axis')=='y' and e.get('dy',0)<-30:self._cancel_theme_detail()
            elif e.get('axis')=='x' and not self.drawer:self._change_page(int(e.get('delta',0)),wrap=False)
            elif e.get('axis')=='y' and e.get('dy',0)>30:self.drawer=True
            elif e.get('axis')=='y' and e.get('dy',0)<-30:self.app_launcher=True;self.app_offset=0;self.drawer=False
        elif kind=='tap':
            x,y=int(e.get('x',0)),int(e.get('y',0))
            if self.app_launcher:
                if self.APP_CAT_PREV[0]<=x<=self.APP_CAT_PREV[2] and self.APP_CAT_PREV[1]<=y<=self.APP_CAT_PREV[3]:
                    cats=self._app_categories();self.app_category_idx=(self.app_category_idx-1)%len(cats);self.app_offset=0;self.dirty.set()
                elif self.APP_CAT_NEXT[0]<=x<=self.APP_CAT_NEXT[2] and self.APP_CAT_NEXT[1]<=y<=self.APP_CAT_NEXT[3]:
                    cats=self._app_categories();self.app_category_idx=(self.app_category_idx+1)%len(cats);self.app_offset=0;self.dirty.set()
                else:
                    rows=self._apps_current();cards=rows[self.app_offset:self.app_offset+self.APP_PAGE_SIZE]
                    opened=False
                    for app,box in zip(cards,self.APP_CARD_BOXES):
                        if box[0]<=x<=box[2] and box[1]<=y<=box[3]:
                            self._open_app(app.id);opened=True;break
                    if not opened and 224<=y<=277:
                        maxoff=max(0,((len(rows)-1)//self.APP_PAGE_SIZE)*self.APP_PAGE_SIZE)
                        if x<155:self.app_offset=max(0,self.app_offset-self.APP_PAGE_SIZE);self.dirty.set()
                        elif x>324:self.app_offset=min(maxoff,self.app_offset+self.APP_PAGE_SIZE);self.dirty.set()
                        else:self.app_launcher=False;self.dirty.set()
            elif self.capsule_share_overlay:
                frames=((self.capsule_share.get('qr') or {}).get('frames') or []) if isinstance(self.capsule_share,dict) else []
                if hit('capsule-prev',self.CAPSULE_PREV,x,y,minimum=48):
                    if frames:self.capsule_frame_idx=(self.capsule_frame_idx-1)%len(frames)
                    self.dirty.set()
                elif hit('capsule-next',self.CAPSULE_NEXT,x,y,minimum=48):
                    if frames:self.capsule_frame_idx=(self.capsule_frame_idx+1)%len(frames)
                    self.dirty.set()
                elif hit('capsule-close',self.CAPSULE_CLOSE,x,y,minimum=48):
                    self.capsule_share_overlay=False;self.app_launcher=True;self.dirty.set()
            elif self.telemetry_overlay:
                if 238<=y<=277:
                    rows=list(self.aux.get('telemetry') or []);maxoff=max(0,((len(rows)-1)//4)*4)
                    if x<155:self.telemetry_offset=max(0,self.telemetry_offset-4);self.dirty.set()
                    elif x>324:self.telemetry_offset=min(maxoff,self.telemetry_offset+4);self.dirty.set()
                    else:self.telemetry_overlay=False;self.app_launcher=True;self.dirty.set()
            elif self.widget_inspector_overlay:
                if 232<=y<=277:self.widget_inspector_overlay=False;self.widget_inspector_key=None;self.dirty.set()
            elif self.correlation_overlay:
                if 232<=y<=277:self.correlation_overlay=False;self.app_launcher=True;self.dirty.set()
            elif self.plugins_overlay:
                if 238<=y<=277:
                    rows=list(self.state.get('plugins.catalog') or []);maxoff=max(0,((len(rows)-1)//3)*3)
                    if x<155:self.plugins_offset=max(0,self.plugins_offset-3);self.dirty.set()
                    elif x>324:self.plugins_offset=min(maxoff,self.plugins_offset+3);self.dirty.set()
                    else:self.plugins_overlay=False;self.app_launcher=True;self.dirty.set()
            elif self.beastdex_overlay:
                rows=list(self.state.get('records.encounters.recent') or [])
                if self.beastdex_detail is not None:
                    if 232<=y<=277:self.beastdex_detail=None;self.dirty.set()
                elif 64<=y<222:
                    idx=self.beastdex_offset+min(2,max(0,(y-64)//52))
                    if idx<len(rows):self.beastdex_detail=idx;self.dirty.set()
                elif 238<=y<=277:
                    maxoff=max(0,((len(rows)-1)//3)*3)
                    if x<155:self.beastdex_offset=max(0,self.beastdex_offset-3);self.dirty.set()
                    elif x>324:self.beastdex_offset=min(maxoff,self.beastdex_offset+3);self.dirty.set()
                    else:self.beastdex_overlay=False;self.app_launcher=True;self.dirty.set()
            elif self.capture_vault_overlay:
                rows=list(self.state.get('captures.recent') or [])
                if self.capture_vault_detail is not None:
                    if 232<=y<=277:self.capture_vault_detail=None;self.dirty.set()
                elif 64<=y<222:
                    idx=self.capture_vault_offset+min(2,max(0,(y-64)//52))
                    if idx<len(rows):self.capture_vault_detail=idx;self.dirty.set()
                elif 238<=y<=277:
                    maxoff=max(0,((len(rows)-1)//3)*3)
                    if x<155:self.capture_vault_offset=max(0,self.capture_vault_offset-3);self.dirty.set()
                    elif x>324:self.capture_vault_offset=min(maxoff,self.capture_vault_offset+3);self.dirty.set()
                    else:self.capture_vault_overlay=False;self.app_launcher=True;self.dirty.set()
            elif self.performance_overlay:
                if 238<=y<=277:
                    rows=list(self.state.get('performance.processes') or []);maxoff=max(0,((len(rows)-1)//3)*3)
                    if x<155:self.performance_offset=max(0,self.performance_offset-3);self.dirty.set()
                    elif x>324:self.performance_offset=min(maxoff,self.performance_offset+3);self.dirty.set()
                    else:self.performance_overlay=False;self.app_launcher=True;self.dirty.set()
            elif self.platform_overlay:
                if self.platform_overlay in {'topology','operations'}:
                    if hit('platform-special-close',self.PLATFORM_SPECIAL_CLOSE,x,y,minimum=48):
                        self.platform_overlay=None;self.app_launcher=True;self.dirty.set()
                elif 224<=y<=277:
                    rows=self._platform_rows(self.platform_overlay);maxoff=max(0,((len(rows)-1)//self.PLATFORM_PAGE_SIZE)*self.PLATFORM_PAGE_SIZE)
                    if x<155:self.platform_offset=max(0,self.platform_offset-self.PLATFORM_PAGE_SIZE);self.dirty.set()
                    elif x>324:self.platform_offset=min(maxoff,self.platform_offset+self.PLATFORM_PAGE_SIZE);self.dirty.set()
                    else:self.platform_overlay=None;self.app_launcher=True;self.dirty.set()
            elif self.studio_overlay:
                if 232<=y<=277:self.studio_overlay=False;self.app_launcher=True;self.dirty.set()
            elif self.theme_detail:
                if hit('theme-cancel-top',(372,42,466,74),x,y,minimum=48):self._cancel_theme_detail()
                elif self._theme_option_rows(self.theme.id):
                    rows=self._theme_option_rows(self.theme.id); start=self.theme_detail_page*2; shown=rows[start:start+2]; ys=[106,161]
                    handled=False
                    for (key,_label,vals),ry in zip(shown,ys):
                        if hit('matrix-row',(20,ry,460,ry+51),x,y,minimum=56):
                            if hit('matrix-prev',(20,ry,132,ry+51),x,y,minimum=56):self._step_theme_option(key,vals,-1)
                            elif hit('matrix-next',(348,ry,460,ry+51),x,y,minimum=56):self._step_theme_option(key,vals,1)
                            handled=True; break
                    if not handled and 216<=y<=271:
                        pages=max(1,(len(rows)+1)//2); last=pages-1
                        if self.theme_detail_page==0:
                            if hit('detail-cancel',(18,216,228,270),x,y,minimum=56):self._cancel_theme_detail()
                            elif hit('detail-next',(244,216,458,270),x,y,minimum=56):self.theme_detail_page=min(last,1);self.dirty.set()
                        elif self.theme_detail_page<last:
                            if hit('detail-prev',(18,216,142,270),x,y,minimum=56):self.theme_detail_page-=1;self.dirty.set()
                            elif hit('detail-cancel',(152,216,286,270),x,y,minimum=56):self._cancel_theme_detail()
                            elif hit('detail-next',(296,216,458,270),x,y,minimum=56):self.theme_detail_page+=1;self.dirty.set()
                        else:
                            if hit('detail-prev',(18,216,142,270),x,y,minimum=56):self.theme_detail_page=max(0,self.theme_detail_page-1);self.dirty.set()
                            elif hit('detail-cancel',(152,216,286,270),x,y,minimum=56):self._cancel_theme_detail()
                            elif hit('detail-apply',(296,216,458,270),x,y,minimum=56):self._apply_theme_detail()
                elif hit('detail-apply',(244,216,458,270),x,y,minimum=56):self._apply_theme_detail()
                elif hit('detail-cancel',(18,216,228,270),x,y,minimum=56):self._cancel_theme_detail()
            elif self.theme_library:
                if hit('theme-card-1',(18,58,458,126),x,y,minimum=68):
                    idx=self.theme_library_offset
                    if idx<len(self.THEMES):self._open_theme_detail(self.THEMES[idx])
                elif hit('theme-card-2',(18,136,458,204),x,y,minimum=68):
                    idx=self.theme_library_offset+1
                    if idx<len(self.THEMES):self._open_theme_detail(self.THEMES[idx])
                elif 216<=y<=272:
                    maxoff=max(0,((len(self.THEMES)-1)//2)*2)
                    if hit('theme-prev',(18,216,146,271),x,y,minimum=56):self.theme_library_offset=max(0,self.theme_library_offset-2);self.dirty.set()
                    elif hit('theme-next',(334,216,462,271),x,y,minimum=56):self.theme_library_offset=min(maxoff,self.theme_library_offset+2);self.dirty.set()
                    elif hit('theme-back',(158,216,322,271),x,y,minimum=56):self.theme_library=False;self.drawer=True;self.dirty.set()
            elif self.visualizer_overlay:
                pids=list(self.RENDERER_CHOICES);shown=pids[self.visualizer_offset:self.visualizer_offset+2]
                for i,pid in enumerate(shown):
                    y1,y2=(58,142) if i==0 else (150,234)
                    if y1<=y<=y2:
                        if x<150:self.cycle_renderer(pid,-1)
                        elif x>330:self.cycle_renderer(pid,1)
                        self.dirty.set();break
                else:
                    if 240<=y<=277:
                        maxoff=max(0,((len(pids)-1)//2)*2)
                        if x<155:self.visualizer_offset=max(0,self.visualizer_offset-2);self.dirty.set()
                        elif x>324:self.visualizer_offset=min(maxoff,self.visualizer_offset+2);self.dirty.set()
                        else:self.visualizer_overlay=False;self.drawer=True;self.dirty.set()
            elif self.achievements_overlay:
                if self.achievement_detail:
                    if 232<=y<=277 and 8<=x<=471:self.achievement_detail=None;self.dirty.set()
                # Achievement Explorer uses non-overlapping physical touch
                # partitions. Expanded hitboxes were individually large, but on
                # the 3.5-inch resistive panel adjacent regions could overlap and
                # make a correct press trigger the row above it.
                elif 40<=y<=80 and 8<=x<240:
                    self.achievement_tab='achievements';self.achievement_offset=0;self.achievement_detail=None;self.dirty.set()
                elif 40<=y<=80 and 240<=x<=471:
                    self.achievement_tab='awards';self.achievement_offset=0;self.achievement_detail=None;self.dirty.set()
                elif 81<=y<=121 and 8<=x<240:self._cycle_achievement_filter()
                elif 81<=y<=121 and 240<=x<=471:self._cycle_achievement_sort()
                elif 122<=y<=180 and 8<=x<=471:
                    rows=self._achievement_rows();idx=self.achievement_offset
                    if idx<len(rows):self.achievement_detail=rows[idx].get('id');self.dirty.set()
                elif 181<=y<=239 and 8<=x<=471:
                    rows=self._achievement_rows();idx=self.achievement_offset+1
                    if idx<len(rows):self.achievement_detail=rows[idx].get('id');self.dirty.set()
                elif 240<=y<=277:
                    pages=self._achievement_page_count();maxoff=max(0,(pages-1)*2)
                    if 8<=x<=155:self.achievement_offset=max(0,self.achievement_offset-2);self.dirty.set()
                    elif 324<=x<=471:self.achievement_offset=min(maxoff,self.achievement_offset+2);self.dirty.set()
                    elif 156<=x<=323:self.achievements_overlay=False;self.drawer=True;self.achievement_detail=None;self.dirty.set()
            elif self.help_overlay:
                if hit('help-touchzones',(250,244,458,266),x,y,minimum=56):
                    self.touch_zones_overlay=not self.touch_zones_overlay; self.help_overlay=False
                elif hit('help-close',(0,244,238,277),x,y,minimum=56):self.help_overlay=False
            elif self.drawer:
                if self.CONTROL_APP_BOX[0]<=x<=self.CONTROL_APP_BOX[2] and self.CONTROL_APP_BOX[1]<=y<=self.CONTROL_APP_BOX[3]:
                    self.app_launcher=True;self.app_offset=0;self.drawer=False;self.dirty.set()
                else:
                    opened=False
                    for idx,box in enumerate(self.CONTROL_QUICK_BOXES):
                        if box[0]<=x<=box[2] and box[1]<=y<=box[3]:
                            if idx==0:self.theme_library=True;self.drawer=False
                            elif idx==1:self.visualizer_overlay=True;self.visualizer_offset=0;self.drawer=False
                            elif idx==2:self.achievements_overlay=True;self.drawer=False
                            elif idx==3:self.help_overlay=True;self.drawer=False
                            opened=True;break
                    if opened:self.dirty.set()
            else:
                _pid=self.pages.IDS[self.page]
                if _pid=='recon' and hit('recon-main',(8,58,252,244),x,y,minimum=72):self.cycle_renderer('recon')
                elif _pid=='spectrum' and hit('spectrum-main',(8,42,472,190),x,y,minimum=72):self.cycle_renderer('spectrum')
                elif _pid=='captures' and hit('captures-main',(8,110,472,244),x,y,minimum=72):self.cycle_renderer('captures')
                elif _pid=='system' and hit('system-history',(294,104,476,244),x,y,minimum=72):self.cycle_renderer('system')
                elif hit('footer-prev',(0,250,122,319),x,y,minimum=72):self.button_flash='prev'; self.button_flash_at=time.monotonic(); self._change_page(-1)
                elif hit('footer-next',(358,250,479,319),x,y,minimum=72):self.button_flash='next'; self.button_flash_at=time.monotonic(); self._change_page(1)
                elif hit('footer-home',(122,274,358,319),x,y,minimum=56):
                    self.button_flash='home'; self.button_flash_at=time.monotonic()
                    if self.page!=0:self._change_page(-self.page)
                    else:self.app_launcher=True;self.app_offset=0;self.dirty.set()
        elif kind=='long_press':
            if self.app_launcher:self.app_launcher=False
            elif self.telemetry_overlay:self.telemetry_overlay=False;self.app_launcher=True
            elif self.widget_inspector_overlay:self.widget_inspector_overlay=False;self.widget_inspector_key=None
            elif self.correlation_overlay:self.correlation_overlay=False;self.app_launcher=True
            elif self.plugins_overlay:self.plugins_overlay=False;self.app_launcher=True
            elif self.beastdex_overlay:
                if self.beastdex_detail is not None:self.beastdex_detail=None
                else:self.beastdex_overlay=False;self.app_launcher=True
            elif self.capture_vault_overlay:
                if self.capture_vault_detail is not None:self.capture_vault_detail=None
                else:self.capture_vault_overlay=False;self.app_launcher=True
            elif self.performance_overlay:self.performance_overlay=False;self.app_launcher=True
            elif self.platform_overlay:self.platform_overlay=None;self.app_launcher=True
            elif self.studio_overlay:self.studio_overlay=False;self.app_launcher=True
            elif self.theme_detail:self._cancel_theme_detail()
            elif self.theme_library:self.theme_library=False;self.drawer=True
            elif self.visualizer_overlay:self.visualizer_overlay=False;self.drawer=True
            elif self.achievements_overlay:
                if self.achievement_detail:self.achievement_detail=None
                else:self.achievements_overlay=False;self.drawer=True
            elif self.help_overlay:self.help_overlay=False
            else:
                x,y=int(e.get('x',0)),int(e.get('y',0));_pid=self.pages.IDS[self.page];key=self._widget_key_at(_pid,x,y)
                if key:self.widget_inspector_key=key;self.widget_inspector_overlay=True;self.drawer=False
                else:self.drawer=not self.drawer
        self.dirty.set()

    def _apply_rare_preview(self):
        try:
            obj=json.loads(self.rare_preview_path.read_text())
            if float(obj.get('expires') or 0) <= time.time():
                try:self.rare_preview_path.unlink()
                except Exception:pass
                return
            mode=str(obj.get('mode') or '')
            if mode not in {'omen','moment'}:return
            self.state['rare.preview.active']=True
            self.state['rare.omen.active']=mode=='omen'
            self.state['rare.moment.active']=mode=='moment'
            self.state['rare.moment.id']='preview'
            self.state['rare.moment.rarity']=str(obj.get('rarity') or 'legendary')
            self.state['rare.moment.sigil']=str(obj.get('sigil') or 'eye')
            self.state['rare.moment.presentation']=str(obj.get('presentation') or 'drift')
            self.state['rare.moment.remaining_sec']=max(0,int(float(obj.get('expires'))-time.time()))
        except Exception:
            self.state.pop('rare.preview.active',None)

    def _sync_feed(self):
        if not self.feed:return
        st,ev,hist,aux,err=self.feed.snapshot()
        if st:
            self.state=st
            content_pack_sig=tuple(sorted((str(r.get('id') or ''),str(r.get('pack_type') or ''),bool(r.get('enabled')),str(r.get('version') or '')) for r in (st.get('packs.items') or []) if isinstance(r,dict) and str(r.get('pack_type') or '') in {'theme','face','animation','board','layout'}))
            if content_pack_sig!=getattr(self,'_content_pack_sig',None):
                self._content_pack_sig=content_pack_sig
                self._refresh_theme_catalog();self.face.refresh_profiles();self.face.refresh_animation_profiles();self.face.set_profile(self.face_profile_pref);self.face.set_animation_profile(self.animation_profile_pref);self.pack_boards=discover_enabled_pack_boards();self.apps=self._build_app_registry()
                if self.active_board_id and self.active_board_id not in {str(b.get('id')) for b in self._all_boards()}:self.active_board_id=''
            sig=(bool(st.get('containers.runtime.available')),bool(st.get('capabilities.rtlsdr.present')),int(st.get('display.connected_outputs') or 0))
            if sig!=self._capability_app_sig:
                self._capability_app_sig=sig;self.apps=self._build_app_registry()
        self.events=ev
        self.histories=hist
        self.aux=aux
        self.data_error=err
        self._apply_rare_preview()

    def adaptive_fps(self):
        try:cpu=float(self.state.get('system.cpu.total') or 0)
        except Exception:cpu=0
        thermal=str(self.state.get('system.thermal.band') or 'normal')
        motion=getattr(self.theme,'motion','normal')
        try:gov_cap=float(self.state.get('governor.ui.fps_cap') or 99)
        except Exception:gov_cap=99.0
        if thermal=='critical':target=2.0
        elif thermal=='hot':target=4.0
        elif self.touching or self.transition or time.monotonic()-self.last_input_at<.7:
            target=7.0 if cpu>=90 else 10.0 if cpu>=80 else 18.0
        else:
            base={'low':7.0,'normal':10.0,'high':14.0}.get(motion,10.0)
            target=2.0 if cpu>=90 else min(5.0,base) if cpu>=80 else min(7.0,base) if cpu>=70 else base
        return max(1.0,min(target,gov_cap))

    def _dynamic_frame_due(self,now=None):
        """Return True only when a visual layer genuinely needs another frame.

        Live telemetry dirties the UI independently. This prevents a static page
        from being fully recomposed 7-18 times/sec merely because the render
        budget *allows* it, which saves substantial Pi CPU/heat without making
        touch, transitions or ambient themes less responsive.
        """
        now=time.monotonic() if now is None else float(now)
        if self.transition:return True
        if self.state.get('rare.omen.active') or self.state.get('rare.moment.active'):return True
        mr=reveal_active(self.state,dismissed_id=self.monster_reveal_dismissed_id)
        if mr:self._monster_reveal_was_active=True;return True
        if self._monster_reveal_was_active:self._monster_reveal_was_active=False;return True
        if self.button_flash:
            age=now-self.button_flash_at
            if age<.30:return True
            self.button_flash=None
            return True  # one cleanup frame removes the highlight
        opts=self.render_options_for_theme(self.theme.id);fps=self._background_cadence(opts)
        if fps>0:
            return self._bg_cache is None or now-self._bg_cache_at>=1.0/max(.1,fps)
        return False

    def _header(self,d,title):
        t=self.theme; f=self.fonts
        d.rectangle((0,0,self.W,self.HEADER_H),fill=t.c('ink'))
        style=str(getattr(t,'geometry','classic'))
        if style in {'terminal'}:
            d.rectangle((2,2,self.W-3,self.HEADER_H-3),outline=t.c('edge'))
        else:
            d.line((0,self.HEADER_H-1,self.W,self.HEADER_H-1),fill=t.c('edge'))

        if t.id in {'pwn_dark','pwn_light','pwn_chroma'}:
            brand='PWNAGOTCHI'
            d.text((TOKENS.space_s,7),brand,font=f['title'],fill=t.c('primary'))
            title_x=142
        elif style=='lcars':
            d.rounded_rectangle((4,4,94,29),radius=TOKENS.radius_l,fill=t.c('secondary'))
            d.text((13,8),'BEAST',font=f['medium'],fill=t.c('ink'))
            d.rounded_rectangle((99,4,122,29),radius=TOKENS.radius_s,fill=t.c('accent'))
            title_x=132
        else:
            # Full product identity matters on a 480x320 appliance.  The old
            # short "BEAST" label made every theme look like the same debug UI.
            d.text((8,7),'BEAST',font=f['title'],fill=t.c('primary'))
            bw=d.textbbox((0,0),'BEAST',font=f['title'])[2]
            d.text((10+bw,7),'AGOTCHI',font=f['title'],fill=t.c('secondary'))
            title_x=min(182,18+bw+d.textbbox((0,0),'AGOTCHI',font=f['title'])[2])

        page_label='HOME' if str(title).upper()=='BEAST CORE' else str(title).upper()[:16]
        d.text((title_x,11),page_label,font=f['tiny'],fill=t.c('dim'))
        level=self.state.get('progression.level')
        if isinstance(level,(int,float)):
            d.text((302,10),f'LV {int(level):02d}',font=f['tiny'],fill=t.c('secondary'))
        d.text((352,10),f"CH {self.state.get('radio.primary.channel','--')}",font=f['tiny'],fill=t.c('info'))

        if self.state.get('dock.docked'):
            right='DOCK'; col=t.c('accent')
        elif self.state.get('power.telemetry.available'):
            pct=self.state.get('power.battery.percent_estimate')
            right=f"BAT {pct:.0f}%" if isinstance(pct,(int,float)) else 'BAT'
            col=t.c('accent')
        else:
            health=str(self.state.get('health.core.state','--')).upper()
            right=health[:7]
            col=t.c('accent') if health=='HEALTHY' else t.c('warn')
        tw=d.textbbox((0,0),right,font=f['tiny'])[2]
        d.text((472-tw,10),right,font=f['tiny'],fill=col)

    def _footer(self,d,idx=None):
        t=self.theme;f=self.fonts;idx=self.page if idx is None else idx;count=len(self.pages.IDS)
        cur_id=self.pages.IDS[idx];name=self.pages.TITLES[cur_id]
        if cur_id=='dashboard' and self.active_board_id:
            name=next((str(b.get('label') or b.get('id')) for b in self._all_boards() if str(b.get('id'))==self.active_board_id),name)
        prev_name=self.pages.TITLES[self.pages.IDS[max(0,idx-1)]] if idx>0 else ''
        next_name=self.pages.TITLES[self.pages.IDS[min(count-1,idx+1)]] if idx<count-1 else ''
        flash=self.button_flash if time.monotonic()-self.button_flash_at<TOKENS.motion_notice_s else None
        style=str(getattr(t,'footer_style','classic'))

        d.rectangle((0,self.FOOTER_Y,self.W,self.H),fill=t.c('ink'))
        d.line((0,self.FOOTER_Y,self.W,self.FOOTER_Y),fill=t.c('edge'))
        left_col=t.c('accent') if flash=='prev' else t.c('primary')
        right_col=t.c('accent') if flash=='next' else t.c('primary')

        if style=='terminal':
            d.rectangle((6,284,112,314),outline=left_col)
            d.rectangle((368,284,474,314),outline=right_col)
            d.text((15,290),'<<',font=f['small'],fill=left_col)
            d.text((392,290),'>>',font=f['small'],fill=right_col)
            if prev_name:d.text((38,292),prev_name[:9],font=f['micro'],fill=t.c('dim'))
            if next_name:d.text((432,292),next_name[:9],font=f['micro'],fill=t.c('dim'),anchor='ra')
        elif style in {'angular','cut'}:
            lf=t.c('panel2') if flash!='prev' else t.c('accent');rf=t.c('panel2') if flash!='next' else t.c('accent')
            d.polygon([(6,284),(101,284),(112,294),(112,314),(6,314)],fill=lf,outline=left_col)
            d.polygon([(368,294),(379,284),(474,284),(474,314),(368,314)],fill=rf,outline=right_col)
            d.text((15,290),'‹',font=f['medium'],fill=left_col if flash!='prev' else t.c('ink'))
            d.text((452,290),'›',font=f['medium'],fill=right_col if flash!='next' else t.c('ink'))
            if prev_name:d.text((34,292),prev_name[:9],font=f['micro'],fill=t.c('dim'))
            if next_name:
                tw=d.textbbox((0,0),next_name[:9],font=f['micro'])[2];d.text((448-tw,292),next_name[:9],font=f['micro'],fill=t.c('dim'))
        elif style=='segments':
            d.rounded_rectangle((5,283,116,315),radius=10,fill=t.c('secondary'))
            d.rounded_rectangle((364,283,475,315),radius=10,fill=t.c('primary'))
            d.text((16,290),'‹',font=f['medium'],fill=t.c('ink'));d.text((451,290),'›',font=f['medium'],fill=t.c('ink'))
            if prev_name:d.text((34,292),prev_name[:9],font=f['micro'],fill=t.c('ink'))
            if next_name:
                tw=d.textbbox((0,0),next_name[:9],font=f['micro'])[2];d.text((448-tw,292),next_name[:9],font=f['micro'],fill=t.c('ink'))
        else:
            # Flatter cockpit rail: same proven hit boxes, much less dashboard-card bulk.
            d.line((6,314,112,314),fill=left_col,width=2);d.line((368,314,474,314),fill=right_col,width=2)
            d.text((13,288),'‹',font=f['medium'],fill=left_col);d.text((454,288),'›',font=f['medium'],fill=right_col)
            if prev_name:d.text((30,292),prev_name[:10],font=f['micro'],fill=t.c('dim'))
            if next_name:
                tw=d.textbbox((0,0),next_name[:10],font=f['micro'])[2];d.text((450-tw,292),next_name[:10],font=f['micro'],fill=t.c('dim'))

        center_col=t.c('accent') if flash=='home' else t.c('text')
        center_name='HOME' if cur_id=='home' else name
        tw=d.textbbox((0,0),center_name,font=f['small'])[2]
        d.text((240-tw//2,285),center_name,font=f['small'],fill=center_col)
        index=f'{idx+1} / {count}';iw=d.textbbox((0,0),index,font=f['micro'])[2]
        d.text((240-iw//2,299),index,font=f['micro'],fill=t.c('dim'))
        total=(count-1)*7+13;x=240-total//2
        for i in range(count):
            w=13 if i==idx else 5
            d.rounded_rectangle((x,309,x+w,313),radius=2,fill=t.c('accent') if i==idx else t.c('edge'));x+=w+2

        if flash and str(flash).startswith('renderer:'):
            label=str(flash).split(':')[-1].upper()[:18]
            d.rounded_rectangle((132,281,348,302),radius=TOKENS.radius_s,fill=t.c('panel2'),outline=t.c('accent'))
            tw=d.textbbox((0,0),label,font=f['small'])[2]
            d.text((240-tw//2,287),label,font=f['small'],fill=t.c('accent'))

    @staticmethod
    def _reaction_label(ev):
        typ=str(ev.get('type') or ''); data=ev.get('data') if isinstance(ev.get('data'),dict) else {}
        if typ=='progression.level_up':return f"LEVEL UP // {data.get('to','?')} {str(data.get('stage','')).upper()}"
        if typ=='progression.stage_changed':return f"EVOLUTION // {str(data.get('to','')).upper()}"
        if typ=='progression.vendor_discovered':return f"NEW SPECIES // +{data.get('count',1)} VENDOR"
        if typ=='progression.achievement_unlocked':return f"ACHIEVEMENT // {str(data.get('label','UNLOCKED')).upper()}"
        if typ=='pwnagotchi.handshake':return 'CAPTURE STORED'
        if typ=='gps.lock_acquired':return 'GPS LOCK ACQUIRED'
        if typ=='wifi.ap_discovered':return f"NEW SIGNALS // +{data.get('count',1)}"
        if typ=='context.mode_changed':return f"MODE // {str(data.get('to','')).upper()}"
        if typ=='dock.changed':return 'DOCK STATE CHANGED'
        if typ=='system.thermal_band':return f"THERMAL // {str(data.get('to','')).upper()}"
        if typ=='system.health_changed':return f"SYSTEM // {str(data.get('to','')).upper()}"
        if typ=='collector.error':return 'COLLECTOR FAULT'
        return typ.upper()

    def _event_reaction(self,d):
        picked=self.reactions.select(self.events)
        if not picked:return
        ev=picked['event']; p=picked['progress']; typ=str(ev.get('type','')); t=self.theme; style=t.reaction_style
        severe=picked['priority']>=90; col=t.c('danger') if severe else t.c('accent') if typ!='context.mode_changed' else t.c('secondary')
        if style in {'pulse','soft'}:
            inset=int((1-p)*22);d.rectangle((inset,34+inset,479-inset,277-inset),outline=col,width=2)
        elif style=='glitch':
            # Matrix reactions use localized VERTICAL data pulses only.
            # v0.9.4's reaction bars advanced X and Y together. On the physical
            # TFT that read as a temporary pink/magenta diagonal sweep and was
            # easily mistaken for broken Matrix rain. Keep reaction geometry on
            # fixed X coordinates; animate only height/intensity.
            if str(self.options_for_theme('matrix').get('reactions_enabled','on')).lower() == 'off':
                return
            tick=int(self.phase*11)
            fixed_x=(28,86,151,219,288,354,417,462)
            for i,x in enumerate(fixed_x):
                y=54 + ((i*31) % 166)
                h=7 + ((i*9 + tick) % 18)
                # One-pixel vertical data pulse: never translates sideways.
                d.line((x,y,x,min(274,y+h)),fill=col,width=1 if i%3 else 2)
            # Severe events use stationary danger corner brackets rather than a
            # moving field. This keeps thermal/fault visibility without
            # producing a second moving visual language on Matrix.
            if severe:
                d.line((6,38,6,62,18,62),fill=col,width=2)
                d.line((473,250,473,274,461,274),fill=col,width=2)
            else:
                off=6
                d.line((off,38,off,55),fill=col,width=1)
                d.line((479-off,257,479-off,274),fill=col,width=1)
        elif style=='sweep':
            # Starcore event reaction: segmented perimeter chase, not a vertical scan bar.
            q=int((self.phase*7)%4)
            segs=[(18,36,122,36),(358,36,462,36),(18,275,122,275),(358,275,462,275)]
            for i,(x1,y1,x2,y2) in enumerate(segs):
                if i==q:
                    d.line((x1,y1,x2,y2),fill=col,width=3)
                else:
                    d.line((x1,y1,x2,y2),fill=t.c('edge'),width=1)
        elif style=='crack':
            for x in (60,170,310,420):d.line((x,34,x-12,90,x+8,140,x-18,210,x+5,277),fill=col,width=1)
        elif style=='ember':
            for i in range(24):
                x=(i*29+int(self.phase*63))%480;y=260-((i*17+int(self.phase*41))%190);d.ellipse((x,y,x+1,y+2),fill=col)
        # Small event banner is deliberately theme-neutral/readable.
        label=self._reaction_label(ev)[:48]
        w=min(420,max(160,14+len(label)*6));x=(480-w)//2
        d.rectangle((x,38,x+w,54),fill=t.c('ink'),outline=col)
        d.text((x+7,42),label,font=self.fonts['tiny'],fill=col)

    def _physical_test_overlay(self,d):
        if not self.test_mode_path.exists():return
        t=self.theme;f=self.fonts;d.rectangle((0,34,480,49),fill=t.c('panel2'));d.text((6,37),f'PHYS TEST // Beastagotchi {UI_VERSION} Physical Acceptance',font=f['tiny'],fill=t.c('warn'))
        if self.last_input and time.monotonic()-self.last_input_at<4:
            kind,e=self.last_input;x=int(e.get('x',240));y=int(e.get('y',160));d.line((max(0,x-10),y,min(479,x+10),y),fill=t.c('accent'),width=2);d.line((x,max(34,y-10),x,min(277,y+10)),fill=t.c('accent'),width=2)

    def _drawer(self,d):
        if not self.drawer:return
        t=self.theme;f=self.fonts
        d.rectangle((0,34,480,278),fill=t.c('ink'))
        panel(d,(8,38,472,274),t,accent=t.c('secondary'),width=2)

        d.text((18,48),'BEAST CONTROL CENTER',font=f['medium'],fill=t.c('secondary'))
        beast_name=str(self.state.get('progression.beast.name') or 'BEAST').strip() or 'BEAST'
        beast_level=self.state.get('progression.level')
        beast_stage=str(self.state.get('progression.stage') or '').upper()
        identity=f'{beast_name[:16]}'
        if isinstance(beast_level,(int,float)):
            identity+=f' · LV {int(beast_level):02d}'
        if beast_stage:
            identity+=f' {beast_stage[:10]}'
        d.text((18,67),identity,font=f['tiny'],fill=t.c('accent'))
        d.text((18,78),f'{self.theme.label[:22]} · {str(self.state.get("context.mode.effective") or "pwn").upper()[:10]}',font=f['micro'],fill=t.c('dim'))

        box=self.CONTROL_APP_BOX
        d.rounded_rectangle(box,radius=7,fill=t.c('panel2'),outline=t.c('accent'),width=2)
        d.text((385,57),'APPS',font=f['small'],fill=t.c('accent'))

        rows=[
            ('THEME LIBRARY','Identity, palette, motion',t.c('primary')),
            ('VISUALIZER STUDIO','Graphs + renderers',t.c('info')),
            ('ACHIEVEMENTS','Progress, awards, rarity',t.c('accent')),
            ('CONTROLS / HELP','Gestures + touch debug',t.c('warn')),
        ]
        for box,(title,sub,col) in zip(self.CONTROL_QUICK_BOXES,rows):
            x1,y1,x2,y2=box
            d.rounded_rectangle(box,radius=8,fill=t.c('panel2'),outline=col,width=2)
            d.text((x1+12,y1+14),title,font=f['small'],fill=col)
            d.text((x1+12,y1+36),sub[:29],font=f['tiny'],fill=t.c('text'))
            d.text((x1+12,y2-16),'OPEN',font=f['micro'],fill=t.c('dim'))

    def _deck_category_map(self):
        rows=list(getattr(self,'context_decks',[]) or [])
        if getattr(self,'active_context_deck',''):
            rows.sort(key=lambda d:(0 if d.get('id')==self.active_context_deck else 1,str(d.get('label') or d.get('id'))))
        return {f"★ {str(d.get('label') or d.get('id')).upper()}":d for d in rows}

    def _app_categories(self):
        return ['ALL']+list(self._deck_category_map())+self.apps.categories()

    def _apps_current(self):
        cats=self._app_categories();idx=max(0,min(len(cats)-1,int(self.app_category_idx)));cat=cats[idx]
        deck=self._deck_category_map().get(cat)
        return self.apps.by_ids(deck.get('apps') or []) if deck else self.apps.by_category(cat)

    def _load_capsule_share(self):
        """Fetch a fresh real Lineage Capsule without blocking the render loop."""
        if self.capsule_loading:return
        self.capsule_loading=True
        self.capsule_share={"loading":True}
        self.capsule_frame_idx=0
        self.dirty.set()
        def worker():
            try:
                api=getattr(getattr(self,'feed',None),'api',None)
                if api is None:
                    row={"ok":False,"error":"Beast Core Capsule API is unavailable"}
                else:
                    row=api.capsule_export(qr_chars=220)
                    if not isinstance(row,dict) or not row:
                        row={"ok":False,"error":"Capsule export returned no data"}
                self.capsule_share=row
                self.capsule_frame_idx=0
            except Exception as exc:
                self.capsule_share={"ok":False,"error":f"{type(exc).__name__}: {exc}"}
            finally:
                self.capsule_loading=False
                self.dirty.set()
        threading.Thread(target=worker,name='beastui-capsule-export',daemon=True).start()

    def _open_app(self,app_id):
        app=self.apps.get(app_id)
        if app is None:return
        self.app_launcher=False
        if app.kind=='page' and app.target in self.pages.IDS:
            self.active_board_id=''
            idx=self.pages.IDS.index(app.target)
            if idx!=self.page:self._change_page(idx-self.page,wrap=False)
        elif app.kind=='board':
            self.active_board_id=str(app.target)
            idx=self.pages.IDS.index('dashboard')
            if idx!=self.page:self._change_page(idx-self.page,wrap=False)
        elif app.target=='theme_library':self.theme_library=True
        elif app.target=='visualizer':self.visualizer_overlay=True;self.visualizer_offset=0
        elif app.target=='achievements':self.achievements_overlay=True
        elif app.target=='telemetry':self.telemetry_overlay=True;self.telemetry_offset=0
        elif app.target=='correlation':self.correlation_overlay=True
        elif app.target=='plugins':self.plugins_overlay=True;self.plugins_offset=0
        elif app.target=='beastdex':self.beastdex_overlay=True;self.beastdex_offset=0;self.beastdex_detail=None
        elif app.target=='capture_vault':self.capture_vault_overlay=True;self.capture_vault_offset=0;self.capture_vault_detail=None
        elif app.target=='performance':self.performance_overlay=True;self.performance_offset=0
        elif app.target=='capsule_share':
            self.capsule_share_overlay=True;self.capsule_frame_idx=0;self._load_capsule_share()
        elif app.target in {'timeline','notifications','diagnostics','services','hardware','storage','operations','topology','tasks','field_library','missions','containers','incidents','backups','ai_operator','connectivity','command_center'}:self.platform_overlay=app.target;self.platform_offset=0
        elif app.target=='studio':self.studio_overlay=True
        elif app.target=='help':self.help_overlay=True
        self.dirty.set()

    def _telemetry_row(self,key):
        key=str(key or '')
        for row in (self.aux.get('telemetry') or []):
            if isinstance(row,dict) and str(row.get('key') or '')==key:return row
        return {'key':key,'label':key.split('.')[-1].replace('_',' ').title(),'value':self.state.get(key),'quality':'unknown','source':None,'age_sec':None,'unit':None,'kind':'live','category':'Other'}

    def _dashboard_widget_at(self,x,y):
        # Reverse order mirrors compositor z-order if the user intentionally
        # overlaps tiles in Beast Studio. The visually topmost tile wins.
        rows=[r for r in self._active_dashboard_widgets() if isinstance(r,dict) and bool(r.get('visible',True))]
        rows.sort(key=lambda r:(int(r.get('z',0)), str(r.get('id') or '')))
        for row in reversed(rows):
            x1,y1,x2,y2=dashboard_widget_box(row)
            if x1<=x<=x2 and y1<=y<=y2:return row
        return None

    def _widget_key_at(self,page_id,x,y):
        page_id=str(page_id)
        if page_id=='dashboard':
            row=self._dashboard_widget_at(x,y);return str((row or {}).get('key') or '') or None
        if page_id=='system':
            # Match the actual v0.19 System header geometry. These used to
            # point at pre-redesign metric boxes, which made inspector taps
            # report the wrong source after the visual hierarchy changed.
            zones=[
                ((8,43,112,105),'health.core.state'),
                ((113,43,175,105),'system.temp.cpu_c'),
                ((176,43,235,105),'system.cpu.total'),
                ((236,43,294,105),'system.memory.used_pct'),
                ((302,43,472,105),'governor.mode'),
            ]
        elif page_id=='captures':
            zones=[
                ((8,43,214,111),'captures.total'),
                ((222,43,347,111),'pwnagotchi.handshakes'),
                ((348,43,472,111),'wifi.handshake_ap_count'),
            ]
        elif page_id=='spectrum':
            zones=[
                ((8,43,123,91),'radio.primary.channel'),
                ((124,43,239,91),'radio.primary.band'),
                ((356,43,472,91),'wifi.ap_count'),
            ]
        elif page_id=='expedition':
            zones=[
                ((8,107,123,163),'expedition.distance_m'),
                ((124,107,239,163),'expedition.route_points'),
                ((240,107,355,163),'expedition.ap_unique'),
                ((356,107,472,163),'expedition.captures_delta'),
            ]
        elif page_id=='beast':
            zones=[
                ((218,43,472,136),'progression.level'),
                ((230,145,309,194),'pwnagotchi.mood'),
                ((310,145,389,194),'progression.aura'),
                ((390,145,472,194),'context.mode.effective'),
                ((230,203,314,250),'progression.discovery.beast_unique_aps'),
                ((315,203,389,250),'progression.discovery.device_first_witnessed'),
                ((390,203,472,250),'progression.achievements.count'),
            ]
        elif page_id=='networks':
            zones=[
                ((8,43,123,91),'wifi.ap_count'),
            ]
        else:
            zones=[]
        for box,key in zones:
            if box[0]<=x<=box[2] and box[1]<=y<=box[3]:return key
        return None

    @staticmethod
    def _pearson(a,b):
        aa=[float(x) for x in (a or []) if isinstance(x,(int,float))]
        bb=[float(x) for x in (b or []) if isinstance(x,(int,float))]
        n=min(len(aa),len(bb),64)
        if n<3:return None
        aa=aa[-n:];bb=bb[-n:];ma=sum(aa)/n;mb=sum(bb)/n
        num=sum((x-ma)*(y-mb) for x,y in zip(aa,bb));da=sum((x-ma)**2 for x in aa);db=sum((y-mb)**2 for y in bb)
        if da<=0 or db<=0:return None
        return max(-1.0,min(1.0,num/math.sqrt(da*db)))

    @staticmethod
    def _normalized_series(values):
        vals=[float(x) for x in (values or []) if isinstance(x,(int,float))]
        if not vals:return []
        lo=min(vals);hi=max(vals)
        if hi<=lo:return [0.5 for _ in vals]
        return [(x-lo)/(hi-lo) for x in vals]

    def _widget_inspector(self,d):
        if not self.widget_inspector_overlay or not self.widget_inspector_key:return
        t=self.theme;f=self.fonts;row=self._telemetry_row(self.widget_inspector_key);d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,274),t,accent=t.c('info'),width=2)
        quality=str(row.get('quality') or 'unknown').upper();age=row.get('age_sec');age_txt=f'{float(age):.2f}s' if isinstance(age,(int,float)) else '--';value=row.get('value');unit=row.get('unit') or ''
        d.text((20,48),'DATA SOURCE // WIDGET INSPECTOR',font=f['medium'],fill=t.c('info'));d.text((20,78),str(row.get('label') or self.widget_inspector_key)[:36],font=f['large'],fill=t.c('text'))
        d.text((20,112),self.widget_inspector_key[:54],font=f['small'],fill=t.c('accent'));d.text((20,140),f"VALUE  {(str(value)+' '+str(unit)).strip()[:30]}",font=f['small'],fill=t.c('primary'))
        d.text((20,164),f"SOURCE {str(row.get('source') or '--')[:26]}",font=f['small'],fill=t.c('text'));d.text((260,164),f"AGE {age_txt}",font=f['small'],fill=t.c('dim'))
        d.text((20,188),f"QUALITY {quality[:14]}",font=f['small'],fill=t.c('accent') if quality=='LIVE' else t.c('warn'));d.text((260,188),f"TYPE {str(row.get('kind') or '--')[:18].upper()}",font=f['tiny'],fill=t.c('dim'))
        hist=self.histories.get(self.widget_inspector_key) or [];d.text((20,214),f"HISTORY {len(hist)} SAMPLES",font=f['tiny'],fill=t.c('dim'));d.text((270,214),f"CATEGORY {str(row.get('category') or 'Other')[:17].upper()}",font=f['tiny'],fill=t.c('dim'))
        d.rounded_rectangle((18,238,462,270),radius=7,fill=t.c('panel2'),outline=t.c('info'));d.text((192,248),'CLOSE',font=f['small'],fill=t.c('info'))

    def _correlation_lab(self,d):
        if not self.correlation_overlay:return
        t=self.theme;f=self.fonts;keys=list(self.correlation_keys or [])[:2]
        while len(keys)<2:keys.append('system.cpu.total' if not keys else 'system.temp.cpu_c')
        a,b=keys;ha=self.histories.get(a) or [];hb=self.histories.get(b) or [];na=self._normalized_series(ha);nb=self._normalized_series(hb);r=self._pearson(ha,hb)
        d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,274),t,accent=t.c('info'),width=2);d.text((20,48),'CORRELATION LAB // REAL HISTORY',font=f['medium'],fill=t.c('info'))
        box=(18,77,462,203);panel(d,box,t)
        def line(vals,col):
            if len(vals)<2:return
            x1,y1,x2,y2=box;pts=[]
            for i,v in enumerate(vals[-64:]):
                x=x1+7+int(i*max(1,x2-x1-14)/max(1,min(64,len(vals))-1));y=y2-8-int(float(v)*(y2-y1-16));pts.append((x,y))
            if len(pts)>1:d.line(pts,fill=col,width=2)
        line(na,t.c('primary'));line(nb,t.c('accent'))
        ra=self._telemetry_row(a);rb=self._telemetry_row(b);d.text((24,84),f"A {str(ra.get('label') or a)[:22]}",font=f['tiny'],fill=t.c('primary'));d.text((250,84),f"B {str(rb.get('label') or b)[:22]}",font=f['tiny'],fill=t.c('accent'))
        corr='--' if r is None else f'{r:+.3f}';d.text((20,212),f'PEARSON r  {corr}',font=f['medium'],fill=t.c('text'));d.text((218,215),f'{min(len(ha),len(hb),64)} RECENT SAMPLE PAIRS',font=f['tiny'],fill=t.c('dim'))
        d.text((20,234),'NORMALIZED FOR SHAPE ONLY // SOURCES REMAIN UNCHANGED',font=f['tiny'],fill=t.c('dim'));d.rounded_rectangle((18,247,462,273),radius=6,fill=t.c('panel2'),outline=t.c('info'));d.text((186,254),'APPS / CLOSE',font=f['tiny'],fill=t.c('info'))

    def _apps_overlay(self,d):
        if not self.app_launcher:return
        t=self.theme;f=self.fonts
        d.rectangle((0,34,480,278),fill=t.c('ink'))
        panel(d,(8,38,472,276),t,accent=t.c('accent'),width=2)
        cats=self._app_categories()
        cat=cats[max(0,min(len(cats)-1,self.app_category_idx))]
        apps=self._apps_current()
        shown=apps[self.app_offset:self.app_offset+self.APP_PAGE_SIZE]
        page=self.app_offset//self.APP_PAGE_SIZE+1
        pages=max(1,(len(apps)+self.APP_PAGE_SIZE-1)//self.APP_PAGE_SIZE)

        # Category navigation gets real finger-sized targets instead of tiny
        # desktop-style arrow glyph hit areas.
        for box,glyph in ((self.APP_CAT_PREV,'‹'),(self.APP_CAT_NEXT,'›')):
            d.rounded_rectangle(box,radius=7,fill=t.c('panel2'),outline=t.c('primary'),width=2)
            gb=d.textbbox((0,0),glyph,font=f['large']);gw=gb[2]-gb[0]
            d.text((box[0]+((box[2]-box[0])-gw)//2,box[1]+12),glyph,font=f['large'],fill=t.c('primary'))
        d.text((86,47),'APPS',font=f['tiny'],fill=t.c('dim'))
        d.text((86,60),str(cat).upper()[:30],font=f['medium'],fill=t.c('accent'))
        d.text((347,60),f'{page}/{pages}',font=f['small'],fill=t.c('dim'))

        for app,box in zip(shown,self.APP_CARD_BOXES):
            col=t.c(app.accent,t.c('primary'));x1,y1,x2,y2=box
            d.rounded_rectangle(box,radius=7,fill=t.c('panel2'),outline=col,width=2)
            d.text((x1+10,y1+8),app.title.upper()[:22],font=f['small'],fill=col)
            d.text((x1+10,y1+27),app.description[:31],font=f['tiny'],fill=t.c('text'))
            d.text((x2-64,y2-14),app.category.upper()[:10],font=f['micro'],fill=t.c('dim'))

        if not shown:
            d.text((155,140),'NO APPS IN THIS VIEW',font=f['medium'],fill=t.c('dim'))

        for box,col in (
            (self.APP_NAV_PREV,t.c('primary')),
            (self.APP_NAV_CLOSE,t.c('edge')),
            (self.APP_NAV_NEXT,t.c('primary')),
        ):
            d.rounded_rectangle(box,radius=7,fill=t.c('panel2'),outline=col,width=2)
        d.text((45,242),'<< PREV',font=f['tiny'],fill=t.c('primary'))
        d.text((213,242),'CLOSE',font=f['tiny'],fill=t.c('text'))
        d.text((369,242),'NEXT >>',font=f['tiny'],fill=t.c('primary'))

    def _capsule_share_view(self,d):
        if not self.capsule_share_overlay:return
        t=self.theme;f=self.fonts
        d.rectangle((0,34,480,278),fill=t.c('ink'))
        panel(d,(8,40,472,274),t,accent=t.c('info'),width=2)
        row=self.capsule_share if isinstance(self.capsule_share,dict) else {}
        d.text((232,49),'BEAST CAPSULE // OFFLINE SHARE',font=f['small'],fill=t.c('info'))

        if self.capsule_loading or row.get('loading'):
            d.text((232,82),'PREPARING LINEAGE CAPSULE',font=f['medium'],fill=t.c('text'))
            d.text((232,108),'Reading the active Beast from Core.',font=f['tiny'],fill=t.c('dim'))
            d.text((232,126),'Nothing has been imported or published.',font=f['tiny'],fill=t.c('dim'))
            d.rounded_rectangle(self.CAPSULE_QR_BOX,radius=8,fill=t.c('panel2'),outline=t.c('edge'),width=2)
            d.text((63,143),'PREPARING',font=f['medium'],fill=t.c('dim'))
        elif not row.get('ok'):
            d.rounded_rectangle(self.CAPSULE_QR_BOX,radius=8,fill=t.c('panel2'),outline=t.c('warn'),width=2)
            d.text((47,132),'CAPSULE',font=f['large'],fill=t.c('warn'))
            d.text((38,160),'UNAVAILABLE',font=f['medium'],fill=t.c('warn'))
            d.text((232,82),'EXPORT NOT READY',font=f['medium'],fill=t.c('warn'))
            d.text((232,108),str(row.get('error') or 'No Capsule data available.')[:36],font=f['tiny'],fill=t.c('text'))
            d.text((232,130),'No substitute/fake QR is shown.',font=f['tiny'],fill=t.c('dim'))
        else:
            qr=row.get('qr') if isinstance(row.get('qr'),dict) else {}
            frames=[str(x) for x in (qr.get('frames') or []) if str(x)]
            payload=((row.get('envelope') or {}).get('payload') or {}) if isinstance(row.get('envelope'),dict) else {}
            total=max(1,len(frames));self.capsule_frame_idx=max(0,min(total-1,int(self.capsule_frame_idx)))
            frame=frames[self.capsule_frame_idx] if frames else ''
            qrstat=qr_backend_status();render_error=None;render_meta={}
            if frame and qrstat.get('available'):
                try:render_meta=draw_qr(d,self.CAPSULE_QR_BOX,frame,error_correction='M')
                except Exception as exc:render_error=str(exc)
            else:
                render_error='QR renderer dependency is not installed' if not qrstat.get('available') else 'Capsule contains no QR frame'
            if render_error:
                d.rounded_rectangle(self.CAPSULE_QR_BOX,radius=8,fill=t.c('panel2'),outline=t.c('warn'),width=2)
                d.text((49,126),'QR FRAME',font=f['medium'],fill=t.c('warn'))
                d.text((53,149),'UNAVAILABLE',font=f['small'],fill=t.c('warn'))
                d.text((32,176),render_error[:28],font=f['micro'],fill=t.c('dim'))

            preview=bool(payload.get('preview'))
            name=str(payload.get('name') or 'UNNAMED BEAST')
            lineage=str(payload.get('lineage') or '--').replace('_',' ').upper()
            level=payload.get('level');stage=str(payload.get('stage') or '--').upper()
            kind=str(payload.get('kind') or 'beast').upper()
            d.text((232,72),name[:24],font=f['medium'],fill=t.c('accent'))
            d.text((232,94),f'{kind[:8]}  ·  {lineage[:18]}',font=f['tiny'],fill=t.c('text'))
            d.text((232,112),f'LV {level if level is not None else "--"}  ·  {stage[:18]}',font=f['small'],fill=t.c('primary'))
            d.text((232,136),f'FRAME {self.capsule_frame_idx+1}/{total}',font=f['medium'],fill=t.c('info'))
            if render_meta:
                d.text((336,139),f"{render_meta.get('modules','--')} MOD / {render_meta.get('scale_px','--')}PX",font=f['micro'],fill=t.c('dim'))
            integrity=(row.get('envelope') or {}).get('integrity') if isinstance(row.get('envelope'),dict) else {}
            authenticated=bool((integrity or {}).get('authenticated'))
            d.text((232,160),'SIGNED / AUTHENTICATED' if authenticated else 'UNSIGNED · INTEGRITY ONLY',font=f['tiny'],fill=t.c('accent') if authenticated else t.c('warn'))
            d.text((232,179),'NO CAPTURES · NO GPS · NO CREDS',font=f['tiny'],fill=t.c('dim'))
            d.text((232,197),'LOCAL QR SHARE · NO CLOUD REQUIRED',font=f['tiny'],fill=t.c('text'))
            if preview:
                d.rounded_rectangle((232,204,464,220),radius=4,fill=t.c('panel2'),outline=t.c('warn'))
                d.text((273,208),'GALLERY PREVIEW · NOT IMPORTABLE',font=f['micro'],fill=t.c('warn'))

        for box,label,col in (
            (self.CAPSULE_PREV,'< FRAME',t.c('primary')),
            (self.CAPSULE_CLOSE,'CLOSE',t.c('edge')),
            (self.CAPSULE_NEXT,'FRAME >',t.c('primary')),
        ):
            d.rounded_rectangle(box,radius=7,fill=t.c('panel2'),outline=col,width=2)
            tb=d.textbbox((0,0),label,font=f['micro']);tw=tb[2]-tb[0]
            d.text((box[0]+max(4,((box[2]-box[0])-tw)//2),box[1]+19),label,font=f['micro'],fill=t.c('text') if label=='CLOSE' else col)

    def _telemetry_inspector(self,d):
        if not self.telemetry_overlay:return
        t=self.theme;f=self.fonts;d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,274),t,accent=t.c('accent'),width=2)
        rows=[r for r in (self.aux.get('telemetry') or []) if isinstance(r,dict)];page=self.telemetry_offset//4+1;pages=max(1,(len(rows)+3)//4)
        d.text((20,47),'TELEMETRY INSPECTOR',font=f['medium'],fill=t.c('accent'));d.text((395,51),f'{page}/{pages}',font=f['small'],fill=t.c('dim'))
        for i,row in enumerate(rows[self.telemetry_offset:self.telemetry_offset+4]):
            y=65+i*42;quality=str(row.get('quality') or 'unknown').upper();qcol=t.c('accent') if quality=='LIVE' else t.c('warn') if quality in {'STALE','DEGRADED'} else t.c('info')
            d.line((18,y+35,462,y+35),fill=t.c('edge'));d.text((20,y),str(row.get('label') or row.get('key'))[:24],font=f['small'],fill=t.c('text'))
            val=row.get('value');unit=row.get('unit') or '';txt=(f'{val} {unit}').strip();d.text((190,y),txt[:17],font=f['small'],fill=t.c('primary'))
            d.text((350,y),quality[:10],font=f['tiny'],fill=qcol);src=str(row.get('source') or '--');age=row.get('age_sec');age_txt=f'{float(age):.1f}s' if isinstance(age,(int,float)) else '--'
            d.text((20,y+18),str(row.get('key') or '')[:34],font=f['tiny'],fill=t.c('dim'));d.text((292,y+18),f'{src[:14]} / {age_txt}',font=f['tiny'],fill=t.c('dim'))
        if not rows:d.text((88,135),'WAITING FOR TELEMETRY CATALOG...',font=f['small'],fill=t.c('dim'))
        d.rounded_rectangle((12,238,154,274),radius=5,fill=t.c('panel2'),outline=t.c('primary'));d.rounded_rectangle((162,238,318,274),radius=5,fill=t.c('panel2'),outline=t.c('edge'));d.rounded_rectangle((326,238,468,274),radius=5,fill=t.c('panel2'),outline=t.c('primary'))
        d.text((45,250),'<< PREV',font=f['tiny'],fill=t.c('primary'));d.text((216,250),'APPS',font=f['tiny'],fill=t.c('text'));d.text((369,250),'NEXT >>',font=f['tiny'],fill=t.c('primary'))

    def _plugins_manager(self,d):
        if not self.plugins_overlay:return
        t=self.theme;f=self.fonts;d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,274),t,accent=t.c('secondary'),width=2)
        rows=[r for r in (self.state.get('plugins.catalog') or []) if isinstance(r,dict)];page=self.plugins_offset//3+1;pages=max(1,(len(rows)+2)//3)
        d.text((20,47),'PLUGIN INTEGRATION',font=f['medium'],fill=t.c('secondary'));d.text((397,51),f'{page}/{pages}',font=f['small'],fill=t.c('dim'))
        for i,row in enumerate(rows[self.plugins_offset:self.plugins_offset+3]):
            y1=64+i*56;y2=y1+49;enabled=bool(row.get('enabled'));col=t.c('accent') if enabled else t.c('dim');integ=str(row.get('integration') or 'config_only')
            d.rounded_rectangle((18,y1,462,y2),radius=6,fill=t.c('panel2'),outline=col if enabled else t.c('edge'))
            d.text((28,y1+7),str(row.get('name') or 'plugin')[:24],font=f['small'],fill=t.c('text'));d.text((366,y1+7),'ON' if enabled else 'OFF',font=f['small'],fill=col)
            d.text((28,y1+25),f"{str(row.get('role') or 'plugin')[:16]} // {integ[:20]}",font=f['tiny'],fill=t.c('info') if integ not in {'config_only','isolated'} else t.c('dim'))
            d.text((286,y1+25),str(row.get('display_policy') or '')[:22],font=f['tiny'],fill=t.c('dim'))
        if not rows:d.text((105,135),'NO PLUGINS REPORTED YET',font=f['small'],fill=t.c('dim'))
        d.rounded_rectangle((12,238,154,274),radius=5,fill=t.c('panel2'),outline=t.c('primary'));d.rounded_rectangle((162,238,318,274),radius=5,fill=t.c('panel2'),outline=t.c('edge'));d.rounded_rectangle((326,238,468,274),radius=5,fill=t.c('panel2'),outline=t.c('primary'))
        d.text((45,250),'<< PREV',font=f['tiny'],fill=t.c('primary'));d.text((216,250),'APPS',font=f['tiny'],fill=t.c('text'));d.text((369,250),'NEXT >>',font=f['tiny'],fill=t.c('primary'))

    @staticmethod
    def _human_bytes(value):
        try:v=float(value or 0)
        except Exception:return '--'
        for unit in ('B','KB','MB','GB'):
            if abs(v)<1024.0:return f'{v:.0f}{unit}' if unit=='B' else f'{v:.1f}{unit}'
            v/=1024.0
        return f'{v:.1f}TB'

    @staticmethod
    def _age_text(ts):
        try:
            age=max(0.0,time.time()-float(ts))
            if age<60:return f'{age:.0f}s ago'
            if age<3600:return f'{age/60:.0f}m ago'
            if age<86400:return f'{age/3600:.1f}h ago'
            return f'{age/86400:.1f}d ago'
        except Exception:return '--'

    def _beastdex(self,d):
        if not self.beastdex_overlay:return
        t=self.theme;f=self.fonts;rows=[r for r in (self.state.get('records.encounters.recent') or []) if isinstance(r,dict)]
        d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,274),t,accent=t.c('accent'),width=2)
        if self.beastdex_detail is not None and self.beastdex_detail<len(rows):
            r=rows[self.beastdex_detail];ssid=str(r.get('ssid') or '<hidden>');vendor=str(r.get('vendor') or 'Unknown')
            d.text((20,48),'BEASTDEX // ENCOUNTER DETAIL',font=f['medium'],fill=t.c('accent'));d.text((20,76),ssid[:38],font=f['large'],fill=t.c('text'));d.text((20,101),vendor[:44],font=f['small'],fill=t.c('info'))
            d.text((20,126),f"BSSID {str(r.get('bssid') or '--')[:24]}",font=f['small'],fill=t.c('dim'));d.text((20,147),f"CH {r.get('channel','--')}  RSSI {r.get('strongest_rssi','--')} dBm  CLIENTS {r.get('max_clients','--')}",font=f['small'],fill=t.c('text'))
            enc=str(r.get('encryption') or '--');chs=','.join(map(str,r.get('channels') or [])) or '--';d.text((20,168),f'ENC {enc[:22]}  CHANNELS {chs[:22]}',font=f['small'],fill=t.c('text'))
            d.text((20,190),f"OBS {r.get('observation_count',0)}  SESSIONS {r.get('seen_sessions',0)}  LAST {self._age_text(r.get('last_seen'))}",font=f['small'],fill=t.c('primary'))
            if isinstance(r.get('last_latitude'),(int,float)) and isinstance(r.get('last_longitude'),(int,float)):
                d.text((20,211),f"LAST GPS {float(r['last_latitude']):.5f}, {float(r['last_longitude']):.5f}",font=f['tiny'],fill=t.c('secondary'))
            else:d.text((20,211),'LAST GPS --',font=f['tiny'],fill=t.c('dim'))
            d.rounded_rectangle((18,238,462,270),radius=7,fill=t.c('panel2'),outline=t.c('primary'));d.text((205,248),'BACK',font=f['small'],fill=t.c('primary'));return
        total=int(self.state.get('records.encounters.total') or 0);vendors=int(self.state.get('records.encounters.vendor_count') or 0);page=self.beastdex_offset//3+1;pages=max(1,(len(rows)+2)//3)
        d.text((20,47),'BEASTDEX // NETWORK ENCYCLOPEDIA',font=f['medium'],fill=t.c('accent'));d.text((332,49),f'{total} AP / {vendors} VEND',font=f['tiny'],fill=t.c('dim'))
        for i,r in enumerate(rows[self.beastdex_offset:self.beastdex_offset+3]):
            y=66+i*52;ssid=str(r.get('ssid') or '<hidden>');vendor=str(r.get('vendor') or 'Unknown');ch=r.get('channel','--');sig=r.get('strongest_rssi','--')
            d.rounded_rectangle((18,y,462,y+45),radius=6,fill=t.c('panel2'),outline=t.c('edge'));d.text((28,y+6),ssid[:28],font=f['small'],fill=t.c('text'));d.text((307,y+6),f'CH {ch}  {sig}dBm',font=f['tiny'],fill=t.c('primary'));d.text((28,y+23),vendor[:26],font=f['tiny'],fill=t.c('info'));d.text((236,y+23),f"OBS {r.get('observation_count',0)} // {self._age_text(r.get('last_seen'))}",font=f['tiny'],fill=t.c('dim'))
        if not rows:d.text((96,136),'NO PERSISTED ENCOUNTERS YET',font=f['small'],fill=t.c('dim'))
        d.rounded_rectangle((12,238,154,274),radius=5,fill=t.c('panel2'),outline=t.c('primary'));d.rounded_rectangle((162,238,318,274),radius=5,fill=t.c('panel2'),outline=t.c('edge'));d.rounded_rectangle((326,238,468,274),radius=5,fill=t.c('panel2'),outline=t.c('primary'));d.text((45,250),'<< PREV',font=f['tiny'],fill=t.c('primary'));d.text((202,250),f'APPS {page}/{pages}',font=f['tiny'],fill=t.c('text'));d.text((369,250),'NEXT >>',font=f['tiny'],fill=t.c('primary'))

    def _capture_vault(self,d):
        if not self.capture_vault_overlay:return
        t=self.theme;f=self.fonts;rows=[r for r in (self.state.get('captures.recent') or []) if isinstance(r,dict)]
        d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,274),t,accent=t.c('secondary'),width=2)
        if self.capture_vault_detail is not None and self.capture_vault_detail<len(rows):
            r=rows[self.capture_vault_detail];name=str(r.get('filename') or '--');hint=str(r.get('network_hint') or '--')
            d.text((20,48),'CAPTURE VAULT // FILE DETAIL',font=f['medium'],fill=t.c('secondary'));d.text((20,78),name[:48],font=f['medium'],fill=t.c('text'));d.text((20,108),f"TYPE {str(r.get('extension') or '--').upper()}   SIZE {self._human_bytes(r.get('size_bytes'))}",font=f['small'],fill=t.c('accent'));d.text((20,132),f"MODIFIED {self._age_text(r.get('mtime'))}",font=f['small'],fill=t.c('text'));d.text((20,157),'FILENAME-DERIVED HINT',font=f['tiny'],fill=t.c('dim'));d.text((20,171),hint[:54],font=f['small'],fill=t.c('info'));d.text((20,199),'Packet metadata parsing is not claimed yet.',font=f['tiny'],fill=t.c('warn'));d.text((20,214),str(r.get('path') or '')[-62:],font=f['tiny'],fill=t.c('dim'));d.rounded_rectangle((18,238,462,270),radius=7,fill=t.c('panel2'),outline=t.c('primary'));d.text((205,248),'BACK',font=f['small'],fill=t.c('primary'));return
        total=int(self.state.get('captures.indexed_files') or 0);size=self._human_bytes(self.state.get('captures.storage_bytes'));page=self.capture_vault_offset//3+1;pages=max(1,(len(rows)+2)//3)
        d.text((20,47),'CAPTURE VAULT // REAL FILE INDEX',font=f['medium'],fill=t.c('secondary'));d.text((355,49),f'{total} / {size}',font=f['tiny'],fill=t.c('dim'))
        for i,r in enumerate(rows[self.capture_vault_offset:self.capture_vault_offset+3]):
            y=66+i*52;name=str(r.get('filename') or '--');ext=str(r.get('extension') or '').upper()
            d.rounded_rectangle((18,y,462,y+45),radius=6,fill=t.c('panel2'),outline=t.c('edge'));d.text((28,y+6),name[:38],font=f['small'],fill=t.c('text'));d.text((377,y+6),ext[:8],font=f['tiny'],fill=t.c('accent'));d.text((28,y+24),self._human_bytes(r.get('size_bytes')),font=f['tiny'],fill=t.c('primary'));d.text((112,y+24),self._age_text(r.get('mtime')),font=f['tiny'],fill=t.c('dim'));d.text((230,y+24),('HINT '+str(r.get('network_hint') or '--'))[:35],font=f['tiny'],fill=t.c('info'))
        if not rows:d.text((115,136),'NO CAPTURE FILES INDEXED',font=f['small'],fill=t.c('dim'))
        d.rounded_rectangle((12,238,154,274),radius=5,fill=t.c('panel2'),outline=t.c('primary'));d.rounded_rectangle((162,238,318,274),radius=5,fill=t.c('panel2'),outline=t.c('edge'));d.rounded_rectangle((326,238,468,274),radius=5,fill=t.c('panel2'),outline=t.c('primary'));d.text((45,250),'<< PREV',font=f['tiny'],fill=t.c('primary'));d.text((202,250),f'APPS {page}/{pages}',font=f['tiny'],fill=t.c('text'));d.text((369,250),'NEXT >>',font=f['tiny'],fill=t.c('primary'))

    def _performance_lab(self,d):
        if not self.performance_overlay:return
        t=self.theme;f=self.fonts;rows=[r for r in (self.state.get('performance.processes') or []) if isinstance(r,dict)]
        d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,274),t,accent=t.c('warn'),width=2);page=self.performance_offset//3+1;pages=max(1,(len(rows)+2)//3)
        d.text((20,47),'PERFORMANCE // COST ATTRIBUTION',font=f['medium'],fill=t.c('warn'));d.text((393,50),f'{page}/{pages}',font=f['tiny'],fill=t.c('dim'))
        for i,r in enumerate(rows[self.performance_offset:self.performance_offset+3]):
            y=68+i*42;cpu=float(r.get('cpu_pct') or 0);rss=float(r.get('rss_mb') or 0);col=t.c('warn') if cpu>=35 else t.c('accent')
            d.text((24,y),str(r.get('label') or r.get('id'))[:22],font=f['small'],fill=t.c('text'));d.text((264,y),f'{cpu:5.1f}% CPU',font=f['small'],fill=col);d.text((382,y),f'{rss:.0f}M',font=f['small'],fill=t.c('info'));d.line((22,y+28,458,y+28),fill=t.c('edge'))
        render=self.state.get('performance.ui.avg_render_ms');fb=self.state.get('performance.fb.write_ratio_pct');beast=self.state.get('performance.beast.cpu_pct');plat=self.state.get('performance.platform_services.cpu_pct')
        d.text((22,198),f"BEAST {float(beast or 0):.1f}%  PLATFORM {float(plat or 0):.1f}%",font=f['small'],fill=t.c('primary'));d.text((22,216),f"RENDER {float(render or 0):.1f}ms  FB WRITE {float(fb or 0):.1f}% OF FRAME",font=f['small'],fill=t.c('accent'));d.rounded_rectangle((12,238,154,274),radius=5,fill=t.c('panel2'),outline=t.c('primary'));d.rounded_rectangle((162,238,318,274),radius=5,fill=t.c('panel2'),outline=t.c('edge'));d.rounded_rectangle((326,238,468,274),radius=5,fill=t.c('panel2'),outline=t.c('primary'));d.text((45,250),'<< PREV',font=f['tiny'],fill=t.c('primary'));d.text((202,250),f'APPS {page}/{pages}',font=f['tiny'],fill=t.c('text'));d.text((369,250),'NEXT >>',font=f['tiny'],fill=t.c('primary'))

    def _platform_rows(self,mode):
        rows=[];mode=str(mode or '')
        if mode=='timeline':
            for e in reversed([x for x in self.events if isinstance(x,dict)]):
                rows.append({'title':str(e.get('type') or 'event'),'subtitle':str(e.get('source') or '--'),'value':self._age_text(e.get('ts')),'severity':str(e.get('severity') or 'info')})
        elif mode=='notifications':
            important=[]
            for e in reversed([x for x in self.events if isinstance(x,dict)]):
                sev=str(e.get('severity') or 'info').lower();typ=str(e.get('type') or '')
                if sev in {'warning','error','critical'} or any(k in typ for k in ('achievement','capture','gps.','hardware','dock.','governor.','rare.')):important.append(e)
            for e in important:
                rows.append({'title':str(e.get('type') or 'notice'),'subtitle':str(e.get('source') or '--'),'value':self._age_text(e.get('ts')),'severity':str(e.get('severity') or 'info')})
        elif mode=='services':
            for r in self.state.get('platform.services') or []:
                if not isinstance(r,dict):continue
                active=str(r.get('active') or 'unknown');rows.append({'title':str(r.get('unit') or 'service'),'subtitle':f"{active} / {r.get('sub','--')} / pid {r.get('pid',0)}",'value':active.upper(),'severity':'info' if active=='active' else 'warning'})
        elif mode=='connectivity':
            route=bool(self.state.get('network.route.available'))
            rows.append({'title':'DEFAULT ROUTE','subtitle':f"{self.state.get('network.default.dev') or '--'} via {self.state.get('network.default.gateway') or '--'}",'value':'AVAILABLE' if route else 'NONE','severity':'info' if route else 'warning'})
            rows.append({'title':'INTERNET','subtitle':'Beast does not infer Internet from a default route','value':str(self.state.get('network.internet.state') or 'unknown').upper(),'severity':'info'})
            for r in self.state.get('network.interfaces') or []:
                if not isinstance(r,dict):continue
                addrs=', '.join(str(x) for x in (r.get('addresses') or [])[:2]) or '--'
                rows.append({'title':str(r.get('name') or 'interface'),'subtitle':addrs,'value':str(r.get('operstate') or 'unknown').upper(),'severity':'info' if r.get('operstate')=='up' else 'warning'})
        elif mode=='command_center':
            rows.append({'title':'EXTERNAL DISPLAY','subtitle':f"{self.state.get('display.connected_outputs') or 0} DRM/HDMI output(s) connected",'value':'READY' if self.state.get('display.external_connected') else 'NONE','severity':'info'})
            rows.append({'title':'DESKTOP RUNTIME','subtitle':', '.join(str(x.get('label')) for x in (self.state.get('desktop.runtimes') or []) if isinstance(x,dict)) or 'No optional desktop installed','value':'AVAILABLE' if self.state.get('desktop.runtime.available') else 'NOT INSTALLED','severity':'info'})
            rows.append({'title':'WEB BROWSER','subtitle':', '.join(str(x.get('id')) for x in (self.state.get('desktop.browsers') or []) if isinstance(x,dict)) or 'No local browser detected','value':'AVAILABLE' if self.state.get('desktop.browser.available') else 'NOT INSTALLED','severity':'info'})
            rows.append({'title':'ROLE MODEL','subtitle':'TFT = Field UI / external display = Command surface','value':'CAPABILITY DRIVEN','severity':'info'})
        elif mode=='missions':
            for r in self.state.get('missions.items') or []:
                if not isinstance(r,dict):continue
                ready=bool(r.get('requirements_met'));missing=', '.join(r.get('missing_capabilities') or [])
                rows.append({'title':str(r.get('label') or r.get('id') or 'mission'),'subtitle':str(r.get('description') or '')[:64]+((' / missing '+missing) if missing else ''),'value':'READY' if ready else 'NEEDS HW','severity':'info' if ready else 'warning'})
        elif mode=='hardware':
            for r in self.state.get('platform.hardware') or []:
                if not isinstance(r,dict):continue
                raw=str(r.get('raw') or r.get('id') or 'USB device');rows.append({'title':raw[33:77] if len(raw)>33 else raw,'subtitle':raw[:32],'value':str(r.get('id') or 'USB'),'severity':'info'})
            if not rows:
                for r in self.state.get('capabilities.items') or []:
                    if isinstance(r,dict):rows.append({'title':str(r.get('label') or r.get('id') or 'capability'),'subtitle':str(r.get('detail') or ''),'value':str(r.get('state') or 'DETECTED'),'severity':'info'})
        elif mode=='storage':
            used=self.state.get('storage.root.used_pct');free=self.state.get('storage.root.free_bytes');ro=bool(self.state.get('storage.root.readonly'))
            rows.append({'title':'ROOT FILESYSTEM','subtitle':f"Used {used:.1f}%" if isinstance(used,(int,float)) else 'Usage --','value':'READ ONLY' if ro else self._human_bytes(free)+' FREE','severity':'warning' if ro else 'info'})
            for r in self.state.get('storage.mounts') or []:
                if not isinstance(r,dict):continue
                opts=r.get('options') or [];rows.append({'title':str(r.get('mount') or '--'),'subtitle':f"{r.get('source','--')} // {r.get('fstype','--')}",'value':'RO' if 'ro' in opts and 'rw' not in opts else 'RW','severity':'warning' if 'ro' in opts and 'rw' not in opts else 'info'})
        elif mode=='operations':
            summary=self.state.get('overview.summary') or {}
            rows.append({'title':'PLATFORM HEALTH','subtitle':f"Pwn {summary.get('pwnagotchi','--')} / Bettercap {summary.get('bettercap','--')}",'value':str(self.state.get('overview.state') or '--').upper(),'severity':'warning' if self.state.get('overview.attention_count') else 'info'})
            rows.append({'title':'BEAST CORE','subtitle':f"{self.state.get('health.core.collector_count',0)} collectors / {self.state.get('health.core.critical_count',0)} critical",'value':str(self.state.get('health.core.state') or '--').upper(),'severity':'warning' if self.state.get('health.core.state')!='healthy' else 'info'})
            rows.append({'title':'EXPEDITION','subtitle':f"AP {self.state.get('expedition.ap_unique',0)} / {self.state.get('expedition.distance_m',0)} m",'value':'ACTIVE' if self.state.get('expedition.id') else 'IDLE','severity':'info'})
            rows.append({'title':'FIELD LIBRARY','subtitle':f"{self.state.get('library.text_indexed_count',0)} searchable text docs",'value':str(self.state.get('library.document_count',0))+' DOC','severity':'info'})
            rows.append({'title':'TASK CENTER','subtitle':'background operations / indexing','value':str(len((self.aux.get('jobs') or {}).get('items') or []))+' JOB','severity':'info'})
            rows.append({'title':'PLUGIN LAYER','subtitle':f"{self.state.get('plugins.integrated_count',0)} integrated / {self.state.get('plugins.enabled_count',0)} enabled",'value':str(self.state.get('plugins.catalog_count',0))+' PLUG','severity':'info'})
        elif mode=='topology':
            for r in self.state.get('topology.nodes') or []:
                if not isinstance(r,dict):continue
                st=str(r.get('state') or 'unknown');bad=st not in {'active','running','ready','available','healthy','fix','connected','connected_no_fix'}
                rows.append({'title':str(r.get('label') or r.get('id') or 'NODE'),'subtitle':str(r.get('kind') or '')+' / '+str(r.get('detail') or ''),'value':st.upper(),'severity':'warning' if bad else 'info'})
        elif mode=='tasks':
            for r in ((self.aux.get('jobs') or {}).get('items') or self.state.get('tasks.recent') or []):
                if not isinstance(r,dict):continue
                st=str(r.get('status') or 'unknown');prog=r.get('progress');pt=f"{float(prog)*100:.0f}%" if isinstance(prog,(int,float)) else st.upper()
                rows.append({'title':str(r.get('label') or r.get('kind') or 'JOB'),'subtitle':str(r.get('detail') or '')[:64],'value':pt,'severity':'warning' if st in {'failed','error'} else 'info'})
        elif mode=='field_library':
            lib=self.aux.get('library') or {}
            for r in lib.get('recent') or []:
                if not isinstance(r,dict):continue
                ext=str(r.get('extension') or '').upper().lstrip('.');size=int(r.get('size_bytes') or 0)
                rows.append({'title':str(r.get('title') or r.get('filename') or 'DOCUMENT'),'subtitle':str(r.get('path') or '')[-64:],'value':f"{ext or 'DOC'} {self._human_bytes(size)}",'severity':'info'})
        elif mode=='backups':
            for r in self.state.get('backups.items') or []:
                if not isinstance(r,dict):continue
                rows.append({'title':str(r.get('name') or 'BACKUP'),'subtitle':str(r.get('path') or '')[-64:],'value':self._human_bytes(r.get('size_bytes')),'severity':'info'})
            if not rows:
                rows.append({'title':'NO BEAST BACKUPS','subtitle':'Create one from Beast Studio / Command Center','value':'READY','severity':'info'})
        elif mode=='incidents':
            for r in ((self.aux.get('incidents') or {}).get('items') or self.state.get('incidents.recent') or []):
                if not isinstance(r,dict):continue
                status=str(r.get('status') or 'unknown');sev=str(r.get('severity') or 'warning')
                docs=len(((r.get('snapshot') or {}).get('related_documents') or []))
                detail=str(r.get('detail') or '')[:52]+(f' / {docs} RUNBOOK' if docs==1 else f' / {docs} RUNBOOKS' if docs else '')
                rows.append({'title':str(r.get('summary') or r.get('kind') or 'INCIDENT'),'subtitle':detail,'value':status.upper(),'severity':'warning' if status=='open' or sev in {'warning','critical'} else 'info'})
        elif mode=='containers':
            for r in self.state.get('containers.items') or []:
                if not isinstance(r,dict):continue
                st='RUNNING' if r.get('running') else str(r.get('status') or 'STOPPED').upper()[:14]
                rows.append({'title':str(r.get('name') or r.get('id') or 'container'),'subtitle':str(r.get('image') or '')[:64],'value':st,'severity':'info' if r.get('running') else 'warning'})
            if not rows and self.state.get('containers.runtime.available'):
                rows.append({'title':'NO CONTAINERS','subtitle':str(self.state.get('containers.runtime') or 'runtime')+' is available','value':'READY','severity':'info'})
        elif mode=='ai_operator':
            rows.append({'title':'LOCAL AI RUNTIME','subtitle':str(self.state.get('ai.llama.binary') or 'llama.cpp not detected'),'value':'READY' if self.state.get('ai.llama.available') else 'NOT INSTALLED','severity':'info'})
            rows.append({'title':'VOICE / STT','subtitle':str(self.state.get('ai.whisper.binary') or 'whisper.cpp not detected'),'value':'READY' if self.state.get('ai.whisper.available') else 'NOT INSTALLED','severity':'info'})
            rows.append({'title':'LOCAL MODELS','subtitle':'Model files discovered in Beast model roots','value':str(self.state.get('ai.models.count') or 0),'severity':'info'})
            rows.append({'title':'PRIVILEGE MODEL','subtitle':'Observer / Operator / Maintainer / Administrator Session','value':'ACTION BROKER','severity':'info'})
        elif mode=='diagnostics':
            coverage=self.state.get('doctor.coverage') or {}
            counts=coverage.get('counts') or {} if isinstance(coverage,dict) else {}
            covered=int(counts.get('covered',0) or 0);unavailable=int(counts.get('unavailable',0) or 0);unknown=int(counts.get('unknown',0) or 0)
            total=int(coverage.get('count',covered+unavailable+unknown) or 0) if isinstance(coverage,dict) else 0
            if total:
                rows.append({
                    'title':'DOCTOR COVERAGE',
                    'subtitle':f'{covered} covered / {unavailable} unavailable / {unknown} unknown',
                    'value':'FULL' if unknown==0 else 'PARTIAL',
                    'severity':'info' if unknown==0 else 'warning',
                })
            patient=self.state.get('doctor.patient.identity') or {}
            if isinstance(patient,dict) and any(patient.values()):
                model=str(patient.get('model') or 'unknown model')
                arch=str(patient.get('architecture') or 'unknown arch')
                kernel=str(patient.get('kernel') or 'unknown kernel')
                rows.append({
                    'title':'PATIENT CHART',
                    'subtitle':f'{model} / {arch} / kernel {kernel}'[:67],
                    'value':str(patient.get('os_id') or 'IDENTIFIED').upper()[:14],
                    'severity':'info',
                })
                py=str(patient.get('python_version') or 'unknown')
                pwn=str(patient.get('pwnagotchi_version') or 'unknown')
                osver=str(patient.get('os_version_id') or patient.get('os_build_id') or 'unknown')
                rows.append({
                    'title':'COMPATIBILITY FINGERPRINT',
                    'subtitle':f'Pwnagotchi {pwn} / Python {py} / OS {osver}'[:67],
                    'value':'READ ONLY',
                    'severity':'info',
                })
            memory=self.state.get('doctor.patient.memory') or {}
            recurrence=(memory.get('recurrence') or {}) if isinstance(memory,dict) else {}
            if isinstance(recurrence,dict) and recurrence:
                recurrent=sum(1 for row in recurrence.values() if isinstance(row,dict) and row.get('recurrent'))
                active=sum(1 for row in recurrence.values() if isinstance(row,dict) and row.get('active'))
                rows.append({
                    'title':'RECURRENCE MEMORY',
                    'subtitle':f'{len(recurrence)} incident kinds / {recurrent} recurrent / {active} active',
                    'value':'RECUR' if recurrent else 'QUIET',
                    'severity':'warning' if active or recurrent else 'info',
                })
            kg_count=int(self.state.get('doctor.patient.known_good_count') or 0)
            drift=self.state.get('doctor.patient.known_good_drift') or {}
            if kg_count or (isinstance(drift,dict) and drift.get('found')):
                change_count=int((drift.get('change_count') if isinstance(drift,dict) else 0) or 0)
                checkpoint=(drift.get('checkpoint') or {}) if isinstance(drift,dict) else {}
                label=str(checkpoint.get('label') or 'latest baseline')
                rows.append({
                    'title':'KNOWN-GOOD BASELINE',
                    'subtitle':f'{kg_count} saved / {label}'[:67],
                    'value':f'DRIFT {change_count}' if change_count else 'MATCH',
                    'severity':'warning' if change_count else 'info',
                })
            names=[]
            for k in self.state:
                if k.startswith('health.collector.') and k.endswith('.state'):
                    name=k[len('health.collector.'):-len('.state')];names.append(name)
            for name in sorted(set(names)):
                base=f'health.collector.{name}.';st=str(self.state.get(base+'state') or 'unknown');dur=self.state.get(base+'duration_ms');err=self.state.get(base+'last_error');age=self.state.get(base+'age_sec')
                sub=(f"{float(dur):.1f}ms" if isinstance(dur,(int,float)) else '--')+(f" / age {float(age):.1f}s" if isinstance(age,(int,float)) else '')
                if err:sub+=' / '+str(err)[:38]
                rows.append({'title':name.upper(),'subtitle':sub,'value':st.upper(),'severity':'info' if st=='ok' else 'warning'})
        return rows

    def _platform_browser(self,d):
        if not self.platform_overlay:return
        mode=str(self.platform_overlay);t=self.theme;f=self.fonts;rows=self._platform_rows(mode);page=self.platform_offset//self.PLATFORM_PAGE_SIZE+1;pages=max(1,(len(rows)+self.PLATFORM_PAGE_SIZE-1)//self.PLATFORM_PAGE_SIZE)
        if mode=='topology':
            d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,274),t,accent=t.c('info'),width=2)
            d.text((20,47),'SERVICE TOPOLOGY // LIVE DEPENDENCIES',font=f['medium'],fill=t.c('info'))
            nodes={str(x.get('id')):x for x in (self.state.get('topology.nodes') or []) if isinstance(x,dict)}
            pos={'radio':(34,92),'bettercap':(123,92),'pwnagotchi':(220,92),'bridge':(315,92),'core':(406,92),'gps':(123,177),'ui':(315,177),'studio':(406,177)}
            def cstate(st):
                st=str(st or 'unknown').lower();return t.c('accent') if st in {'active','running','ready','available','healthy','fix','connected','connected_no_fix','up'} else t.c('warn')
            for e in self.state.get('topology.edges') or []:
                if not isinstance(e,dict):continue
                a=pos.get(str(e.get('from')));b=pos.get(str(e.get('to')));
                if a and b:d.line((a[0],a[1],b[0],b[1]),fill=t.c('edge'),width=2)
            for nid,(x,y) in pos.items():
                n=nodes.get(nid,{}) ; col=cstate(n.get('state')); d.ellipse((x-24,y-18,x+24,y+18),fill=t.c('panel2'),outline=col,width=2)
                label=str(n.get('label') or nid).upper().replace('BEAST ','')[:10];d.text((x-22,y-5),label,font=f['micro'],fill=col)
            d.text((18,216),'RADIO → BETTERCAP → PWNAGOTCHI → BRIDGE → CORE',font=f['tiny'],fill=t.c('dim'))
            d.text((18,231),'GPS → CORE     CORE → UI / STUDIO',font=f['tiny'],fill=t.c('dim'))
            fail=int(self.state.get('topology.failure_count') or 0);d.text((18,248),f'{fail} DEPENDENCY FAILURE(S)',font=f['small'],fill=t.c('warn') if fail else t.c('accent'))
            d.rounded_rectangle(self.PLATFORM_SPECIAL_CLOSE,radius=7,fill=t.c('panel2'),outline=t.c('primary'),width=2);d.text((371,242),'CLOSE',font=f['tiny'],fill=t.c('primary'))
            return
        if mode=='operations':
            d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,274),t,accent=t.c('primary'),width=2)
            overall=str(self.state.get('overview.state') or '--').upper()
            col=t.c('danger') if overall=='CRITICAL' else t.c('warn') if overall=='ATTENTION' else t.c('accent')
            d.text((20,47),'OPERATIONS CENTER',font=f['medium'],fill=t.c('primary'))
            # Keep the whole-device condition visible without turning it into
            # another equal-weight tile.
            ob=d.textbbox((0,0),overall,font=f['tiny']);ow=max(0,ob[2]-ob[0])
            d.text((454-ow,51),overall,font=f['tiny'],fill=col)

            panel(d,(18,72,304,222),t,accent=t.c('edge'))
            d.text((28,82),'LIVE PLATFORM',font=f['tiny'],fill=t.c('dim'))
            active_services=sum(1 for x in (self.state.get('platform.services') or []) if isinstance(x,dict) and x.get('active')=='active')
            service_total=len(self.state.get('platform.services') or [])
            recent_jobs=len((self.aux.get('jobs') or {}).get('items') or [])
            rows=[
                ('CORE',str(self.state.get('health.core.state') or '--').upper(),f"{self.state.get('health.core.collector_count',0)} collectors"),
                ('SERVICES',f'{active_services}/{service_total}', 'active / tracked'),
                ('TASKS',str(recent_jobs),'recent durable jobs'),
                ('LIBRARY',str(self.state.get('library.document_count',0)),f"{self.state.get('library.text_indexed_count',0)} searchable"),
            ]
            for i,(lab,val,sub) in enumerate(rows):
                y=100+i*29
                d.text((28,y),lab,font=f['tiny'],fill=t.c('dim'))
                d.text((100,y-2),val[:14],font=f['small'],fill=t.c('text'))
                d.text((184,y),sub[:20],font=f['micro'],fill=t.c('info') if i else col)
                if i<3:d.line((28,y+20,294,y+20),fill=t.c('edge'))

            panel(d,(312,72,454,222),t,accent=col)
            att=int(self.state.get('overview.attention_count') or 0)
            d.text((322,82),'ATTENTION',font=f['tiny'],fill=t.c('dim'))
            d.text((322,98),str(att),font=f['large'],fill=t.c('warn') if att else t.c('accent'))
            d.text((350,104),'ITEMS',font=f['tiny'],fill=t.c('dim'))
            d.line((322,126,444,126),fill=t.c('edge'))
            temp=self.state.get('system.temp.cpu_c')
            cpu=self.state.get('system.cpu.total')
            gov=str(self.state.get('governor.mode') or 'FULL').upper()
            d.text((322,138),'TEMP',font=f['micro'],fill=t.c('dim'))
            d.text((375,136),f'{float(temp):.1f}C' if isinstance(temp,(int,float)) else '--',font=f['small'],fill=t.c('warn'))
            d.text((322,158),'CPU',font=f['micro'],fill=t.c('dim'))
            d.text((375,156),f'{float(cpu):.0f}%' if isinstance(cpu,(int,float)) else '--',font=f['small'],fill=t.c('primary'))
            d.text((322,178),'MODE',font=f['micro'],fill=t.c('dim'))
            d.text((375,176),gov[:10],font=f['small'],fill=t.c('secondary'))
            d.text((322,201),'OPEN DETAIL APPS FOR DEPTH',font=f['micro'],fill=t.c('dim'))

            d.text((18,214),'Detail apps keep incidents, services and history one layer deeper.',font=f['micro'],fill=t.c('dim'))
            d.rounded_rectangle(self.PLATFORM_SPECIAL_CLOSE,radius=7,fill=t.c('panel2'),outline=t.c('primary'),width=2)
            d.text((371,242),'CLOSE',font=f['tiny'],fill=t.c('primary'))
            return
        accent={'timeline':'info','notifications':'warn','diagnostics':'warn','services':'accent','hardware':'secondary','storage':'info','operations':'primary','topology':'info','tasks':'secondary','field_library':'accent','missions':'primary','containers':'info','incidents':'warn','backups':'accent','ai_operator':'primary','connectivity':'info','command_center':'accent'}.get(mode,'primary')
        col=t.c(accent,t.c('primary'));d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,274),t,accent=col,width=2)
        labels={
            'notifications':'NOTIFICATIONS','diagnostics':'COLLECTOR HEALTH','services':'SERVICES',
            'hardware':'HARDWARE','storage':'STORAGE','timeline':'TIMELINE','tasks':'TASK CENTER',
            'field_library':'FIELD LIBRARY','missions':'MISSIONS','containers':'CONTAINERS',
            'incidents':'INCIDENTS','backups':'BACKUPS','ai_operator':'AI OPERATOR',
            'connectivity':'CONNECTIVITY','command_center':'COMMAND CENTER',
        }
        title=labels.get(mode,mode.replace('_',' ').upper())
        d.text((20,47),title+' // LIVE',font=f['medium'],fill=col)
        d.text((405,50),f'{page}/{pages}',font=f['small'],fill=t.c('dim'))
        visible=rows[self.platform_offset:self.platform_offset+self.PLATFORM_PAGE_SIZE]
        for i,row in enumerate(visible):
            y=72+i*49;sev=str(row.get('severity') or 'info').lower();vcol=t.c('danger') if sev in {'error','critical'} else t.c('warn') if sev=='warning' else t.c('accent')
            d.text((20,y),str(row.get('title') or '--')[:31],font=f['small'],fill=t.c('text'))
            value=str(row.get('value') or '')[:14];vb=d.textbbox((0,0),value,font=f['tiny']);vw=max(0,vb[2]-vb[0])
            d.text((458-vw,y+1),value,font=f['tiny'],fill=vcol)
            d.text((20,y+18),str(row.get('subtitle') or '')[:67],font=f['tiny'],fill=t.c('dim'))
            if i<self.PLATFORM_PAGE_SIZE-1:d.line((18,y+39,462,y+39),fill=t.c('edge'))
        if not rows:
            empty={
                'notifications':('NO ACTIVE NOTICES','Important events and warnings will appear here.'),
                'incidents':('NO OPEN INCIDENTS','Black Box has no incident rows to surface.'),
                'tasks':('NO RECENT TASKS','Durable background operations will appear here.'),
                'hardware':('NO HARDWARE ROWS','Detected capabilities will appear when available.'),
                'backups':('NO BACKUP ROWS','Create and verify backups from Beast Studio.'),
            }.get(mode,('NO CURRENT ITEMS','This live surface has no rows to display.'))
            d.text((20,100),empty[0],font=f['medium'],fill=t.c('dim'))
            d.text((20,126),empty[1][:68],font=f['tiny'],fill=t.c('dim'))
            d.text((20,151),'Unavailable stays unavailable; Beast does not invent demo state.',font=f['micro'],fill=t.c('warn'))
        for box,bcol in (
            (self.PLATFORM_NAV_PREV,t.c('primary')),
            (self.PLATFORM_NAV_CLOSE,t.c('edge')),
            (self.PLATFORM_NAV_NEXT,t.c('primary')),
        ):
            d.rounded_rectangle(box,radius=7,fill=t.c('panel2'),outline=bcol,width=2)
        d.text((45,242),'<< PREV',font=f['tiny'],fill=t.c('primary'))
        d.text((216,242),'APPS',font=f['tiny'],fill=t.c('text'))
        d.text((369,242),'NEXT >>',font=f['tiny'],fill=t.c('primary'))

    def _studio_status(self,d):
        if not self.studio_overlay:return
        t=self.theme;f=self.fonts;hostname=str(self.state.get('system.hostname') or 'pwnagotchi');services=list(self.state.get('platform.services') or []);status='unknown'
        for row in services:
            if isinstance(row,dict) and row.get('unit')=='beast-studio.service':status=str(row.get('active') or 'unknown');break
        d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,274),t,accent=t.c('primary'),width=2);d.text((20,49),'BEAST STUDIO // WEB CUSTOMIZER',font=f['medium'],fill=t.c('primary'));d.text((20,82),'EXACT 480x320 COMPOSITOR PREVIEW',font=f['small'],fill=t.c('accent'));d.text((20,107),'Draft -> Preview -> Apply -> auto reload',font=f['small'],fill=t.c('text'));d.text((20,137),'STATUS',font=f['tiny'],fill=t.c('dim'));d.text((86,133),status.upper(),font=f['medium'],fill=t.c('accent') if status=='active' else t.c('warn'));d.text((20,164),'PAIRED URL',font=f['tiny'],fill=t.c('dim'));d.text((20,179),f'http://{hostname}.local:8091/',font=f['small'],fill=t.c('info'));d.text((20,204),'SSH: beast-studio-token',font=f['small'],fill=t.c('warn'));d.text((20,220),'Token gates live data + Apply. QR pairing comes next.',font=f['tiny'],fill=t.c('dim'));d.rounded_rectangle((18,238,462,270),radius=7,fill=t.c('panel2'),outline=t.c('primary'));d.text((205,248),'APPS',font=f['small'],fill=t.c('primary'))

    def _visualizers(self,d):
        if not self.visualizer_overlay:return
        t=self.theme;f=self.fonts;d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,274),t,accent=t.c('info'),width=2)
        pids=list(self.RENDERER_CHOICES);page=self.visualizer_offset//2+1;pages=max(1,(len(pids)+1)//2)
        d.text((20,47),'VISUALIZER STUDIO',font=f['medium'],fill=t.c('info'));d.text((398,51),f'{page}/{pages}',font=f['small'],fill=t.c('dim'))
        shown=pids[self.visualizer_offset:self.visualizer_offset+2]
        for i,pid in enumerate(shown):
            y1,y2=(58,142) if i==0 else (150,234);cur=self.renderer_for(pid);choices=self.RENDERER_CHOICES[pid]
            d.rounded_rectangle((18,y1,462,y2),radius=8,fill=t.c('panel2'),outline=t.c('edge'),width=2)
            d.rounded_rectangle((22,y1+4,128,y2-4),radius=7,fill=t.c('ink'),outline=t.c('primary'),width=2)
            d.rounded_rectangle((352,y1+4,458,y2-4),radius=7,fill=t.c('ink'),outline=t.c('primary'),width=2)
            d.text((62,y1+30),'<<',font=f['medium'],fill=t.c('primary'));d.text((394,y1+30),'>>',font=f['medium'],fill=t.c('primary'))
            d.text((145,y1+12),pid.upper(),font=f['tiny'],fill=t.c('dim'));d.text((145,y1+31),cur.upper(),font=f['medium'],fill=t.c('accent'))
            d.text((145,y1+55),f'{choices.index(cur)+1}/{len(choices)} choices',font=f['tiny'],fill=t.c('text'))
        d.rounded_rectangle((12,240,154,274),radius=5,fill=t.c('panel2'),outline=t.c('primary'))
        d.rounded_rectangle((162,240,318,274),radius=5,fill=t.c('panel2'),outline=t.c('edge'))
        d.rounded_rectangle((326,240,468,274),radius=5,fill=t.c('panel2'),outline=t.c('primary'))
        d.text((45,251),'<< PREV',font=f['tiny'],fill=t.c('primary'));d.text((218,251),'BACK',font=f['tiny'],fill=t.c('text'));d.text((370,251),'NEXT >>',font=f['tiny'],fill=t.c('primary'))

    def _theme_library_overlay(self,d):
        if not self.theme_library:return
        t=self.theme;f=self.fonts
        d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,273),t,accent=t.c('primary'),width=2)
        page=self.theme_library_offset//2+1; pages=max(1,(len(self.THEMES)+1)//2)
        d.text((20,47),'THEME LIBRARY',font=f['medium'],fill=t.c('primary'))
        d.text((378,51),f'{page}/{pages}',font=f['small'],fill=t.c('dim'))
        rows=[(58,126),(136,204)]
        for i,(y1,y2) in enumerate(rows):
            idx=self.theme_library_offset+i
            if idx>=len(self.THEMES):continue
            tid=self.THEMES[idx];tp=self._theme_path(tid);th=load_theme(tp) if tp else self.theme;active=tid==self.theme.id
            d.rounded_rectangle((18,y1,458,y2),radius=9,fill=th.c('panel2'),outline=th.c('accent') if active else th.c('primary'),width=3 if active else 2)
            # Larger preview block and bigger text make the entire card obvious.
            d.rounded_rectangle((30,y1+11,112,y2-11),radius=6,fill=th.c('bg'),outline=th.c('accent'))
            d.line((40,y1+26,100,y1+26),fill=th.c('primary'),width=3)
            d.line((40,y1+40,92,y1+40),fill=th.c('secondary'),width=2)
            d.line((40,y1+54,104,y1+54),fill=th.c('accent'),width=2)
            d.text((130,y1+12),th.label,font=f['medium'],fill=th.c('accent'))
            d.text((130,y1+36),f'{th.background.upper()}  //  {th.motion.upper()} MOTION',font=f['small'],fill=th.c('text'))
            d.text((130,y1+56),'TAP ANYWHERE ON THIS CARD',font=f['tiny'],fill=th.c('dim'))
            if active:d.text((390,y1+13),'ACTIVE',font=f['tiny'],fill=th.c('accent'))
        # Large explicit paging controls supplement vertical swipe.
        d.rounded_rectangle((18,216,146,271),radius=7,fill=t.c('panel2'),outline=t.c('primary'),width=2)
        d.rounded_rectangle((158,216,322,271),radius=7,fill=t.c('panel2'),outline=t.c('edge'),width=2)
        d.rounded_rectangle((334,216,462,271),radius=7,fill=t.c('panel2'),outline=t.c('primary'),width=2)
        d.text((44,237),'<< PREV',font=f['small'],fill=t.c('primary'));d.text((216,237),'BACK',font=f['small'],fill=t.c('text'));d.text((365,237),'NEXT >>',font=f['small'],fill=t.c('primary'))

    def _theme_preview_strip(self,d,t,opts):
        x1,y1,x2,y2=20,72,458,104
        d.rectangle((x1,y1,x2,y2),fill=t.c('bg'),outline=t.c('edge'))
        if t.id=='matrix':
            density=str(opts.get('density','dense'));step={'sparse':24,'light':18,'normal':14,'dense':11,'heavy':9,'storm':7,'deluge':5}.get(density,11)
            pal=str(opts.get('palette_mode','green'))
            colors={'green':((0,255,65),(210,255,218)),'cyan':((0,229,255),(225,254,255)),'violet':((190,80,255),(249,231,255)),'red':((255,44,74),(255,225,229)),'amber':((255,174,35),(255,246,198)),'holiday':((255,54,62),(35,255,92))}
            if pal=='custom':
                pcol=palette_color(str(opts.get('primary_color','green')),self.phase,t.c('primary'));hcol=tuple(int(c+(255-c)*.72) for c in pcol)
            else:
                pcol,hcol=colors.get(pal,(t.c('primary'),t.c('matrix_head',t.c('text'))))
            for i,x in enumerate(range(x1+6,x2-4,step)):
                h=10+((i*17+int(self.phase*13))%20);head=y1+4+((i*9+int(self.phase*25))%24)
                col=hcol if i%4==0 else pcol
                d.line((x,max(y1+2,head-h),x,min(y2-2,head)),fill=col,width=1)
        else:
            cols=[t.c('primary'),t.c('secondary'),t.c('accent'),t.c('info')]
            w=(x2-x1)//len(cols)
            for i,c in enumerate(cols):d.rectangle((x1+i*w,y1,x1+(i+1)*w,y2),fill=c)
        d.text((x1+6,y1+4),'LIVE PREVIEW',font=self.fonts['tiny'],fill=t.c('text'))

    def _theme_detail_overlay(self,d):
        if not self.theme_detail:return
        t=self.theme;f=self.fonts;opts=self.options_for_theme(t.id)
        d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,272),t,accent=t.c('accent'),width=2)
        d.rectangle((12,44,468,69),fill=t.c('ink'),outline=t.c('edge'))
        d.text((20,48),t.label.upper(),font=f['medium'],fill=t.c('accent'));d.text((390,51),'CANCEL',font=f['small'],fill=t.c('warn'))
        self._theme_preview_strip(d,t,opts)
        if self._theme_option_rows(t.id):
            rows=self._theme_option_rows(t.id); pages=max(1,(len(rows)+1)//2); self.theme_detail_page=min(self.theme_detail_page,pages-1)
            start=self.theme_detail_page*2; shown=rows[start:start+2]; ys=[106,161]
            d.text((344,91),f'{self.theme_detail_page+1}/{pages}',font=f['tiny'],fill=t.c('dim'))
            for (key,lab,_vals),y in zip(shown,ys):
                val=str(opts.get(key,'')).upper()
                if key=='foreground_fraction':
                    try:val=f'{int(float(val)*100)}%'
                    except Exception:pass
                d.rounded_rectangle((20,y,460,y+51),radius=8,fill=t.c('panel2'),outline=t.c('edge'),width=1)
                d.rounded_rectangle((22,y+2,126,y+49),radius=7,fill=t.c('ink'),outline=t.c('primary'),width=2)
                d.rounded_rectangle((354,y+2,458,y+49),radius=7,fill=t.c('ink'),outline=t.c('primary'),width=2)
                d.text((62,y+17),'<<',font=f['medium'],fill=t.c('primary'));d.text((396,y+17),'>>',font=f['medium'],fill=t.c('primary'))
                d.text((140,y+8),lab,font=f['tiny'],fill=t.c('dim'))
                d.text((140,y+25),val[:18],font=f['medium'],fill=t.c('accent'))
            if self.theme_detail_page==0:
                d.rounded_rectangle((18,216,228,270),radius=8,fill=t.c('panel2'),outline=t.c('warn'),width=2);d.text((82,237),'CANCEL',font=f['small'],fill=t.c('warn'))
                d.rounded_rectangle((244,216,458,270),radius=8,fill=t.c('accent'),outline=t.c('accent'),width=2);d.text((327,237),'NEXT',font=f['small'],fill=t.c('ink'))
            elif self.theme_detail_page<pages-1:
                d.rounded_rectangle((18,216,142,270),radius=8,fill=t.c('panel2'),outline=t.c('primary'),width=2);d.text((58,237),'PREV',font=f['small'],fill=t.c('primary'))
                d.rounded_rectangle((152,216,286,270),radius=8,fill=t.c('panel2'),outline=t.c('warn'),width=2);d.text((190,237),'CANCEL',font=f['small'],fill=t.c('warn'))
                d.rounded_rectangle((296,216,458,270),radius=8,fill=t.c('accent'),outline=t.c('accent'),width=2);d.text((352,237),'NEXT',font=f['small'],fill=t.c('ink'))
            else:
                d.rounded_rectangle((18,216,142,270),radius=8,fill=t.c('panel2'),outline=t.c('primary'),width=2);d.text((58,237),'PREV',font=f['small'],fill=t.c('primary'))
                d.rounded_rectangle((152,216,286,270),radius=8,fill=t.c('panel2'),outline=t.c('warn'),width=2);d.text((190,237),'CANCEL',font=f['small'],fill=t.c('warn'))
                d.rounded_rectangle((296,216,458,270),radius=8,fill=t.c('accent'),outline=t.c('accent'),width=2);d.text((352,237),'APPLY',font=f['small'],fill=t.c('ink'))
        else:
            d.rounded_rectangle((22,108,458,208),radius=7,fill=t.c('panel2'),outline=t.c('edge'))
            d.text((34,117),'FULLSCREEN THEME CARD',font=f['small'],fill=t.c('primary'))
            d.text((34,142),f'Background: {t.background}',font=f['body'],fill=t.c('text'));d.text((34,164),f'Motion: {t.motion}',font=f['body'],fill=t.c('text'))
            d.text((34,186),f'Face: {t.face_style}  //  Reaction: {t.reaction_style}',font=f['body'],fill=t.c('text'))
            d.rounded_rectangle((18,216,228,270),radius=8,fill=t.c('panel2'),outline=t.c('warn'),width=2);d.text((82,237),'CANCEL',font=f['small'],fill=t.c('warn'))
            d.rounded_rectangle((244,216,458,270),radius=8,fill=t.c('accent'),outline=t.c('accent'),width=2);d.text((322,237),'APPLY',font=f['small'],fill=t.c('ink'))

    def _achievement_color(self,row):
        t=self.theme
        if self.achievement_tab=='awards':return t.c('accent') if row.get('unlocked') else t.c('dim')
        return {
            'common':t.c('text'),'uncommon':t.c('info'),'rare':t.c('primary'),
            'epic':t.c('secondary'),'legendary':t.c('warn'),'mythic':t.c('danger'),
        }.get(str(row.get('rarity') or 'common').lower(),t.c('text'))

    def _progress_bar(self,d,box,pct,fill,bg=None):
        x1,y1,x2,y2=box;t=self.theme;bg=bg or t.c('panel')
        d.rounded_rectangle(box,radius=3,fill=bg,outline=t.c('edge'),width=1)
        p=max(0.0,min(100.0,float(pct or 0)))/100.0
        if p>0:
            xx=x1+max(2,int((x2-x1)*p))
            d.rounded_rectangle((x1+1,y1+1,min(x2-1,xx),y2-1),radius=2,fill=fill)

    def _achievement_detail_row(self):
        ident=str(self.achievement_detail or '')
        source=(self.state.get('progression.awards.catalog') or []) if self.achievement_tab=='awards' else (self.state.get('progression.achievements.catalog') or [])
        for row in source:
            if isinstance(row,dict) and str(row.get('id') or '')==ident:return dict(row)
        return None

    def _achievements(self,d):
        if not self.achievements_overlay:return
        t=self.theme;f=self.fonts
        d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(8,40,472,273),t,accent=t.c('accent'),width=2)

        if self.achievement_detail:
            row=self._achievement_detail_row()
            if not row:
                self.achievement_detail=None
                return self._achievements(d)
            col=self._achievement_color(row); unlocked=bool(row.get('unlocked'))
            d.text((20,49),'AWARD DETAIL' if self.achievement_tab=='awards' else 'ACHIEVEMENT DETAIL',font=f['medium'],fill=t.c('accent'))
            d.text((20,77),str(row.get('label') or '???')[:45],font=f['large'],fill=col if unlocked else t.c('dim'))
            status='UNLOCKED' if unlocked else 'LOCKED'
            rarity=str(row.get('rarity') or row.get('kind') or '').upper()
            d.text((20,104),status,font=f['small'],fill=t.c('accent') if unlocked else t.c('dim'))
            if rarity:d.text((112,104),rarity[:16],font=f['small'],fill=col)
            cur=row.get('current',0);target=row.get('target',0);pct=float(row.get('progress_pct') or 0)
            self._progress_bar(d,(20,126,460,142),pct,col)
            if str(row.get('metric') or '')=='runtime_sec':
                curtxt=f'{float(cur)/3600:.1f}h / {float(target)/3600:.0f}h'
            else:
                try:curtxt=f'{int(float(cur)):,} / {int(float(target)):,}'
                except Exception:curtxt=f'{cur} / {target}'
            d.text((20,149),f'PROGRESS  {curtxt}  //  {pct:.0f}%',font=f['small'],fill=t.c('text'))
            desc=str(row.get('description') or '')
            for i,line in enumerate(textwrap.wrap(desc,width=58)[:3]):
                d.text((20,174+i*15),line,font=f['small'],fill=t.c('text'))
            if self.achievement_tab=='achievements':
                bonus=int(row.get('bonus_xp') or 0);d.text((20,216),f'REWARD // +{bonus} XP',font=f['small'],fill=t.c('warn'))
            d.rounded_rectangle((18,238,462,270),radius=7,fill=t.c('panel2'),outline=t.c('primary'),width=2)
            d.text((204,248),'BACK',font=f['small'],fill=t.c('primary'))
            return

        # Top-level tabs are intentionally large: the entire half-width region is a hit target.
        ach_active=self.achievement_tab=='achievements'
        d.rounded_rectangle((12,42,232,78),radius=6,fill=t.c('panel2') if not ach_active else t.c('accent'),outline=t.c('accent'))
        d.rounded_rectangle((248,42,468,78),radius=6,fill=t.c('panel2') if ach_active else t.c('accent'),outline=t.c('accent'))
        d.text((70,53),'ACHIEVEMENTS',font=f['small'],fill=t.c('ink') if ach_active else t.c('text'))
        d.text((316,53),'AWARDS',font=f['small'],fill=t.c('text') if ach_active else t.c('ink'))

        d.rounded_rectangle((12,82,232,118),radius=5,fill=t.c('panel2'),outline=t.c('edge'))
        d.rounded_rectangle((248,82,468,118),radius=5,fill=t.c('panel2'),outline=t.c('edge'))
        d.text((31,87),f'FILTER // {self.achievement_filter.upper()}',font=f['small'],fill=t.c('primary'))
        d.text((257,87),f'SORT // {self.achievement_sort.upper()}',font=f['small'],fill=t.c('secondary'))

        rows=self._achievement_rows(); pages=max(1,(len(rows)+1)//2); page=min(pages,max(1,self.achievement_offset//2+1))
        shown=rows[self.achievement_offset:self.achievement_offset+2]
        for row,y1,y2 in [(shown[0] if len(shown)>0 else None,122,178),(shown[1] if len(shown)>1 else None,183,237)]:
            if row is None:continue
            col=self._achievement_color(row);unlocked=bool(row.get('unlocked'));pct=float(row.get('progress_pct') or 0)
            d.rounded_rectangle((12,y1,468,y2),radius=7,fill=t.c('panel2'),outline=col if unlocked else t.c('edge'),width=2 if unlocked else 1)
            marker='✓' if unlocked else 'LOCK'
            d.text((28,y1+8),marker,font=f['small'],fill=col if unlocked else t.c('dim'))
            d.text((76,y1+7),str(row.get('label') or '???')[:39],font=f['small'],fill=col if unlocked else t.c('dim'))
            if self.achievement_tab=='achievements':
                d.text((382,y1+7),str(row.get('rarity') or '').upper()[:5],font=f['tiny'],fill=col if unlocked else t.c('dim'))
            else:
                d.text((382,y1+7),str(row.get('kind') or '').upper()[:8],font=f['tiny'],fill=col if unlocked else t.c('dim'))
            self._progress_bar(d,(76,y1+29,430,y1+40),pct,col if unlocked else t.c('dim'))
            try:cur=int(float(row.get('current') or 0));target=int(float(row.get('target') or 0));ct=f'{cur:,}/{target:,}'
            except Exception:ct=''
            d.text((76,y1+44),f'{pct:.0f}%  {ct}',font=f['tiny'],fill=t.c('dim'))

        d.rounded_rectangle((12,242,154,274),radius=5,fill=t.c('panel2'),outline=t.c('primary'))
        d.rounded_rectangle((162,242,318,274),radius=5,fill=t.c('panel2'),outline=t.c('edge'))
        d.rounded_rectangle((326,242,468,274),radius=5,fill=t.c('panel2'),outline=t.c('primary'))
        d.text((44,252),'<< PREV',font=f['tiny'],fill=t.c('primary'));d.text((211,252),f'BACK  {page}/{pages}',font=f['tiny'],fill=t.c('text'));d.text((368,252),'NEXT >>',font=f['tiny'],fill=t.c('primary'))

    def _help(self,d):
        if not self.help_overlay:return
        t=self.theme;f=self.fonts;d.rectangle((0,34,480,278),fill=t.c('ink'));panel(d,(10,42,470,269),t,accent=t.c('accent'),width=2)
        d.text((22,51),'CONTROLS // LIVE REFERENCE',font=f['medium'],fill=t.c('accent'))
        page=self.pages.IDS[self.page]; rows=rows_for(page)
        for i,(k,v) in enumerate(rows[:7]):
            y=76+i*21;d.text((24,y),k,font=f['small'],fill=t.c('primary'));d.text((174,y),v,font=f['small'],fill=t.c('text'))
        d.text((24,229),hint_for(page)[:72],font=f['tiny'],fill=t.c('dim'))
        d.rounded_rectangle((250,244,458,266),radius=5,fill=t.c('panel2'),outline=t.c('primary'));d.text((267,251),'SHOW TOUCH ZONES',font=f['tiny'],fill=t.c('primary'))
        d.text((24,252),'Swipe up or tap footer to close',font=f['tiny'],fill=t.c('accent'))

    def _touch_zones(self,d):
        if not self.touch_zones_overlay:return
        t=self.theme;f=self.fonts
        for x1,y1,x2,y2,label in TOUCH_ZONES:
            d.rectangle((x1,y1,x2,y2),outline=t.c('warn'),width=2);d.text((x1+4,max(281,y1+2)),label,font=f['tiny'],fill=t.c('warn'))
        d.rectangle((0,34,480,277),outline=t.c('warn'),width=1);d.text((315,39),'TOUCH ZONES ON',font=f['tiny'],fill=t.c('warn'))

    def _write_runtime(self,total_ms,compose_ms,write_ms):
        if self.output is not None:return
        try:
            self._render_samples.append(float(total_ms)); self._render_samples=self._render_samples[-180:]
            self._compose_samples.append(float(compose_ms)); self._compose_samples=self._compose_samples[-180:]
            self._write_samples.append(float(write_ms)); self._write_samples=self._write_samples[-180:]
            self._frame_count+=1
            if self._frame_count % 8:return
            avg=lambda rows: sum(rows)/len(rows) if rows else 0.0
            elapsed=max(0.001,time.monotonic()-self._runtime_started)
            obj={
                'version':UI_VERSION,'theme':self.theme.id,'page':self.pages.IDS[self.page],
                'frames':self._frame_count,'avg_render_ms':round(avg(self._render_samples),2),'max_render_ms':round(max(self._render_samples or [0]),2),
                'avg_compose_ms':round(avg(self._compose_samples),2),'avg_fb_write_ms':round(avg(self._write_samples),2),'max_fb_write_ms':round(max(self._write_samples or [0]),2),
                'target_fps':round(self.adaptive_fps(),1),'lifetime_fps':round(self._frame_count/elapsed,2),
                'drawer':self.drawer,'help':self.help_overlay,'touch_zones':self.touch_zones_overlay,
                'spectrum_renderer':self.renderer_for('spectrum'),'data_error':self.data_error,'native_pwnagotchi':self.native_source.info().__dict__ if self._is_native_theme() else None,
                'framebuffer':self.fb.telemetry(),'display':self.display_transform.metadata(),
                'scene':self.scene_runtime.snapshot(),'compositor_cache':compositor_cache_telemetry(),'ts':time.time(),
            }
            self.runtime_path.parent.mkdir(parents=True,exist_ok=True); self.runtime_path.write_text(json.dumps(obj,separators=(',',':'))+'\n')
        except Exception:log.debug('runtime telemetry write failed',exc_info=True)

    def _compose_native(self):
        self.phase=float(self.phase_override) if self.phase_override is not None else time.monotonic()
        mode=self._native_mode()
        opts=self.options_for_theme(self.theme.id)
        ink=self._native_ink_color()
        glow_level=str(opts.get('glow_level','soft')) if mode=='chroma' else 'off'
        glow_strength={'off':0.0,'soft':1.0,'strong':2.0}.get(glow_level,1.0)
        im=self.native_source.render(
            mode=mode, size=(480,320), ink_color=ink,
            background_color=self.theme.c('bg'), glow=glow_strength
        )
        if im is not None and mode=='chroma':
            im=apply_native_effects(im,self.phase,opts,ink=ink)
        if im is None:
            # Fail visibly rather than silently substituting a replica. This is
            # important: the NATIVE profiles promise the actual Jayofelony frame.
            im=Image.new('RGB',(480,320),self.theme.c('bg'))
            d=ImageDraw.Draw(im)
            d.text((20,34),'PWNAGOTCHI NATIVE FRAME UNAVAILABLE',font=self.fonts['medium'],fill=self.theme.c('warn'))
            d.text((20,62),'/var/tmp/pwnagotchi/pwnagotchi.png',font=self.fonts['small'],fill=self.theme.c('text'))
            info=self.native_source.info()
            d.text((20,82),(info.error or 'waiting for Pwnagotchi UI frame')[:70],font=self.fonts['tiny'],fill=self.theme.c('dim'))
            d.text((20,112),'Long-press to open Beast Control Center.',font=self.fonts['small'],fill=self.theme.c('accent'))
        d=ImageDraw.Draw(im)
        # No Beast header/footer/event reaction/scanline is painted in Native
        # Dark/Light: the untouched Jayofelony composition is the point.
        # Chroma only recolors/glows the exact native foreground mask.
        self._drawer(d);self._apps_overlay(d);self._telemetry_inspector(d);self._widget_inspector(d);self._correlation_lab(d);self._plugins_manager(d);self._beastdex(d);self._capture_vault(d);self._performance_lab(d);self._platform_browser(d);self._studio_status(d);self._visualizers(d);self._theme_library_overlay(d);self._theme_detail_overlay(d);self._achievements(d);self._help(d);self._touch_zones(d)
        # Monster reveals remain available above Native; Rare Moments still win final priority.
        im=render_monster_reveal(im,self.state,self.phase,self.theme,self.fonts,dismissed_id=self.monster_reveal_dismissed_id)
        return render_rare_overlay(im,self.state,self.phase,self.theme,self.fonts)

    def _background_cadence(self,opts):
        """Intentional ambient-layer cadence, independent of touch/data FPS."""
        kind=str(getattr(self.theme,'background','none'))
        if kind=='none':return 0.0
        if kind=='grid':return 3.0 if str(opts.get('pulse_level','off'))!='off' else 0.0
        if kind=='matrix':return 6.0
        if kind=='starfield':return 4.0 if str(opts.get('twinkle','off'))!='off' else 0.0
        if kind=='ice':return 3.0 if str(opts.get('drift','still'))!='still' else 0.0
        if kind=='hunter':return 4.0 if str(opts.get('reticle','off'))!='off' else 0.0
        if kind=='synthwave':return 3.0 if str(opts.get('stars','off'))!='off' else 0.0
        if kind=='tactical':return 5.0 if str(opts.get('sweep','off'))!='off' else 0.0
        if kind=='ghost':return 1.5 if str(opts.get('ambient','off'))!='off' else 0.0
        if kind=='cyberpunk':return 4.0 if str(opts.get('rain','off'))!='off' or str(opts.get('glitch','off'))!='off' else 0.0
        if kind=='wopr':return 4.0 if str(opts.get('sweep','off'))!='off' or str(opts.get('blips','off'))!='off' else 0.0
        if kind=='lcars':return 2.5 if str(opts.get('pulse','off'))!='off' else 0.0
        if kind=='crt':return 3.0 if str(opts.get('noise','off'))!='off' else 0.0
        return 2.0

    def _background_frame(self):
        opts=self.render_options_for_theme(self.theme.id)
        try:key=(self.theme.id,json.dumps(opts,sort_keys=True,default=str))
        except Exception:key=(self.theme.id,str(opts))
        now=time.monotonic();fps=self._background_cadence(opts);due=self._bg_cache is None or key!=self._bg_cache_key or fps<=0 or now-self._bg_cache_at>=1.0/max(.1,fps)
        # fps==0 means static: render once per key, not every frame.
        if fps<=0 and self._bg_cache is not None and key==self._bg_cache_key:due=False
        if due:
            bg=Image.new('RGB',(480,320),self.theme.c('bg'));bd=ImageDraw.Draw(bg);draw_background(bd,self.theme,self.phase,opts)
            self._bg_cache=bg;self._bg_cache_key=key;self._bg_cache_at=now
        return self._bg_cache.copy() if self._bg_cache is not None else Image.new('RGB',(480,320),self.theme.c('bg'))

    def _compose(self,page_idx):
        if self._is_native_theme():
            return self._compose_native()
        self.phase=float(self.phase_override) if self.phase_override is not None else time.monotonic();im=self._background_frame();d=ImageDraw.Draw(im)
        page_id=self.pages.IDS[page_idx];title=self.pages.TITLES[page_id]
        self.scene_runtime.begin(page_id=page_id,scene_id=f'page:{page_id}',theme_id=self.theme.id)
        self.scene_runtime.update_signals(self.state)
        if page_id=='dashboard' and self.active_board_id:title=next((str(b.get('label') or b.get('id')) for b in self._all_boards() if str(b.get('id'))==self.active_board_id),title)
        self._header(d,title);getattr(self.pages,page_id)(d,self.state,self);self.scene_runtime.end()
        im=draw_foreground_effects(im,self.theme,self.phase,self.render_options_for_theme(self.theme.id));d=ImageDraw.Draw(im)
        self._event_reaction(d);self._physical_test_overlay(d);self._footer(d,page_idx);self._drawer(d);self._apps_overlay(d);self._telemetry_inspector(d);self._widget_inspector(d);self._correlation_lab(d);self._plugins_manager(d);self._beastdex(d);self._capture_vault(d);self._performance_lab(d);self._platform_browser(d);self._studio_status(d);self._visualizers(d);self._theme_library_overlay(d);self._theme_detail_overlay(d);self._achievements(d);self._help(d);self._touch_zones(d)
        _scanline_opt=str(self.render_options_for_theme(self.theme.id).get('scanline','on')).lower()
        if self.theme.scanlines and _scanline_opt!='off':
            speed=float(getattr(self.theme,'scanline_speed',31.0) or 31.0);width=max(1,int(getattr(self.theme,'scanline_width',1) or 1));y=35+int((self.phase*speed)%240)
            # Protected scanline layer: always painted after normal/foreground
            # theme effects so Matrix rain can never segment it.
            col=self.theme.c('scanline',self.theme.c('edge'));d.rectangle((0,y,479,y+width-1),fill=col)
        # Machine-readable transport must remain above theme scanlines/effects.
        # A decorative sweep through a QR can make a mathematically valid code
        # physically unscannable. Monster/Rare overlays intentionally retain
        # higher precedence than ordinary transport UI.
        self._capsule_share_view(d)
        # Monster reveals are celebratory, but Rare Moments remain the absolute top layer.
        im=render_monster_reveal(im,self.state,self.phase,self.theme,self.fonts,dismissed_id=self.monster_reveal_dismissed_id)
        im=render_rare_overlay(im,self.state,self.phase,self.theme,self.fonts)
        return im

    def render(self):
        total_started=time.perf_counter();self._reload_external_prefs();self._sync_feed();compose_started=time.perf_counter()
        if self.transition:
            now=time.monotonic();tr=self.transition;p=min(1.0,(now-tr['started'])/tr['duration']);e=p*p*(3-2*p);old=self._compose(tr['old']);new=self._compose(tr['new']);canvas=Image.new('RGB',(480,320),self.theme.c('bg'));direction=tr['direction'];old_x=int((-480*e) if direction>0 else (480*e));new_x=int((480*(1-e)) if direction>0 else (-480*(1-e)));canvas.paste(old,(old_x,0));canvas.paste(new,(new_x,0));im=canvas
            if p>=1:self.transition=None
            else:self.dirty.set()
        else:im=self._compose(self.page)
        compose_ms=(time.perf_counter()-compose_started)*1000.0
        physical_im=self.display_transform.to_physical(im)
        write_started=time.perf_counter();self.fb.write(physical_im);write_ms=(time.perf_counter()-write_started)*1000.0
        self.last_render=time.monotonic();self._write_runtime((time.perf_counter()-total_started)*1000.0,compose_ms,write_ms);return physical_im

    def run(self,duration=0.0):
        log.info('Beast UI start root=%s output=%s theme=%s',self.root,self.output,self.theme.id)
        if self.output is None:
            self.feed=DataFeed(self.dirty,extra_history_keys=tuple(dashboard_history_keys(self._active_dashboard_widgets()))+tuple(self.correlation_keys));self.feed.start()
            # Allow the local feed one short moment to get the first snapshot.
            deadline=time.monotonic()+0.35
            while time.monotonic()<deadline:
                self._sync_feed()
                if self.state:break
                time.sleep(.02)
        if self.touch:self.touch.start()
        start=time.monotonic();self.render()
        try:
            while not self.stop_event.is_set():
                now=time.monotonic()
                if duration and now-start>=duration:break
                fps=max(1.0,self.adaptive_fps());interval=1.0/fps;due=(now-self.last_render)>=interval
                # Dirty means "render at the next frame budget", not "render immediately".
                # A static page no longer burns CPU by redrawing just because its
                # theme declares motion. Ambient layers request their own cadence.
                if due and (self.dirty.is_set() or self._dynamic_frame_due(now)):
                    self.dirty.clear();self.render()
                time.sleep(.008)
        finally:
            self.stop_event.set()
            if self.feed:self.feed.stop();self.feed.join(timeout=1)
            if self.touch:self.touch.stop();self.touch.join(timeout=1)
            self.fb.close()
