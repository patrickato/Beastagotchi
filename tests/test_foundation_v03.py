import json
import tempfile
import time
import unittest
from pathlib import Path

from beastcore.state import StateRegistry
from beastcore.context import ContextEngine
from beastcore.collectors.bridge import BridgeCollector
from beastcore.db import Store

class StateTests(unittest.TestCase):
    def test_priority_and_stale_takeover(self):
        s=StateRegistry()
        s.update_many('low', {'x':1}, priority=10)
        s.update_many('high', {'x':2}, priority=50)
        s.update_many('low', {'x':3}, priority=10)
        self.assertEqual(s.get('x'),2)
        s.mark_source_stale('high', 0)
        s.update_many('low', {'x':3}, priority=10)
        self.assertEqual(s.get('x'),3)

class ContextTests(unittest.TestCase):
    def test_motion_classes(self):
        self.assertEqual(ContextEngine.classify(0.2),'stationary')
        self.assertEqual(ContextEngine.classify(3.0),'walking')
        self.assertEqual(ContextEngine.classify(10.0),'moving')
        self.assertEqual(ContextEngine.classify(20.0),'wardrive')

class BridgeTests(unittest.TestCase):
    def test_bridge_event_ring(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'bridge.json'
            p.write_text(json.dumps({
                'updated_at':123.0,
                'state':{'pwnagotchi.epoch':4},
                'events':[{'seq':1,'type':'epoch','ts':123.0,'data':{'epoch':4}}]
            }))
            c=BridgeCollector(str(p))
            vals=c.collect()
            self.assertEqual(vals['pwnagotchi.epoch'],4)
            evs=c.drain_events(); self.assertEqual(len(evs),1)
            c.collect(); self.assertEqual(c.drain_events(),[])

class StoreTests(unittest.TestCase):
    def test_history(self):
        with tempfile.TemporaryDirectory() as td:
            db=Store(str(Path(td)/'x.db'))
            db.add_samples([(1.0,'system.temp.cpu_c',50.0,'system'),(2.0,'system.temp.cpu_c',51.0,'system')])
            rows=db.query_samples('system.temp.cpu_c',0,10)
            self.assertEqual([x['value'] for x in rows],[50.0,51.0])
            db.close()

if __name__ == '__main__': unittest.main()
