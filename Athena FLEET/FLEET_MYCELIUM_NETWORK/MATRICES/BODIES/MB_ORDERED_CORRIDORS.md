# MB Ordered Corridor Matrix

| source | target | relation | weight | priority | lines |
| --- | --- | --- | --- | --- | --- |
| MB01 | MB01 | compress | 0.880 | primary | Origin,Transit |
| MB01 | MB02 | route | 0.800 | secondary | Origin,Transit |
| MB02 | MB01 | compress | 0.800 | secondary | Origin,Transit |
| MB02 | MB02 | recurse | 0.880 | primary | Origin,Transit,Governance |
