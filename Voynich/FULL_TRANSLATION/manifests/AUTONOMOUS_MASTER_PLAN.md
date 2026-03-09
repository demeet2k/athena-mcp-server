# Autonomous Master Plan

## Control Architecture

This is the canonical macro plan for the full no-stop Voynich manuscript build.

- folio work items: `181`
- macro steps total: `187`

Control law:

1. the macro plan owns the full manuscript-order step ledger
2. the runtime emits one active micro plan from the active macro step
3. the penultimate micro step hands off to the next macro step
4. the final micro step performs successor intake and must not be interpreted as completion
5. every active macro step also emits a five-task run list whose fifth task reboots the cycle by reading the rewritten successor list
6. every active macro step also emits a parallel lane queue so the current folio, immediate successor, and preheated follow-on lane remain staged together
7. when no macro steps remain, the runtime emits the terminal completion micro plan and stops only because no successor step exists

## Canonical Runtime Files

- `framework/registry/autonomous_master_plan.json`
- `manifests/AUTONOMOUS_MASTER_PLAN.md`
- `manifests/ACTIVE_MICRO_PLAN.md`
- `manifests/ACTIVE_RUN_TASK_LIST.md`
- `manifests/PARALLEL_AGENT_QUEUE.md`
- `manifests/AUTONOMOUS_CURSOR.md`
- `manifests/AUTONOMOUS_QUEUE.md`
- `manifests/NEXT_FOLIO_SELF_PROMPT.md`
- `manifests/AUTONOMOUS_TERMINATION_CONTRACT.md`

## Book Spans

| Book | Start | End | Section | Crystal |
| --- | --- | --- | --- | --- |
| Book I - Herbal / materia medica | `F001R` | `F057V` | `sections/FULL_PLANT.md` | `crystals/PLANT_CRYSTAL.md` |
| Book II - Astronomical / astrological | `F058R` | `F073V` | `sections/FULL_ASTROLOGY.md` | `crystals/ASTROLOGY_CRYSTAL.md` |
| Book III - Bath / balneological | `F075R` | `F084V` | `sections/FULL_BATH.md` | `crystals/BATH_CRYSTAL.md` |
| Book V - Pharmaceutical 1 | `F087R` | `F106R` | `sections/PHARMACEUTICAL_1_FULL.md` | `crystals/PHARMACEUTICAL_1_CRYSTAL.md` |
| Book V - Pharmaceutical 2 | `F106V` | `F116V` | `sections/PHARMACEUTICAL_2_FULL.md` | `crystals/PHARMACEUTICAL_2_CRYSTAL.md` |

## Reserved Gap Windows

### Reserved Book IV / Cosmology gap in current canonical registry

- gap window: `F085R`, `F085V`, `F086R`, `F086V`
- placement: after `F084V` and before `F087R`
- rule: Do not invent absent folios. Hold the gap explicitly until a canonical local witness is added.

## Macro Step Ledger

