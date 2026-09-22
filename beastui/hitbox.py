from __future__ import annotations
from dataclasses import dataclass

SCREEN_W=480
SCREEN_H=320
MIN_TARGET=48
NORMAL_TARGET=56
PRIMARY_TARGET=72
EDGE_EXPAND=10

@dataclass(frozen=True)
class HitBox:
    name: str
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return max(0,self.x2-self.x1+1)

    @property
    def height(self) -> int:
        return max(0,self.y2-self.y1+1)

    def contains(self,x:int,y:int) -> bool:
        return self.x1 <= int(x) <= self.x2 and self.y1 <= int(y) <= self.y2


def expanded_hitbox(name:str, visual:tuple[int,int,int,int], minimum:int=NORMAL_TARGET,
                    edge_expand:int=EDGE_EXPAND, screen:tuple[int,int]=(SCREEN_W,SCREEN_H)) -> HitBox:
    """Return a forgiving physical hit region around a visual rectangle.

    Touch Lab showed that visible geometry and physical hit geometry should be
    independent on the 3.5-inch ADS7846 panel.  This helper keeps controls at
    least `minimum` pixels across, then adds a small inward-safe expansion for
    controls that visually touch a display edge.  The returned box is always
    clamped to the screen.
    """
    x1,y1,x2,y2=map(int,visual)
    if x2 < x1: x1,x2=x2,x1
    if y2 < y1: y1,y2=y2,y1
    w=x2-x1+1; h=y2-y1+1
    if w < minimum:
        d=minimum-w; x1-=d//2; x2+=d-d//2
    if h < minimum:
        d=minimum-h; y1-=d//2; y2+=d-d//2
    sw,sh=screen
    if visual[0] <= 4: x2 += edge_expand
    if visual[2] >= sw-5: x1 -= edge_expand
    if visual[1] <= 4: y2 += edge_expand
    if visual[3] >= sh-5: y1 -= edge_expand

    # Clamp by *shifting* the box inward rather than chopping off the expanded
    # side. This preserves the measured minimum physical target size even for
    # controls that sit directly on a bezel edge/corner.
    if x1 < 0:
        x2 += -x1; x1 = 0
    if y1 < 0:
        y2 += -y1; y1 = 0
    if x2 >= sw:
        x1 -= x2-(sw-1); x2 = sw-1
    if y2 >= sh:
        y1 -= y2-(sh-1); y2 = sh-1
    x1=max(0,x1); y1=max(0,y1)
    return HitBox(name,x1,y1,min(sw-1,x2),min(sh-1,y2))


def hit(name:str, visual:tuple[int,int,int,int], x:int, y:int, minimum:int=NORMAL_TARGET,
        edge_expand:int=EDGE_EXPAND) -> bool:
    return expanded_hitbox(name,visual,minimum,edge_expand).contains(x,y)
