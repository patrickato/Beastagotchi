from __future__ import annotations

import json

import pytest

from beastcore.transactions import (
    FileTransactionJournal,
    TransactionEngine,
    TransactionSpec,
    TransactionTransitionError,
)


class _Adapter:
    def __init__(self, *, blocked=False, fail_apply=False, fail_probation=False, fail_verify=False, fail_commit=False, fail_rollback=False):
        self.blocked = blocked
        self.fail_apply = fail_apply
        self.fail_probation = fail_probation
        self.fail_verify = fail_verify
        self.fail_commit = fail_commit
        self.fail_rollback = fail_rollback
        self.calls = []

    def subject(self, request):
        return f"demo:{request.get('id', 'unknown')}"

    def plan(self, ctx):
        self.calls.append('plan')
        return {
            'allowed': not self.blocked,
            'operation': ctx.spec.id,
            'blockers': ['blocked by test'] if self.blocked else [],
        }

    def prepare(self, ctx):
        self.calls.append('prepare')
        return {'ok': True, 'snapshot': 'before'}

    def apply(self, ctx):
        self.calls.append('apply')
        if self.fail_apply:
            return {'ok': False, 'error': 'apply failed after touching state'}
        return {'ok': True, 'changed': True}

    def probation(self, ctx):
        self.calls.append('probation')
        return {'ok': not self.fail_probation, 'error': 'probation failed' if self.fail_probation else None}

    def verify(self, ctx):
        self.calls.append('verify')
        return {'ok': not self.fail_verify, 'error': 'verification failed' if self.fail_verify else None}

    def commit(self, ctx):
        self.calls.append('commit')
        return {'ok': not self.fail_commit, 'error': 'commit failed' if self.fail_commit else None}

    def rollback(self, ctx):
        self.calls.append('rollback')
        if self.fail_rollback:
            return {'ok': False, 'error': 'rollback failed'}
        return {'ok': True, 'restored': True}


def _engine(tmp_path):
    journal = FileTransactionJournal(tmp_path / 'transactions', clock=lambda: 1000.0)
    return TransactionEngine(journal, clock=lambda: 1000.0)


def test_transaction_happy_path_commits_only_after_verification(tmp_path):
    adapter = _Adapter()
    engine = _engine(tmp_path)
    spec = TransactionSpec('demo.change', adapter)

    row = engine.execute(spec, {'id': 'alpha'}, actor='owner')

    assert row['status'] == 'committed'
    assert row['subject'] == 'demo:alpha'
    assert row['actor'] == 'owner'
    assert adapter.calls == ['plan', 'prepare', 'apply', 'probation', 'verify', 'commit']
    states = [x['state'] for x in row['timeline']]
    assert states == [
        'planned', 'preparing', 'prepared', 'applying', 'applied',
        'probation', 'verifying', 'committing', 'committed'
    ]
    assert row['stage_results']['prepare']['snapshot'] == 'before'
    assert row['stage_results']['apply']['changed'] is True
    assert row['stage_results']['probation']['ok'] is True
    assert row['stage_results']['verify']['ok'] is True
    assert row['stage_results']['commit']['ok'] is True


def test_blocked_plan_never_prepares_or_applies(tmp_path):
    adapter = _Adapter(blocked=True)
    engine = _engine(tmp_path)

    row = engine.execute(TransactionSpec('demo.change', adapter), {'id': 'alpha'})

    assert row['status'] == 'cancelled_before_apply'
    assert adapter.calls == ['plan']
    assert row['stage_results']['plan']['ok'] is False
    assert 'blocked by test' in row['timeline'][-1]['detail']


def test_apply_failure_enters_rollback_and_finishes_rolled_back(tmp_path):
    adapter = _Adapter(fail_apply=True)
    engine = _engine(tmp_path)

    row = engine.execute(TransactionSpec('demo.change', adapter), {'id': 'alpha'})

    assert row['status'] == 'rolled_back'
    assert adapter.calls == ['plan', 'prepare', 'apply', 'rollback']
    assert row['stage_results']['apply']['ok'] is False
    assert row['stage_results']['rollback']['restored'] is True