1. `MACRO_001_F001R` | kind: `folio` | target: `F001R` | next: `MACRO_002_F001V`
2. `MACRO_002_F001V` | kind: `folio` | target: `F001V` | next: `MACRO_003_F002R`
3. `MACRO_003_F002R` | kind: `folio` | target: `F002R` | next: `MACRO_004_F002V`
4. `MACRO_004_F002V` | kind: `folio` | target: `F002V` | next: `MACRO_005_F003R`
5. `MACRO_005_F003R` | kind: `folio` | target: `F003R` | next: `MACRO_006_F003V`
6. `MACRO_006_F003V` | kind: `folio` | target: `F003V` | next: `MACRO_007_F004R`
7. `MACRO_007_F004R` | kind: `folio` | target: `F004R` | next: `MACRO_008_F004V`
8. `MACRO_008_F004V` | kind: `folio` | target: `F004V` | next: `MACRO_009_F005R`
9. `MACRO_009_F005R` | kind: `folio` | target: `F005R` | next: `MACRO_010_F005V`
10. `MACRO_010_F005V` | kind: `folio` | target: `F005V` | next: `MACRO_011_F006R`
11. `MACRO_011_F006R` | kind: `folio` | target: `F006R` | next: `MACRO_012_F006V`
12. `MACRO_012_F006V` | kind: `folio` | target: `F006V` | next: `MACRO_013_F007R`
13. `MACRO_013_F007R` | kind: `folio` | target: `F007R` | next: `MACRO_014_F007V`
14. `MACRO_014_F007V` | kind: `folio` | target: `F007V` | next: `MACRO_015_F008R`
15. `MACRO_015_F008R` | kind: `folio` | target: `F008R` | next: `MACRO_016_F008V`
16. `MACRO_016_F008V` | kind: `folio` | target: `F008V` | next: `MACRO_017_F009R`
17. `MACRO_017_F009R` | kind: `folio` | target: `F009R` | next: `MACRO_018_F009V`
18. `MACRO_018_F009V` | kind: `folio` | target: `F009V` | next: `MACRO_019_F010R`
19. `MACRO_019_F010R` | kind: `folio` | target: `F010R` | next: `MACRO_020_F010V`
20. `MACRO_020_F010V` | kind: `folio` | target: `F010V` | next: `MACRO_021_F011R`
21. `MACRO_021_F011R` | kind: `folio` | target: `F011R` | next: `MACRO_022_F011V`
22. `MACRO_022_F011V` | kind: `folio` | target: `F011V` | next: `MACRO_023_F013R`
23. `MACRO_023_F013R` | kind: `folio` | target: `F013R` | next: `MACRO_024_F013V`
24. `MACRO_024_F013V` | kind: `folio` | target: `F013V` | next: `MACRO_025_F014R`
25. `MACRO_025_F014R` | kind: `folio` | target: `F014R` | next: `MACRO_026_F014V`
26. `MACRO_026_F014V` | kind: `folio` | target: `F014V` | next: `MACRO_027_F015R`
27. `MACRO_027_F015R` | kind: `folio` | target: `F015R` | next: `MACRO_028_F015V`
28. `MACRO_028_F015V` | kind: `folio` | target: `F015V` | next: `MACRO_029_F016R`
29. `MACRO_029_F016R` | kind: `folio` | target: `F016R` | next: `MACRO_030_F016V`
30. `MACRO_030_F016V` | kind: `folio` | target: `F016V` | next: `MACRO_031_F017R`
31. `MACRO_031_F017R` | kind: `folio` | target: `F017R` | next: `MACRO_032_F017V`
32. `MACRO_032_F017V` | kind: `folio` | target: `F017V` | next: `MACRO_033_F018R`
33. `MACRO_033_F018R` | kind: `folio` | target: `F018R` | next: `MACRO_034_F018V`
34. `MACRO_034_F018V` | kind: `folio` | target: `F018V` | next: `MACRO_035_F019R`
35. `MACRO_035_F019R` | kind: `folio` | target: `F019R` | next: `MACRO_036_F019V`
36. `MACRO_036_F019V` | kind: `folio` | target: `F019V` | next: `MACRO_037_F020R`
37. `MACRO_037_F020R` | kind: `folio` | target: `F020R` | next: `MACRO_038_F020V`
38. `MACRO_038_F020V` | kind: `folio` | target: `F020V` | next: `MACRO_039_F021R`
39. `MACRO_039_F021R` | kind: `folio` | target: `F021R` | next: `MACRO_040_F021V`
40. `MACRO_040_F021V` | kind: `folio` | target: `F021V` | next: `MACRO_041_F022R`
41. `MACRO_041_F022R` | kind: `folio` | target: `F022R` | next: `MACRO_042_F022V`
42. `MACRO_042_F022V` | kind: `folio` | target: `F022V` | next: `MACRO_043_F023R`
43. `MACRO_043_F023R` | kind: `folio` | target: `F023R` | next: `MACRO_044_F023V`
44. `MACRO_044_F023V` | kind: `folio` | target: `F023V` | next: `MACRO_045_F024R`
45. `MACRO_045_F024R` | kind: `folio` | target: `F024R` | next: `MACRO_046_F024V`
46. `MACRO_046_F024V` | kind: `folio` | target: `F024V` | next: `MACRO_047_F025R`
47. `MACRO_047_F025R` | kind: `folio` | target: `F025R` | next: `MACRO_048_F025V`
48. `MACRO_048_F025V` | kind: `folio` | target: `F025V` | next: `MACRO_049_F026R`
49. `MACRO_049_F026R` | kind: `folio` | target: `F026R` | next: `MACRO_050_F026V`
50. `MACRO_050_F026V` | kind: `folio` | target: `F026V` | next: `MACRO_051_F027R`
51. `MACRO_051_F027R` | kind: `folio` | target: `F027R` | next: `MACRO_052_F027V`
52. `MACRO_052_F027V` | kind: `folio` | target: `F027V` | next: `MACRO_053_F028R`
53. `MACRO_053_F028R` | kind: `folio` | target: `F028R` | next: `MACRO_054_F028V`
54. `MACRO_054_F028V` | kind: `folio` | target: `F028V` | next: `MACRO_055_F029R`
55. `MACRO_055_F029R` | kind: `folio` | target: `F029R` | next: `MACRO_056_F029V`
56. `MACRO_056_F029V` | kind: `folio` | target: `F029V` | next: `MACRO_057_F030R`
57. `MACRO_057_F030R` | kind: `folio` | target: `F030R` | next: `MACRO_058_F030V`
58. `MACRO_058_F030V` | kind: `folio` | target: `F030V` | next: `MACRO_059_F031R`
59. `MACRO_059_F031R` | kind: `folio` | target: `F031R` | next: `MACRO_060_F031V`
60. `MACRO_060_F031V` | kind: `folio` | target: `F031V` | next: `MACRO_061_F032R`
61. `MACRO_061_F032R` | kind: `folio` | target: `F032R` | next: `MACRO_062_F032V`
62. `MACRO_062_F032V` | kind: `folio` | target: `F032V` | next: `MACRO_063_F033R`
63. `MACRO_063_F033R` | kind: `folio` | target: `F033R` | next: `MACRO_064_F033V`
64. `MACRO_064_F033V` | kind: `folio` | target: `F033V` | next: `MACRO_065_F034R`
65. `MACRO_065_F034R` | kind: `folio` | target: `F034R` | next: `MACRO_066_F034V`
66. `MACRO_066_F034V` | kind: `folio` | target: `F034V` | next: `MACRO_067_F035R`
67. `MACRO_067_F035R` | kind: `folio` | target: `F035R` | next: `MACRO_068_F035V`
68. `MACRO_068_F035V` | kind: `folio` | target: `F035V` | next: `MACRO_069_F036R`
69. `MACRO_069_F036R` | kind: `folio` | target: `F036R` | next: `MACRO_070_F036V`
70. `MACRO_070_F036V` | kind: `folio` | target: `F036V` | next: `MACRO_071_F037R`
71. `MACRO_071_F037R` | kind: `folio` | target: `F037R` | next: `MACRO_072_F037V`
72. `MACRO_072_F037V` | kind: `folio` | target: `F037V` | next: `MACRO_073_F038R`
73. `MACRO_073_F038R` | kind: `folio` | target: `F038R` | next: `MACRO_074_F038V`
74. `MACRO_074_F038V` | kind: `folio` | target: `F038V` | next: `MACRO_075_F039R`
75. `MACRO_075_F039R` | kind: `folio` | target: `F039R` | next: `MACRO_076_F039V`
76. `MACRO_076_F039V` | kind: `folio` | target: `F039V` | next: `MACRO_077_F040R`
77. `MACRO_077_F040R` | kind: `folio` | target: `F040R` | next: `MACRO_078_F040V`
78. `MACRO_078_F040V` | kind: `folio` | target: `F040V` | next: `MACRO_079_F041R`
79. `MACRO_079_F041R` | kind: `folio` | target: `F041R` | next: `MACRO_080_F041V`
80. `MACRO_080_F041V` | kind: `folio` | target: `F041V` | next: `MACRO_081_F042R`
81. `MACRO_081_F042R` | kind: `folio` | target: `F042R` | next: `MACRO_082_F042V`
82. `MACRO_082_F042V` | kind: `folio` | target: `F042V` | next: `MACRO_083_F043R`
83. `MACRO_083_F043R` | kind: `folio` | target: `F043R` | next: `MACRO_084_F043V`
84. `MACRO_084_F043V` | kind: `folio` | target: `F043V` | next: `MACRO_085_F044R`
85. `MACRO_085_F044R` | kind: `folio` | target: `F044R` | next: `MACRO_086_F044V`
86. `MACRO_086_F044V` | kind: `folio` | target: `F044V` | next: `MACRO_087_F045R`
87. `MACRO_087_F045R` | kind: `folio` | target: `F045R` | next: `MACRO_088_F045V`
88. `MACRO_088_F045V` | kind: `folio` | target: `F045V` | next: `MACRO_089_F046R`
89. `MACRO_089_F046R` | kind: `folio` | target: `F046R` | next: `MACRO_090_F046V`
90. `MACRO_090_F046V` | kind: `folio` | target: `F046V` | next: `MACRO_091_F047R`
91. `MACRO_091_F047R` | kind: `folio` | target: `F047R` | next: `MACRO_092_F047V`
92. `MACRO_092_F047V` | kind: `folio` | target: `F047V` | next: `MACRO_093_F048R`
93. `MACRO_093_F048R` | kind: `folio` | target: `F048R` | next: `MACRO_094_F048V`
94. `MACRO_094_F048V` | kind: `folio` | target: `F048V` | next: `MACRO_095_F049R`
95. `MACRO_095_F049R` | kind: `folio` | target: `F049R` | next: `MACRO_096_F049V`
96. `MACRO_096_F049V` | kind: `folio` | target: `F049V` | next: `MACRO_097_F050R`
97. `MACRO_097_F050R` | kind: `folio` | target: `F050R` | next: `MACRO_098_F050V`
98. `MACRO_098_F050V` | kind: `folio` | target: `F050V` | next: `MACRO_099_F051R`
99. `MACRO_099_F051R` | kind: `folio` | target: `F051R` | next: `MACRO_100_F051V`
100. `MACRO_100_F051V` | kind: `folio` | target: `F051V` | next: `MACRO_101_F052R`
101. `MACRO_101_F052R` | kind: `folio` | target: `F052R` | next: `MACRO_102_F052V`
102. `MACRO_102_F052V` | kind: `folio` | target: `F052V` | next: `MACRO_103_F053R`
103. `MACRO_103_F053R` | kind: `folio` | target: `F053R` | next: `MACRO_104_F053V`
104. `MACRO_104_F053V` | kind: `folio` | target: `F053V` | next: `MACRO_105_F054R`
105. `MACRO_105_F054R` | kind: `folio` | target: `F054R` | next: `MACRO_106_F054V`
106. `MACRO_106_F054V` | kind: `folio` | target: `F054V` | next: `MACRO_107_F055R`
107. `MACRO_107_F055R` | kind: `folio` | target: `F055R` | next: `MACRO_108_F055V`
108. `MACRO_108_F055V` | kind: `folio` | target: `F055V` | next: `MACRO_109_F056R`
109. `MACRO_109_F056R` | kind: `folio` | target: `F056R` | next: `MACRO_110_F056V`
110. `MACRO_110_F056V` | kind: `folio` | target: `F056V` | next: `MACRO_111_F057R`
111. `MACRO_111_F057R` | kind: `folio` | target: `F057R` | next: `MACRO_112_F057V`
112. `MACRO_112_F057V` | kind: `folio` | target: `F057V` | next: `MACRO_113_SECTION_SYNTHESIS`
113. `MACRO_113_SECTION_SYNTHESIS` | kind: `section_completion` | target: `Book I - Herbal / materia medica synthesis and crystal completion` | next: `MACRO_114_F058R`
114. `MACRO_114_F058R` | kind: `folio` | target: `F058R` | next: `MACRO_115_F058V`
115. `MACRO_115_F058V` | kind: `folio` | target: `F058V` | next: `MACRO_116_F065R`
116. `MACRO_116_F065R` | kind: `folio` | target: `F065R` | next: `MACRO_117_F065V`
117. `MACRO_117_F065V` | kind: `folio` | target: `F065V` | next: `MACRO_118_F066R`
118. `MACRO_118_F066R` | kind: `folio` | target: `F066R` | next: `MACRO_119_F066V`
119. `MACRO_119_F066V` | kind: `folio` | target: `F066V` | next: `MACRO_120_F069R`
120. `MACRO_120_F069R` | kind: `folio` | target: `F069R` | next: `MACRO_121_F071R`
121. `MACRO_121_F071R` | kind: `folio` | target: `F071R` | next: `MACRO_122_F071V`
122. `MACRO_122_F071V` | kind: `folio` | target: `F071V` | next: `MACRO_123_F073R`
123. `MACRO_123_F073R` | kind: `folio` | target: `F073R` | next: `MACRO_124_F073V`
124. `MACRO_124_F073V` | kind: `folio` | target: `F073V` | next: `MACRO_125_SECTION_SYNTHESIS`
125. `MACRO_125_SECTION_SYNTHESIS` | kind: `section_completion` | target: `Book II - Astronomical / astrological synthesis and crystal completion` | next: `MACRO_126_F075R`
126. `MACRO_126_F075R` | kind: `folio` | target: `F075R` | next: `MACRO_127_F075V`
127. `MACRO_127_F075V` | kind: `folio` | target: `F075V` | next: `MACRO_128_F076R`
128. `MACRO_128_F076R` | kind: `folio` | target: `F076R` | next: `MACRO_129_F076V`
129. `MACRO_129_F076V` | kind: `folio` | target: `F076V` | next: `MACRO_130_F077R`
130. `MACRO_130_F077R` | kind: `folio` | target: `F077R` | next: `MACRO_131_F077V`
131. `MACRO_131_F077V` | kind: `folio` | target: `F077V` | next: `MACRO_132_F078R`
132. `MACRO_132_F078R` | kind: `folio` | target: `F078R` | next: `MACRO_133_F078V`
133. `MACRO_133_F078V` | kind: `folio` | target: `F078V` | next: `MACRO_134_F079R`
134. `MACRO_134_F079R` | kind: `folio` | target: `F079R` | next: `MACRO_135_F079V`
135. `MACRO_135_F079V` | kind: `folio` | target: `F079V` | next: `MACRO_136_F080R`
136. `MACRO_136_F080R` | kind: `folio` | target: `F080R` | next: `MACRO_137_F080V`
137. `MACRO_137_F080V` | kind: `folio` | target: `F080V` | next: `MACRO_138_F081R`
138. `MACRO_138_F081R` | kind: `folio` | target: `F081R` | next: `MACRO_139_F081V`
139. `MACRO_139_F081V` | kind: `folio` | target: `F081V` | next: `MACRO_140_F082R`
140. `MACRO_140_F082R` | kind: `folio` | target: `F082R` | next: `MACRO_141_F082V`
141. `MACRO_141_F082V` | kind: `folio` | target: `F082V` | next: `MACRO_142_F083R`
142. `MACRO_142_F083R` | kind: `folio` | target: `F083R` | next: `MACRO_143_F083V`
143. `MACRO_143_F083V` | kind: `folio` | target: `F083V` | next: `MACRO_144_F084R`
144. `MACRO_144_F084R` | kind: `folio` | target: `F084R` | next: `MACRO_145_F084V`
145. `MACRO_145_F084V` | kind: `folio` | target: `F084V` | next: `MACRO_146_SECTION_SYNTHESIS`
146. `MACRO_146_SECTION_SYNTHESIS` | kind: `section_completion` | target: `Book III - Bath / balneological synthesis and crystal completion` | next: `MACRO_147_F087R`
147. `MACRO_147_F087R` | kind: `folio` | target: `F087R` | next: `MACRO_148_F087V`
148. `MACRO_148_F087V` | kind: `folio` | target: `F087V` | next: `MACRO_149_F088R`
149. `MACRO_149_F088R` | kind: `folio` | target: `F088R` | next: `MACRO_150_F088V`
150. `MACRO_150_F088V` | kind: `folio` | target: `F088V` | next: `MACRO_151_F093R`
151. `MACRO_151_F093R` | kind: `folio` | target: `F093R` | next: `MACRO_152_F093V`
152. `MACRO_152_F093V` | kind: `folio` | target: `F093V` | next: `MACRO_153_F094R`
153. `MACRO_153_F094R` | kind: `folio` | target: `F094R` | next: `MACRO_154_F094V`
154. `MACRO_154_F094V` | kind: `folio` | target: `F094V` | next: `MACRO_155_F096R`
155. `MACRO_155_F096R` | kind: `folio` | target: `F096R` | next: `MACRO_156_F096V`
156. `MACRO_156_F096V` | kind: `folio` | target: `F096V` | next: `MACRO_157_F099R`
157. `MACRO_157_F099R` | kind: `folio` | target: `F099R` | next: `MACRO_158_F099V`
158. `MACRO_158_F099V` | kind: `folio` | target: `F099V` | next: `MACRO_159_F100R`
159. `MACRO_159_F100R` | kind: `folio` | target: `F100R` | next: `MACRO_160_F100V`
160. `MACRO_160_F100V` | kind: `folio` | target: `F100V` | next: `MACRO_161_F103R`
161. `MACRO_161_F103R` | kind: `folio` | target: `F103R` | next: `MACRO_162_F103V`
162. `MACRO_162_F103V` | kind: `folio` | target: `F103V` | next: `MACRO_163_F104R`
163. `MACRO_163_F104R` | kind: `folio` | target: `F104R` | next: `MACRO_164_F104V`
164. `MACRO_164_F104V` | kind: `folio` | target: `F104V` | next: `MACRO_165_F105R`
165. `MACRO_165_F105R` | kind: `folio` | target: `F105R` | next: `MACRO_166_F105V`
166. `MACRO_166_F105V` | kind: `folio` | target: `F105V` | next: `MACRO_167_F106R`
167. `MACRO_167_F106R` | kind: `folio` | target: `F106R` | next: `MACRO_168_SECTION_SYNTHESIS`
168. `MACRO_168_SECTION_SYNTHESIS` | kind: `section_completion` | target: `Book V - Pharmaceutical 1 synthesis and crystal completion` | next: `MACRO_169_F106V`
169. `MACRO_169_F106V` | kind: `folio` | target: `F106V` | next: `MACRO_170_F107R`
170. `MACRO_170_F107R` | kind: `folio` | target: `F107R` | next: `MACRO_171_F107V`
171. `MACRO_171_F107V` | kind: `folio` | target: `F107V` | next: `MACRO_172_F108R`
172. `MACRO_172_F108R` | kind: `folio` | target: `F108R` | next: `MACRO_173_F108V`
173. `MACRO_173_F108V` | kind: `folio` | target: `F108V` | next: `MACRO_174_F111R`
174. `MACRO_174_F111R` | kind: `folio` | target: `F111R` | next: `MACRO_175_F111V`
175. `MACRO_175_F111V` | kind: `folio` | target: `F111V` | next: `MACRO_176_F112R`
176. `MACRO_176_F112R` | kind: `folio` | target: `F112R` | next: `MACRO_177_F112V`
177. `MACRO_177_F112V` | kind: `folio` | target: `F112V` | next: `MACRO_178_F113R`
178. `MACRO_178_F113R` | kind: `folio` | target: `F113R` | next: `MACRO_179_F113V`
179. `MACRO_179_F113V` | kind: `folio` | target: `F113V` | next: `MACRO_180_F114R`
180. `MACRO_180_F114R` | kind: `folio` | target: `F114R` | next: `MACRO_181_F114V`
181. `MACRO_181_F114V` | kind: `folio` | target: `F114V` | next: `MACRO_182_F115R`
182. `MACRO_182_F115R` | kind: `folio` | target: `F115R` | next: `MACRO_183_F115V`
183. `MACRO_183_F115V` | kind: `folio` | target: `F115V` | next: `MACRO_184_F116R`
184. `MACRO_184_F116R` | kind: `folio` | target: `F116R` | next: `MACRO_185_F116V`
185. `MACRO_185_F116V` | kind: `folio` | target: `F116V` | next: `MACRO_186_SECTION_SYNTHESIS`
186. `MACRO_186_SECTION_SYNTHESIS` | kind: `section_completion` | target: `Book V - Pharmaceutical 2 synthesis and crystal completion` | next: `MACRO_187_MANUSCRIPT_TERMINUS`
187. `MACRO_187_MANUSCRIPT_TERMINUS` | kind: `terminal_completion` | target: `Manuscript terminal completion` | next: `STOP`
