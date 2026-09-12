"""Signed evidence links must survive retrieval even without page backlinks."""
import csv
import io
from pathlib import Path
import tempfile
import unittest

from athena_mcp.server import Server
from athena_mcp.wiki_memory import digest


def registry():
    groups=[
        (['PAGE_ID','TITLE','DRIVE_FILE_ID'],[['page.a','Report','source.a'],['page.b','Other','source.b']]),
        (['CLAIM_ID','PAGE_ID','CLAIM_SUMMARY','EPI'],[['claim.a','page.a','Reported benefit','HYP'],['claim.b','page.b','Another report','UNK']]),
        (['EVIDENCE_ID','KIND','SOURCE_REF','SUPPORTS_CLAIMS','CONTRADICTS_CLAIMS'],[
            ['evidence.support','TEST','source.support','claim.a',''],
            ['evidence.counter','TEST','source.counter','','claim.a'],
            ['evidence.mixed','TEST','source.mixed','claim.a','claim.a'],
            ['evidence.other','TEST','source.other','','claim.b']]),
        (['TASK_ID','PAGE_ID','SUCCESS_TEST'],[]),
        (['CONFLICT_ID','PAGE_ID','BRANCH_A'],[]),
    ]
    parts=[]
    for headers,rows in groups:
        stream=io.StringIO();writer=csv.writer(stream);writer.writerow(headers);writer.writerows(rows);parts.append(stream.getvalue())
    return '\f'.join(parts)


class WikiCounterevidenceTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.server=Server(str(Path(self.directory.name)/'state.db'))
        text=registry()
        self.snapshot=self.server.call_tool('athena_wiki_import_registry',dict(source_id='registry',observed_at='2026-09-08T12:00:00Z',text=text,expected_sha256=digest(text),expected_snapshot_id=None))['snapshot_id']

    def tearDown(self):
        self.server.store.close();self.directory.cleanup()

    def context(self,limit=100):
        return self.server.call_tool('athena_wiki_context',dict(snapshot_id=self.snapshot,page_id='page.a',max_records=limit))

    def test_counterevidence_only_link_is_retained_without_promoting_claim(self):
        context=self.context()
        evidence={r['EVIDENCE_ID']:r for r in context['records']['evidence']}
        self.assertEqual(set(evidence),{'evidence.support','evidence.counter','evidence.mixed'})
        self.assertEqual(evidence['evidence.counter']['CONTRADICTS_CLAIMS'],'claim.a')
        self.assertEqual(evidence['evidence.mixed']['SUPPORTS_CLAIMS'],'claim.a')
        self.assertEqual(evidence['evidence.mixed']['CONTRADICTS_CLAIMS'],'claim.a')
        self.assertEqual(context['records']['claims'][0]['EPI'],'HYP')
        self.assertFalse(context['truncated'])
        self.assertEqual(context['live_currentness'],'UNVERIFIED')

    def test_bounded_context_counts_omitted_counterevidence(self):
        context=self.context(2)  # One claim and one evidence record fit.
        self.assertTrue(context['truncated'])
        self.assertEqual(context['omitted_records']['evidence'],2)


if __name__=='__main__':unittest.main()
