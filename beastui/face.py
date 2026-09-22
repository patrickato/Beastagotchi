from __future__ import annotations
import math
from PIL import ImageFont

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

    def draw(self,d,box,theme,state,phase):
        style=getattr(theme,'face_style','classic')
        fn=getattr(self,f'draw_{style}',self.draw_classic)
        fn(d,box,theme,state,phase)

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
        # The original Pwnagotchi face floats directly on the display rather
        # than living inside a Beast HUD panel. Preserve that visual language.
        d.rectangle(box,fill=theme.c("panel"))
        face=self.resolve(state); mood=face["mood"]
        glyph=PWN_CLASSIC_FACES.get(mood,PWN_CLASSIC_FACES["awake"])
        mood_colors=getattr(theme,"mood_colors",None) or {}
        color=mood_colors.get(mood,theme.c("primary"))
        target=max(18,min(42,int((y2-y1)*0.29)))
        try:
            font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",target)
        except Exception:
            font=ImageFont.load_default()
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
        # digital ears
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
