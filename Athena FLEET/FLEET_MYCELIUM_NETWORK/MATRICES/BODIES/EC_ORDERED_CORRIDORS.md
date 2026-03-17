# EC Ordered Corridor Matrix

| source | target | relation | weight | priority | lines |
| --- | --- | --- | --- | --- | --- |
| EC01 | EC01 | recurse | 0.880 | primary | Transit,Governance |
| EC01 | EC02 | repair | 0.730 | secondary | Governance |
| EC02 | EC01 | route | 0.730 | secondary | Governance |
| EC02 | EC02 | govern | 0.880 | primary | Crystal,Governance |
