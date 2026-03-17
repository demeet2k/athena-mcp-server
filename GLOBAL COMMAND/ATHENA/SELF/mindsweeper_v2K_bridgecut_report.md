# Mindsweeper v2K Bridge-Cut Sweep

This report computes **bridge power** on the indexed atlas using the generated `mindsweeper_v2K_edge_index.md` graph.

Metrics included:
- directed betweenness centrality on the folded graph
- undirected betweenness centrality on the folded graph
- articulation-point sweep on the folded undirected projection
- bridge-edge sweep on the folded undirected projection
- exact-node betweenness reference table

## Folded graph summary

- Folded nodes: **48**
- Folded directed edges: **50**
- Folded undirected edges: **50**
- Connected components (undirected folded): **9**
- Largest connected component size: **23**

## Top nodes by undirected betweenness (folded)

| node                      | region             |   degree_total |   betweenness_undirected |   component_increase |   largest_component_drop |
|:--------------------------|:-------------------|---------------:|-------------------------:|---------------------:|-------------------------:|
| AppA                      | spine+overlays     |             13 |              0.143293    |                    6 |                        9 |
| Ms⟨mmmm⟩::ChXX⟨dddd⟩.S1.a | chapter/manifold   |              6 |              0.0558742   |                    3 |                        4 |
| Ch10⟨0021⟩                | chapter/manifold   |              9 |              0.0456984   |                    2 |                        3 |
| AppM                      | spine+overlays     |              7 |              0.0374653   |                    1 |                        2 |
| AppP                      | spine+overlays     |              2 |              0.0194265   |                    1 |                        2 |
| AppK                      | spine+overlays     |              2 |              0.0194265   |                    1 |                        2 |
| AppI                      | spine+overlays     |              5 |              0.00832562  |                    0 |                        1 |
| DIV::L1.BINARY_GATE       | divination         |              4 |              0.00555042  |                    3 |                        0 |
| AE₀                       | tunnel/aether      |              4 |              0.00555042  |                    3 |                        0 |
| Z*                        | tunnel/aether      |              3 |              0.00277521  |                    2 |                        0 |
| Stamp::PROMOTED_OK        | promotion+conflict |              2 |              0.000925069 |                    1 |                        0 |
| Ch01⟨0000⟩                | chapter/manifold   |              3 |              0.000370028 |                    0 |                        1 |
| WHO-I-AM::BRAINSTEM       | brainstem          |              3 |              0.000370028 |                    0 |                        1 |
| AppJ                      | spine+overlays     |              2 |              0           |                    0 |                        1 |
| Ch21⟨0110⟩                | chapter/manifold   |              2 |              0           |                    0 |                        1 |

## Top nodes by directed betweenness (folded)

| node                      | region             |   out_degree_directed |   in_degree_directed |   betweenness_directed |
|:--------------------------|:-------------------|----------------------:|---------------------:|-----------------------:|
| AppA                      | spine+overlays     |                     9 |                    4 |            0.0124884   |
| AppM                      | spine+overlays     |                     1 |                    6 |            0.00277521  |
| Z*                        | tunnel/aether      |                     1 |                    2 |            0.000925069 |
| Stamp::PROMOTED_OK        | promotion+conflict |                     1 |                    1 |            0.000462535 |
| AppP                      | spine+overlays     |                     0 |                    2 |            0           |
| AppK                      | spine+overlays     |                     0 |                    2 |            0           |
| Ms⟨mmmm⟩::ChXX⟨dddd⟩.S1.a | chapter/manifold   |                     6 |                    0 |            0           |
| Ch10⟨0021⟩                | chapter/manifold   |                     8 |                    1 |            0           |
| DIV::L1.BINARY_GATE       | divination         |                     4 |                    0 |            0           |
| AppI                      | spine+overlays     |                     0 |                    5 |            0           |
| AE₀                       | tunnel/aether      |                     4 |                    0 |            0           |
| Ch01⟨0000⟩                | chapter/manifold   |                     3 |                    0 |            0           |
| WHO-I-AM::BRAINSTEM       | brainstem          |                     3 |                    0 |            0           |
| AppJ                      | spine+overlays     |                     0 |                    2 |            0           |
| Ch21⟨0110⟩                | chapter/manifold   |                     1 |                    1 |            0           |

## Articulation points (folded undirected)

| node                      | region             |   degree_total |   betweenness_undirected |   component_increase |   largest_component_drop |
|:--------------------------|:-------------------|---------------:|-------------------------:|---------------------:|-------------------------:|
| AppA                      | spine+overlays     |             13 |              0.143293    |                    6 |                        9 |
| Ms⟨mmmm⟩::ChXX⟨dddd⟩.S1.a | chapter/manifold   |              6 |              0.0558742   |                    3 |                        4 |
| DIV::L1.BINARY_GATE       | divination         |              4 |              0.00555042  |                    3 |                        0 |
| AE₀                       | tunnel/aether      |              4 |              0.00555042  |                    3 |                        0 |
| Ch10⟨0021⟩                | chapter/manifold   |              9 |              0.0456984   |                    2 |                        3 |
| Z*                        | tunnel/aether      |              3 |              0.00277521  |                    2 |                        0 |
| AppM                      | spine+overlays     |              7 |              0.0374653   |                    1 |                        2 |
| AppP                      | spine+overlays     |              2 |              0.0194265   |                    1 |                        2 |
| AppK                      | spine+overlays     |              2 |              0.0194265   |                    1 |                        2 |
| Stamp::PROMOTED_OK        | promotion+conflict |              2 |              0.000925069 |                    1 |                        0 |

