from __future__ import annotations

from beastcore.heritage import generate_heritage, mutation_chance_basis_points, normalize_parent_traits
from beastcore.db import Store
from beastcore.progression import xp_threshold
from beastcore.roster import BeastRoster


def parent(pid,lineage,level=70,traits=None):
    return {
        "id":pid,"lineage_id":lineage,"level":level,
        "identity":{"traits":traits or {}},"appearance":{},"preferences":{},
    }


def test_heritage_is_deterministic_for_same_seed_and_parents():
    a=parent("a","forest",traits={"eyes":"slit","aura":"mist","temperament":{"curiosity":90}})
    b=parent("b","star",traits={"eyes":"visor","aura":"orbital","temperament":{"curiosity":20}})
    x=generate_heritage(a,b,"seed-123")
    y=generate_heritage(a,b,"seed-123")
    assert x==y
    assert x["traits"]["eyes"] in {"slit","visor"}
    assert x["traits"]["aura"] in {"mist","orbital"}
    assert 0<=x["traits"]["temperament"]["curiosity"]<=100


def test_explicit_parent_traits_override_lineage_defaults():
    p=parent("a","anything",traits={"silhouette":"feline","eyes":"ring","motion":"stalk"})
    t=normalize_parent_traits(p)
    assert t["silhouette"]=="feline"
    assert t["eyes"]=="ring"
    assert t["motion"]=="stalk"


def test_cross_lineage_and_level_100_parents_raise_but_cap_mutation_chance():
    same=mutation_chance_basis_points(parent("a","x"),parent("b","x"))
    cross=mutation_chance_basis_points(parent("a","x"),parent("b","y"))
    apex=mutation_chance_basis_points(parent("a","x",100),parent("b","y",100))
    assert same==350
    assert cross==500
    assert apex==1000


def test_synthesis_persists_generated_heritage_and_traits(tmp_path):
    store=Store(str(tmp_path/"beast.db"))
    roster=BeastRoster(store,legacy_profile_path=tmp_path/"none.json",clock=lambda:1000.0)
    a=roster.bootstrap_founder(name="Hex")
    b=roster.create_beast("Orbit",lineage_id="starcore",
        identity={"traits":{"eyes":"visor","aura":"orbital","motion":"float"}})
    roster.update_progress(a["id"],xp=xp_threshold(70))
    roster.update_progress(b["id"],xp=xp_threshold(70))
    out=roster.synthesize(a["id"],b["id"],name="Nova")
    m=out["monster"]
    h=m["identity"]["heritage"]
    assert h["schema"]==2
    assert h["generated_identity_pending"] is False
    assert h["generated"]["seed"]==h["inheritance_seed"]
    assert isinstance(m["identity"]["traits"],dict)
    assert m["appearance"]["traits"]==m["identity"]["traits"]


def test_mutation_result_when_present_is_persisted_in_appearance(tmp_path):
    store=Store(str(tmp_path/"beast.db"))
    roster=BeastRoster(store,legacy_profile_path=tmp_path/"none.json",clock=lambda:1000.0)
    a=roster.bootstrap_founder()
    b=roster.create_beast("B",lineage_id="other")
    roster.update_progress(a["id"],xp=xp_threshold(100));roster.update_progress(b["id"],xp=xp_threshold(100))
    out=roster.synthesize(a["id"],b["id"])
    m=out["monster"]
    assert "mutation" in m["appearance"]
    assert m["identity"]["heritage"]["generated"]["mutation_chance_basis_points"]==1000
