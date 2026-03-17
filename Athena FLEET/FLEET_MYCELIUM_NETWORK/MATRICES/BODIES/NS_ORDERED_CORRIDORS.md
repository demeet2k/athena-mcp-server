# NS Ordered Corridor Matrix

| source | target | relation | weight | priority | lines |
| --- | --- | --- | --- | --- | --- |
| NS01 | NS01 | recurse | 0.880 | primary | Origin,Transit,Governance |
| NS01 | NS02 | seed | 0.820 | primary | Transit,Governance |
| NS02 | NS01 | publish | 0.820 | primary | Transit,Governance |
| NS02 | NS02 | recurse | 0.880 | primary | Crystal,Transit,Governance |
