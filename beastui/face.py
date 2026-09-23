from __future__ import annotations
import math
from pathlib import Path
from PIL import ImageFont

from .facepacks import discover_enabled_face_profiles
from .animationpacks import discover_enabled_animation_profiles

PWN_CLASSIC_FACES={
    "look_r":"( ⚆_⚆)", "look_l":"(☉_☉ )", "look_r_happy":"( ◕‿◕)", "look_l_happy":"(◕‿◕ )",
    "sleep":"(⇀‿‿↼)", "sleep2":"(≖‿‿≖)", "awake":"(◕‿‿◕)", "bored":"(-__-)",
    "intense":"(°▃▃°)", "cool":"(⌐■_■)", "happy":"(•‿‿•)", "grateful":"(^‿‿^)",
    "excited":"(ᵔ◡◡ᵔ)", "motivated":"(☼‿‿☼)", "demotivated":"(≖__≖)", "smart":"(✜‿‿✜)",
    "lonely":"(ب__ب)", "sad":"(╥☁╥ )", "angry":"(-_-')", "friend":"(♥‿‿♥)",
    "broken":"(☓‿‿☓)", "debug":"(#__#)", "upload":"(1__0)", "upload1":"(1__1)", "upload2":"(0__1)",
    "waiting":"(⇀‿‿↼)", "alert":"(°▃▃°)", "curious":"( ◕‿◕)"
}