def test_verification_failure_rolls_back_instead_of_committing(tmp_path):
    adapter = _Adapter(fail_verify=True)
    engine = _engine(tmp_path)

    row = engine.execute(TransactionSpec('demo.change', adapter), {'id': 'alpha'})

    assert row['status'] == 'rolled_back'
    assert adapter.calls == ['plan', 'prepare', 'apply', 'probation', 'verify', 'rollback']
    assert row['stage_results']['verify']['ok'] is False
    assert 'commit' not in adapter.calls


def test_commit_failure_still_attempts_rollback(tmp_path):
    adapter = _Adapter(fail_commit=True)
    engine = _engine(tmp_path)

    row = engine.execute(TransactionSpec('demo.change', adapter), {'id': 'alpha'})

    assert row['status'] == 'rolled_back'
    assert adapter.calls[-2:] == ['commit', 'rollback']
    assert row['stage_results']['commit']['ok'] is False


def test_rollback_failure_is_explicit_terminal_state(tmp_path):
    adapter = _Adapter(fail_verify=True, fail_rollback=True)
    engine = _engine(tmp_path)

    row = engine.execute(TransactionSpec('demo.change', adapter), {'id': 'alpha'})

    assert row['status'] == 'rollback_failed'
    assert row['stage_results']['rollback']['ok'] is False


def test_journal_is_private_atomic_and_survives_new_engine_instance(tmp_path):
    root = tmp_path / 'transactions'
    journal = FileTransactionJournal(root, clock=lambda: 1000.0)
    engine = TransactionEngine(journal, clock=lambda: 1000.0)
    row = engine.execute(TransactionSpec('demo.change', _Adapter()), {'id': 'alpha'})

    fp = root / f"{row['id']}.json"
    assert fp.is_file()
    assert (root.stat().st_mode & 0o777) == 0o700
    assert (fp.stat().st_mode & 0o777) == 0o600
    assert not list(root.glob('.*.tmp'))
    assert json.loads(fp.read_text())['status'] == 'committed'

    reopened = FileTransactionJournal(root, clock=lambda: 2000.0)
    assert reopened.get(row['id'])['status'] == 'committed'
    assert reopened.nonterminal() == []


def test_nonterminal_transaction_is_discovered_after_restart_without_blind_replay(tmp_path):
    root = tmp_path / 'transactions'
    journal = FileTransactionJournal(root, clock=lambda: 1000.0)
    adapter = _Adapter()
    spec = TransactionSpec('demo.change', adapter)
    tid = 'txn-demo.change-19700101t001640-aaaaaaaa'
    journal.create(
        transaction_id=tid,
        spec=spec,
        actor='owner',
        request={'id': 'alpha'},
        subject='demo:alpha',
        plan={'allowed': True},
    )
    journal.transition(tid, 'preparing')
    journal.transition(tid, 'prepared')
    journal.transition(tid, 'applying')

    restarted = TransactionEngine(FileTransactionJournal(root, clock=lambda: 2000.0), clock=lambda: 2000.0)
    inventory = restarted.recovery_inventory()

    assert inventory['count'] == 1
    assert inventory['items'][0]['status'] == 'applying'
    assert inventory['automatic_replay_enabled'] is False


def test_illegal_journal_transition_is_rejected(tmp_path):
    journal = FileTransactionJournal(tmp_path / 'transactions', clock=lambda: 1000.0)
    spec = TransactionSpec('demo.change', _Adapter())
    tid = 'txn-demo.change-19700101t001640-bbbbbbbb'
    journal.create(
        transaction_id=tid,
        spec=spec,
        actor='owner',
        request={},
        subject='demo',
        plan={'allowed': True},
    )

    with pytest.raises(TransactionTransitionError):
        journal.transition(tid, 'committed')
