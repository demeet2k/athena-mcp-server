import json
import os
import sqlite3
import tempfile
import unittest

from athena_mcp.server import Server


class LegacyMigrationPreservationTests(unittest.TestCase):
    def setUp(self):
        f=tempfile.NamedTemporaryFile(suffix='.db',delete=False);f.close();self.db=f.name
        conn=sqlite3.connect(self.db)
        conn.execute('CREATE TABLE legacy_sentinel(id TEXT PRIMARY KEY,payload TEXT NOT NULL)')
        conn.execute('INSERT INTO legacy_sentinel VALUES(?,?)',('LEGACY.1',json.dumps({'keep':True,'lineage':'pre-unified'})))
        conn.execute('CREATE TABLE legacy_events(seq INTEGER PRIMARY KEY,note TEXT NOT NULL)')
        conn.execute('INSERT INTO legacy_events(note) VALUES(?)',('never delete unknown durable state',))
        conn.commit();conn.close();self.server=Server(self.db);self.seq=0
    def tearDown(self):
        try:self.server.store.close()
        except Exception:pass
        try:os.unlink(self.db)
        except Exception:pass
    def tool(self,name,args=None):
        self.seq+=1;r=self.server.handle({'jsonrpc':'2.0','id':self.seq,'method':'tools/call','params':{'name':name,'arguments':args or {}}});result=r['result'];self.assertFalse(result.get('isError'),r);return result['structuredContent']
    def legacy_snapshot(self):
        a=self.server.store.one("SELECT * FROM legacy_sentinel WHERE id='LEGACY.1'");b=self.server.store.rows('SELECT * FROM legacy_events ORDER BY seq');return dict(a),[dict(x) for x in b]
    def test_unknown_legacy_tables_and_rows_survive_v1_v2_migration_unchanged(self):
        before=self.legacy_snapshot();plan=self.tool('athena_schema_plan');self.assertEqual(plan['status'],'MIGRATION_REQUIRED');applied=self.tool('athena_schema_migrate');self.assertEqual(applied['status'],'APPLIED',applied);after=self.legacy_snapshot();self.assertEqual(after,before);self.assertEqual(json.loads(after[0]['payload']),{'keep':True,'lineage':'pre-unified'});verify=self.tool('athena_schema_verify');self.assertEqual(verify['status'],'PASS',verify)
        tables={r['name'] for r in self.server.store.rows("SELECT name FROM sqlite_master WHERE type='table'")};self.assertIn('legacy_sentinel',tables);self.assertIn('legacy_events',tables)
    def test_restart_after_migration_preserves_unknown_legacy_state(self):
        self.tool('athena_schema_migrate');before=self.legacy_snapshot();self.server.store.close();self.server=Server(self.db);after=self.legacy_snapshot();self.assertEqual(after,before);self.assertEqual(self.tool('athena_schema_status')['current_db_schema_version'],2)


if __name__=='__main__':unittest.main()