## Top bridge edges (folded undirected)

| src                       | dst                          | kinds    |   edge_betweenness_undirected |   small_side |   large_side | labels                              |
|:--------------------------|:-----------------------------|:---------|------------------------------:|-------------:|-------------:|:------------------------------------|
| AppA                      | AppP                         | REF      |                     0.037234  |            2 |           21 | U09                                 |
| AppA                      | AppK                         | REF      |                     0.037234  |            2 |           21 | U12                                 |
| Ms⟨mmmm⟩::ChXX⟨dddd⟩.S1.a | Ms⟨mmmm⟩::ArcHub(arc).S1.a   | REF      |                     0.0195035 |            1 |           22 | U14                                 |
| Ms⟨mmmm⟩::ChXX⟨dddd⟩.S1.a | Ms⟨mmmm⟩::FacetBase(f).S1.a  | REF      |                     0.0195035 |            1 |           22 | U15                                 |
| Ms⟨mmmm⟩::ChXX⟨dddd⟩.S1.a | Ms⟨mmmm⟩::LensBase(l).S1.a   | REF      |                     0.0195035 |            1 |           22 | U16                                 |
| AppA                      | AppC                         | REF      |                     0.0195035 |            1 |           22 | U04                                 |
| AppA                      | AppE                         | REF      |                     0.0195035 |            1 |           22 | U05                                 |
| AppA                      | AppD                         | REF      |                     0.0195035 |            1 |           22 | U08                                 |
| AppA                      | AppL                         | REF      |                     0.0195035 |            1 |           22 | U11                                 |
| AppM                      | AppO                         | REF      |                     0.0195035 |            1 |           22 | U13;E07                             |
| AppP                      | Ch19⟨0102⟩                   | REF      |                     0.0195035 |            1 |           22 | E05                                 |
| AppK                      | Cell                         | CONFLICT |                     0.0195035 |            1 |           22 | G41;G42;G43;G44;G45;G46;G47;G48;G49 |
| Ch10⟨0021⟩                | AppF                         | REF      |                     0.0195035 |            1 |           22 | E04;P12                             |
| Ch10⟨0021⟩                | AppH                         | REF      |                     0.0195035 |            1 |           22 | P13                                 |
| DIV::L1.BINARY_GATE       | DIV::TAROT.UPRIGHT_REVERSED  | EQUIV    |                     0.0035461 |            1 |           23 | D01                                 |
| DIV::L1.BINARY_GATE       | DIV::ICHING.YIN_YANG         | EQUIV    |                     0.0035461 |            1 |           23 | D02                                 |
| DIV::L1.BINARY_GATE       | DIV::RUNES.UPRIGHT_MERKSTAVE | EQUIV    |                     0.0035461 |            1 |           23 | D03                                 |
| DIV::L1.BINARY_GATE       | DIV::IFA.ONE_TWO             | EQUIV    |                     0.0035461 |            1 |           23 | D04                                 |
| AE₀                       | Z(Fire)                      | REF      |                     0.0035461 |            1 |           23 | G05                                 |
| AE₀                       | Z(Air)                       | REF      |                     0.0035461 |            1 |           23 | G06                                 |

## Chokepoint read

- **AppA** is the strongest structural bridge-cut: highest undirected betweenness and largest disconnection effect after removal.

- **Ms⟨mmmm⟩::ChXX⟨dddd⟩.S1.a** is the generic chapter-entry choke point that feeds ArcHub / FacetBase / LensBase stubs.

- **Ch10⟨0021⟩** is the strongest operational bridge inside the live manifold cluster, connecting compile flow to AppF/AppH and the POI kernel.

- **AppM** is the replay/publish choke point.

- **AppK** and **AppP** are small but sharp cuts: failure/quarantine and governance/router branches each hang off a single bridge from the spine.

- **Z\*** is a real narrow tunnel cut, but only lightly surfaced in the current atlas because only a small number of tunnel edges have been indexed so far.

- **DIV::L1.BINARY_GATE** and **AE₀** are transfer stars: low volume compared with AppA, but each is a clean bridge to four leaves.


## Recommended next lift

1. Assign weighted costs to edge kinds (`PROOF`, `MIGRATE`, `CONFLICT`, `GEN`, ...).
2. Recompute weighted betweenness to separate cheap route carriers from expensive semantic bridges.
3. Add the currently implicit tunnel-envelope repair candidates for `R03/R30/R33`, `Q03/Q30/Q33`, `T03/T30/T33` so `AppK` and `Z*` get a truer bridge profile.
