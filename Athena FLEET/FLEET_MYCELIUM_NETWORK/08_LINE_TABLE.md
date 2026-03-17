# Athena FLEET Line Table

## Line Order

| line | station_order | transfer_hubs_on_line |
| --- | --- | --- |
| Origin | F01 -> F04 -> F02 -> F10 | F02 |
| Crystal | F04 -> F03 -> F07 -> F02 | F07, F02 |
| Transit | F05 -> F06 -> F07 -> F08 -> F09 | F07 |
| Governance | F09 -> F08 -> F10 -> F07 -> F02 -> F01 | F07, F02 |

## Transfer Hubs

| node | label | lines | hub_rank |
| --- | --- | --- | --- |
| F02 | ATHENACHKA | Origin,Crystal,Governance | 4 |
| F07 | SELF STEER BRANCH C | Crystal,Transit,Governance | 2 |