class FaceEngine:
    EXPRESSIONS=set(PWN_CLASSIC_FACES)

    def __init__(self, profile_id: str = "builtin", animation_profile_id: str = "none", *, installed_root: str | Path = "/var/lib/beastagotchi/packs/installed"):
        self.installed_root=Path(installed_root)
        self.profiles={};self.animation_profiles={}
        self.profile_id="builtin";self.animation_profile_id="none"
        self.refresh_profiles();self.refresh_animation_profiles()
        self.set_profile(profile_id);self.set_animation_profile(animation_profile_id)

    def refresh_profiles(self):
        self.profiles=discover_enabled_face_profiles(self.installed_root)
        if self.profile_id!="builtin" and self.profile_id not in self.profiles:self.profile_id="builtin"
        return self.profiles

    def refresh_animation_profiles(self):
        self.animation_profiles=discover_enabled_animation_profiles(self.installed_root)
        if self.animation_profile_id!="none" and self.animation_profile_id not in self.animation_profiles:self.animation_profile_id="none"
        return self.animation_profiles

    def set_animation_profile(self, profile_id: str):
        profile_id=str(profile_id or "none")
        self.animation_profile_id=profile_id if profile_id=="none" or profile_id in self.animation_profiles else "none"
        return self.animation_profile_id

    def animation_profile_options(self):
        rows=[{"id":"none","label":"None · static face motion","source_pack":None,"target":"face"}]
        for pid,row in sorted(self.animation_profiles.items(),key=lambda x:(str(x[1].get("label") or x[0]).lower(),x[0])):
            rows.append({"id":pid,"label":str(row.get("label") or pid),"source_pack":row.get("source_pack"),"target":row.get("target")})
        return rows

    def set_profile(self, profile_id: str):
        profile_id=str(profile_id or "builtin")
        self.profile_id=profile_id if profile_id=="builtin" or profile_id in self.profiles else "builtin"
        return self.profile_id

    def profile_options(self):
        rows=[{"id":"builtin","label":"Built-in · follows theme","source_pack":None,"renderer":"builtin"}]
        for pid,row in sorted(self.profiles.items(),key=lambda x:(str(x[1].get("label") or x[0]).lower(),x[0])):
            rows.append({"id":pid,"label":str(row.get("label") or pid),"source_pack":row.get("source_pack"),"renderer":row.get("renderer")})
        return rows

    def resolve(self,state:dict)->dict:
        beast=str(state.get('beast.expression') or '').lower()
        mapping={
            'idle':'awake','curious':'curious','hunting':'intense','focused':'smart',
            'gps-searching':'waiting','celebrating':'excited','sleepy':'sleep',
            'sleeping':'sleep2','bored':'bored','overheated':'alert','warning':'alert',
            'fault':'broken','reconnecting':'waiting','surprised':'excited','smug':'cool',
        }
        mood=mapping.get(beast) if beast else None
        if not mood:mood=str(state.get('pwnagotchi.mood') or 'awake').lower()
        if mood not in self.EXPRESSIONS:mood='awake'
        thermal=state.get('system.thermal.band'); health=state.get('health.core.state')
        if health in {'critical','failed'}:mood='broken'
        elif health and health not in {'healthy','starting'}:mood='alert'
        elif thermal in {'hot','critical'}:mood='alert'
        return {"mood":mood,"beast_expression":beast or None,"context":str(state.get('context.mode.effective') or 'pwn'),"tags":list(state.get('context.visual.tags') or [])}

    @staticmethod
    def _color(theme,role,default='primary'):
        try:return theme.c(str(role or default))
        except Exception:return theme.c(default)

    @staticmethod
    def _pt(box,p):
        x1,y1,x2,y2=box;w=x2-x1;h=y2-y1
        return (int(x1+w*float(p[0])/1000.0),int(y1+h*float(p[1])/1000.0))

    @classmethod
    def _box(cls,box,b):
        p1=cls._pt(box,(b[0],b[1]));p2=cls._pt(box,(b[2],b[3]))
        return (min(p1[0],p2[0]),min(p1[1],p2[1]),max(p1[0],p2[0]),max(p1[1],p2[1]))

    def _draw_pack_overlays(self,d,box,theme,face,phase):
        x1,y1,x2,y2=box;cx=(x1+x2)//2;w=x2-x1;h=y2-y1
        if 'goggles' in face['tags']:
            ew=max(20,int(w*.23));eh=max(14,int(h*.18));gap=max(8,int(w*.05));gy=y1+max(8,int(h*.26))
            d.rounded_rectangle((cx-gap-ew,gy,cx-gap,gy+eh),radius=5,outline=theme.c('accent'),width=2)
            d.rounded_rectangle((cx+gap,gy,cx+gap+ew,gy+eh),radius=5,outline=theme.c('accent'),width=2)
            d.line((cx-gap,gy+eh//2,cx+gap,gy+eh//2),fill=theme.c('accent'),width=2)
        if 'wind' in face['tags']:
            for i in range(3):
                yy=y1+15+i*18+int(math.sin(phase*3+i)*3);d.line((x1+5,yy,x1+28+i*6,yy),fill=theme.c('dim'))

    def _draw_pack_profile(self,d,box,theme,state,phase,profile):
        face=self.resolve(state);mood=face['mood']
        expressions=profile.get('expressions') or {}
        expression=expressions.get(mood) or expressions.get(profile.get('fallback')) or next(iter(expressions.values()),None)
        if expression is None:return False
        if profile.get('background')=='panel':d.rectangle(box,fill=theme.c('panel'))
        if profile.get('renderer')=='glyph':
            glyph=str(expression)
            x1,y1,x2,y2=box;target=max(12,min(64,int((y2-y1)*float(profile.get('font_size_ratio') or .30))))
            try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",target)
            except Exception:font=ImageFont.load_default()
            try:
                bb=d.textbbox((0,0),glyph,font=font);tw=bb[2]-bb[0];th=bb[3]-bb[1]
            except Exception:
                tw=float(d.textlength(glyph,font=font));th=target
            d.text((int(x1+(x2-x1-tw)/2),int(y1+(y2-y1-th)/2)-2),glyph,font=font,fill=self._color(theme,profile.get('color_role'),'primary'))
        elif profile.get('renderer')=='vector':
            for primitive in expression:
                kind=primitive.get('type');stroke=self._color(theme,primitive.get('stroke'),'primary') if primitive.get('stroke') else None
                fill=self._color(theme,primitive.get('fill'),'primary') if primitive.get('fill') else None;width=max(1,int(primitive.get('width') or 1))
                if kind=='line':
                    pts=[self._pt(box,p) for p in primitive.get('points') or []]
                    if len(pts)>=2:d.line(pts,fill=stroke,width=width,joint='curve')
                elif kind=='polygon':
                    pts=[self._pt(box,p) for p in primitive.get('points') or []]
                    if len(pts)>=3:d.polygon(pts,fill=fill,outline=stroke)
                elif kind=='ellipse':
                    d.ellipse(self._box(box,primitive.get('box')),fill=fill,outline=stroke,width=width)
                elif kind=='rectangle':
                    d.rectangle(self._box(box,primitive.get('box')),fill=fill,outline=stroke,width=width)
                elif kind=='rounded_rectangle':
                    radius=max(0,int(min(box[2]-box[0],box[3]-box[1])*float(primitive.get('radius') or 0)/1000.0))
                    d.rounded_rectangle(self._box(box,primitive.get('box')),radius=radius,fill=fill,outline=stroke,width=width)
                elif kind=='arc':
                    d.arc(self._box(box,primitive.get('box')),float(primitive.get('start',0)),float(primitive.get('end',180)),fill=stroke,width=width)
        else:return False
        self._draw_pack_overlays(d,box,theme,face,phase)
        return True

    def _animation_state(self,box,state,phase):
        profile=self.animation_profiles.get(self.animation_profile_id)
        if not profile:return box,None
        face=self.resolve(state);mul=float((profile.get("reactive") or {}).get(face["mood"],1.0));p=float(phase)*mul
        motion=profile.get("motion") or {};x1,y1,x2,y2=box
        bob=float(motion.get("bob_px") or 0)*math.sin((2*math.pi*p)/max(.8,float(motion.get("bob_period_s") or 4)))
        sway=float(motion.get("sway_px") or 0)*math.sin((2*math.pi*p)/max(.8,float(motion.get("sway_period_s") or 6)))
        breath=float(motion.get("breath_px") or 0)*math.sin((2*math.pi*p)/max(1.0,float(motion.get("breath_period_s") or 5)))
        moved=(int(round(x1+sway-breath)),int(round(y1+bob-breath)),int(round(x2+sway+breath)),int(round(y2+bob+breath)))
        return moved,profile

    def _draw_animation_overlay(self,d,box,theme,phase,profile,state):
        if not profile:return
        orbit=profile.get("orbit") or {};count=int(orbit.get("count") or 0)
        if count<=0:return
        face=self.resolve(state);mul=float((profile.get("reactive") or {}).get(face["mood"],1.0));p=float(phase)*mul
        x1,y1,x2,y2=box;cx=(x1+x2)/2;cy=(y1+y2)/2;r=min(x2-x1,y2-y1)*float(orbit.get("radius_pct") or 48)/100.0
        speed=float(orbit.get("speed_rps") or .06);dot=max(1,int(orbit.get("dot_radius_px") or 2));col=self._color(theme,orbit.get("color_role"),"accent")
        for i in range(count):
            a=2*math.pi*(p*speed+i/count);x=int(cx+math.cos(a)*r);y=int(cy+math.sin(a)*r)
            d.ellipse((x-dot,y-dot,x+dot,y+dot),fill=col)

    def draw(self,d,box,theme,state,phase):
        moved,anim=self._animation_state(box,state,phase)
        profile=self.profiles.get(self.profile_id)
        if profile:
            if self._draw_pack_profile(d,moved,theme,state,phase,profile):
                self._draw_animation_overlay(d,moved,theme,phase,anim,state);return
        style=getattr(theme,'face_style','classic')
        fn=getattr(self,f'draw_{style}',self.draw_classic)
        fn(d,moved,theme,state,phase)
        self._draw_animation_overlay(d,moved,theme,phase,anim,state)

    def _features(self,d,box,theme,state,phase,eye_shape='rect',mouth=True):
        x1,y1,x2,y2=box; w=x2-x1; h=y2-y1; face=self.resolve(state); mood=face['mood']
        p=theme.c('primary'); a=theme.c('accent'); dim=theme.c('dim')
        cx=(x1+x2)//2; ey=y1+int(h*.39); gap=int(w*.13); ew=max(13,int(w*.18)); eh=max(8,int(h*.12))
        blink=(int(phase*2.2)%17==0) and mood not in {'alert','excited'}
        if mood=='sleep':
            d.arc((cx-gap-ew,ey-3,cx-gap,ey+10),10,170,fill=p,width=2); d.arc((cx+gap,ey-3,cx+gap+ew,ey+10),10,170,fill=p,width=2)
        else:
            for ex in (cx-gap-ew,cx+gap):
                if blink:d.line((ex,ey+eh//2,ex+ew,ey+eh//2),fill=p,width=2);continue
                if eye_shape=='ellipse': d.ellipse((ex,ey,ex+ew,ey+eh),outline=p,width=2)
                elif eye_shape=='slash':
                    if ex<cx:d.line((ex,ey,ex+ew,ey+eh//2),fill=p,width=3)
                    else:d.line((ex,ey+eh//2,ex+ew,ey),fill=p,width=3)
                else:d.rounded_rectangle((ex,ey,ex+ew,ey+eh),radius=3,outline=p,width=2)
                if eye_shape!='slash':
                    pupil=4 if mood in {'alert','excited'} else 3; d.ellipse((ex+ew//2-pupil,ey+eh//2-pupil,ex+ew//2+pupil,ey+eh//2+pupil),fill=a)
        if mouth:
            my=y1+int(h*.66)
            if mood in {'sad','bored'}:d.arc((cx-22,my,cx+22,my+22),200,340,fill=p,width=2)
            elif mood in {'excited','curious'}:d.arc((cx-23,my-12,cx+23,my+14),15,165,fill=p,width=2)
            elif mood=='alert':d.line((cx-19,my,cx-7,my+5,cx+6,my-5,cx+19,my),fill=p,width=2)
            else:d.line((cx-20,my,cx-8,my+5,cx+8,my+5,cx+20,my),fill=p,width=2)
        if 'goggles' in face['tags']:
            gy=ey-5
            d.rounded_rectangle((cx-gap-ew-5,gy,cx-gap+5,gy+eh+10),radius=5,outline=a,width=2)
            d.rounded_rectangle((cx+gap-5,gy,cx+gap+ew+5,gy+eh+10),radius=5,outline=a,width=2)
            d.line((cx-gap+5,gy+eh//2+5,cx+gap-5,gy+eh//2+5),fill=a,width=2)
        if 'wind' in face['tags']:
            for i in range(3):
                yy=y1+15+i*18+int(math.sin(phase*3+i)*3); d.line((x1+5,yy,x1+28+i*6,yy),fill=dim)

    def draw_pwnclassic(self,d,box,theme,state,phase):
        x1,y1,x2,y2=box
        d.rectangle(box,fill=theme.c("panel"))
        face=self.resolve(state); mood=face["mood"]
        glyph=PWN_CLASSIC_FACES.get(mood,PWN_CLASSIC_FACES["awake"])
        mood_colors=getattr(theme,"mood_colors",None) or {}
        color=mood_colors.get(mood,theme.c("primary"))
        target=max(18,min(42,int((y2-y1)*0.29)))
        try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",target)
        except Exception:font=ImageFont.load_default()
        try:
            bb=d.textbbox((0,0),glyph,font=font); tw=bb[2]-bb[0]; th=bb[3]-bb[1]
        except Exception:
            tw=float(d.textlength(glyph,font=font)); th=target
        tx=int(x1+(x2-x1-tw)/2); ty=int(y1+(y2-y1-th)/2)-2
        d.text((tx,ty),glyph,font=font,fill=color)
        if "goggles" in face["tags"]:
            gy=max(y1+8,ty-4); cx=(x1+x2)//2
            d.rounded_rectangle((cx-66,gy,cx-8,gy+24),radius=5,outline=theme.c("accent"),width=2)
            d.rounded_rectangle((cx+8,gy,cx+66,gy+24),radius=5,outline=theme.c("accent"),width=2)
            d.line((cx-8,gy+12,cx+8,gy+12),fill=theme.c("accent"),width=2)
        if "wind" in face["tags"]:
            for i in range(3):
                yy=y1+18+i*20+int(math.sin(phase*3+i)*2)
                d.line((x1+6,yy,x1+30+i*6,yy),fill=theme.c("dim"))

    def draw_classic(self,d,box,theme,state,phase):
        d.rectangle(box,fill=theme.c('panel'),outline=theme.c('edge')); self._features(d,box,theme,state,phase)
    def draw_matrix(self,d,box,theme,state,phase):
        d.rectangle(box,fill=theme.c('panel'),outline=theme.c('primary'))
        x1,y1,x2,y2=box; d.line((x1+18,y1+35,x1+35,y1+8,x1+55,y1+34),fill=theme.c('primary'),width=2); d.line((x2-55,y1+34,x2-35,y1+8,x2-18,y1+35),fill=theme.c('primary'),width=2)
        self._features(d,box,theme,state,phase,eye_shape='rect')
    def draw_starcore(self,d,box,theme,state,phase):
        x1,y1,x2,y2=box; d.rounded_rectangle(box,radius=14,fill=theme.c('panel'),outline=theme.c('secondary'),width=2)
        d.arc((x1+6,y1+6,x2-6,y2-6),180+int(phase*20)%60,330+int(phase*20)%60,fill=theme.c('info'),width=2)
        self._features(d,box,theme,state,phase,eye_shape='ellipse')
    def draw_blackice(self,d,box,theme,state,phase):
        x1,y1,x2,y2=box; d.polygon([(x1+8,y1),(x2-8,y1),(x2,y1+8),(x2-5,y2),(x1+5,y2),(x1,y1+8)],fill=theme.c('panel'),outline=theme.c('primary'))
        for i in range(4): d.line((x1+10+i*31,y1+4,x1+30+i*24,y2-5),fill=theme.c('grid'))
        self._features(d,box,theme,state,phase,eye_shape='slash')
    def draw_hunter(self,d,box,theme,state,phase):
        x1,y1,x2,y2=box; d.rectangle(box,fill=theme.c('panel'),outline=theme.c('danger'),width=2)
        d.polygon([(x1+22,y1+38),(x1+38,y1+4),(x1+58,y1+35)],outline=theme.c('danger')); d.polygon([(x2-58,y1+35),(x2-38,y1+4),(x2-22,y1+38)],outline=theme.c('danger'))
        self._features(d,box,theme,state,phase,eye_shape='slash')
    def draw_minimal(self,d,box,theme,state,phase):
        d.rounded_rectangle(box,radius=18,fill=theme.c('panel'),outline=theme.c('edge')); self._features(d,box,theme,state,phase,eye_shape='ellipse')
