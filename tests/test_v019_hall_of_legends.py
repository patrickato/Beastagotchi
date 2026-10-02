from __future__ import annotations

from beastcore.actions import ActionBroker
from beastcore.db import Store
from beastcore.events import EventBus
from beastcore.progression import xp_threshold
from beastcore.roster import BeastRoster
from beastcore.state import StateRegistry

def setup(tmp_path):
    store=Store(str(tmp_path/'beast.db'))
    roster=BeastRoster(store,legacy_profile_path=tmp_path/'none.json',clock=lambda:1000.0)
    a=roster.bootstrap_founder(name='Hex')
    b=roster.create_beast('Orbit',lineage_id='starcore')
    broker=ActionBroker(StateRegistry(),store,EventBus())
    return store,roster,broker,a,b

def test_hall_induction_requires_level_100(tmp_path):
    _,roster,broker,a,_=setup(tmp_path)
    roster.update_progress(a['id'],xp=xp_threshold(99))
    row=broker.perform('roster.legend_set',{'id':a['id'],'enabled':True})
    assert row['status']=='failed'
    assert roster.get(a['id'])['legend'] is False

def test_legend_state_is_independent_of_active_resting_state(tmp_path):
    _,roster,broker,a,b=setup(tmp_path)
    roster.update_progress(a['id'],xp=xp_threshold(100))
    assert broker.perform('roster.legend_set',{'id':a['id'],'enabled':True})['status']=='success'
    roster.set_active(b['id'])
    after=roster.get(a['id'])
    assert after['active'] is False and after['status']=='resting' and after['legend'] is True

def test_hall_snapshot_separates_candidates_and_inductees(tmp_path):
    _,roster,broker,a,b=setup(tmp_path)
    roster.update_progress(a['id'],xp=xp_threshold(100));roster.update_progress(b['id'],xp=xp_threshold(100))
    broker.perform('roster.legend_set',{'id':a['id'],'enabled':True})
    hall=broker.plan('roster.hall',{})
    assert [x['id'] for x in hall['inductees']]==[a['id']]
    assert [x['id'] for x in hall['candidates']]==[b['id']]
    assert hall['level_100_count']==2

def test_ancestry_graph_contains_parent_child_edges(tmp_path):
    _,roster,_,a,b=setup(tmp_path)
    roster.update_progress(a['id'],xp=xp_threshold(70));roster.update_progress(b['id'],xp=xp_threshold(70))
    child=roster.synthesize(a['id'],b['id'],name='Nova')['monster']
    graph=roster.ancestry_graph();edges={(e['parent_id'],e['child_id']) for e in graph['edges']}
    assert (a['id'],child['id']) in edges and (b['id'],child['id']) in edges
    assert child['id'] in {n['id']:n for n in graph['nodes']}[a['id']]['children']

def test_hall_induction_memory_survives_removal(tmp_path):
    _,roster,broker,a,_=setup(tmp_path)
    roster.update_progress(a['id'],xp=xp_threshold(100))
    broker.perform('roster.legend_set',{'id':a['id'],'enabled':True})
    assert broker.memories.summary(a['id'])['memory_count']==1
    broker.perform('roster.legend_set',{'id':a['id'],'enabled':False})
    assert roster.get(a['id'])['legend'] is False
    assert broker.memories.summary(a['id'])['memory_count']==1
