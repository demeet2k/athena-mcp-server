import hashlib
import json

SOURCE_PACKET_COMMIT="c1858bcbc6587296c2b8a7e29642bfef695fdb2a"
SOURCE_PACKET_BLOB_SHA="1dabde8f450f237d28cf230ff2bb5d9e8d729c8e"
SOURCE_PACKET_PATH="registry/mythic_holonomy_heldout_v0.json"
SOURCE_PACKET_CANONICAL_SHA256="3ecc6a6db7a649d73a7d6d3b5d62382060fdfb5d25006ac9610a444e72311129"
FIXTURE_STANDING="SOURCE_PACKET_SEMANTIC_PROJECTION_FOR_EXECUTION; NOT_INDEPENDENT_SOURCE_COPY; NOT_REMOTE_READ"
FIXTURE_PROJECTION_POLICY={
    "semantic_target":"CANONICAL_JSON_EQUAL_TO_FROZEN_SOURCE_PACKET",
    "source_packet_blob_sha":SOURCE_PACKET_BLOB_SHA,
    "remote_source_verified_at_runtime":False,
    "projection_is_independent_evidence":False,
    "known_semantic_omissions":[],
}


def L(layer_id,role,decoder,tags,loss=None,authority="PUBLIC_TEXTUAL_MODEL",source_layer="",invariants=None):
    return {
        "layer_id":layer_id,
        "semantic_role":role,
        "decoder_role":decoder,
        "ontology_tags":list(tags),
        "authority_scope":authority,
        "standing":"SECONDARY_SCHOLARSHIP",
        "provenance":[],
        "source_language_or_text_layer":source_layer,
        "invariants":list(invariants or []),
        "declared_loss":list(loss or []),
    }


def C(case_id,family,path,op,expected,source,inv=None,loss=None,notes=None):
    out={"case_id":case_id,"family_id":family,"path":list(path),"operation":op,"expected_class":expected,"source_refs":[source]}
    if inv:out["bridge_invariants"]=list(inv)
    if loss:out["declared_loss"]=list(loss)
    if notes:out["notes"]=list(notes)
    return out


H01="SRC.SEP.YIJING";H02="SRC.CAMBRIDGE.GARB.KABBALAH.2020";H03="SRC.CAMBRIDGE.GOLDSTEIN.IBN_EZRA"
FAMILIES=[
 {"family_id":"H01.YIJING","name":"Yijing composite textual/commentarial strata","source_refs":[H01],"held_out_from":["REGRESSION12","STRATA10_PRIMARY_DESIGN_SET"],"layers":[
  L("H01.S0.GRAPHIC_SYMBOLS","graphic divinatory/change symbols","symbolic pattern/address layer",["trigrams","hexagrams","change","graphic_symbols"],source_layer="received graphic trigrams/hexagrams as described by SEP",invariants=["8-trigram/64-hexagram graphic address family remains identifiable across later textual layers"]),
  L("H01.S1.HEXAGRAM_LINE_STATEMENTS","written hexagram and line statements attached to graphic symbols","textual statement layer used to interpret hexagram/line configurations",["hexagrams","line_statements","historical_events","divination_reports"],["graphic-only role is expanded by attached textual statements"],source_layer="hexagram and line statement layer",invariants=["graphic hexagram identity remains addressable"]),
  L("H01.S2.TEN_WINGS","later commentarial-philosophical writings interpreting symbols and statements","philosophical/cosmological commentary layer",["hexagrams","Ten_Wings","cosmic_patterns","human_nature_relations","philosophy"],["later philosophical/cosmological interpretive roles are not identical to earlier graphic or statement roles"],source_layer="Ten Wings / later writings dated by scholarship to roughly 5th-2nd century BCE",invariants=["hexagram/line corpus remains the object of commentary"]),
  L("H01.S3.ZHU_XI_COMMENTARY","later commentary distinguishing classic hexagram materials from commentarial materials","meta-commentarial classification/interpretation layer",["classic_jing","commentary_zhuan","hexagrams","Ten_Wings","moral_cosmological_interpretation"],["later classification is a retrospective organization of earlier layers"],source_layer="later Zhu Xi commentarial layer as summarized by SEP",invariants=["classic/commentary distinction explicitly preserves layer difference"])]},
 {"family_id":"H02.KABBALAH","name":"Premodern to modern Kabbalah: breaks and continuities","source_refs":[H02],"held_out_from":["REGRESSION12","STRATA10_PRIMARY_DESIGN_SET"],"layers":[
  L("H02.S0.PREMODERN","premodern kabbalistic textual/theosophical traditions","premodern exegesis/theosophy/theurgy within historical source traditions",["exegesis","sacral_texts","sefirotic_theosophy","theurgy","medieval_Kabbalah"],authority="HISTORICAL_TRADITION_SCOPE",source_layer="premodern/medieval Kabbalah summarized in modern scholarship",invariants=["selected sacral-text/exegetical and theosophical themes recur into later periods"]),
  L("H02.S1.EARLY_MODERN_SAFEDIAN","early-modern/Safedian transformation and canon-forming developments","early-modern reinterpretive and canonical development layer",["Safed","early_modern","canonization","Lurianic_corpus","exegesis","theosophy"],["period-specific schools, crises and canonization alter context and emphasis"],"HISTORICAL_TRADITION_SCOPE",source_layer="early-modern developments treated in Garb's historical periodization",invariants=["some premodern textual/theosophical themes remain historically connected"]),
  L("H02.S2.MODERN","modern Kabbalah as historically autonomous yet continuous with premodern traditions","modern textual, experiential, organizational and exoteric interpretive contexts",["modern_Kabbalah","exegesis","theosophy","fraternal_groups","vernacularization","technology","globalization"],["modernity introduces autonomous forms shaped by technology, geopolitical/ideological change, vernacularization and new social organization"],"MODERN_HISTORICAL_TRADITION_SCOPE",source_layer="modern Kabbalah in Garb's historical analysis",invariants=["continuity with selected premodern themes is source-supported"])]},
 {"family_id":"H03.IBN_EZRA_TRANSMISSION","name":"Arabic to Hebrew to Latin astronomy/astrology transmission through Abraham ibn Ezra","source_refs":[H03],"held_out_from":["REGRESSION12","STRATA10_PRIMARY_DESIGN_SET"],"layers":[
  L("H03.S0.ARABIC_SOURCES","Arabic scientific/astronomical/astrological source tradition available to Ibn Ezra","Arabic-language technical/scientific source layer",["Arabic_science","astronomy","astrology","technical_methods"],["some Arabic originals are no longer extant; reconstruction is source-conditioned"],"HISTORICAL_SCHOLARLY_SOURCE_SCOPE",source_layer="Arabic source tradition as reconstructed in scholarship",invariants=["source scholarship documents Arabic material in the transmission lineage"]),
  L("H03.S1.HEBREW_IBN_EZRA","Ibn Ezra's Hebrew astronomical/astrological works and translations/adaptations","Hebrew-language technical scholarly transmission layer",["Hebrew_scientific_writing","astronomy","astrology","Ibn_Ezra","technical_methods"],["selection, translation and reformulation occur in the Hebrew transmission layer"],"HISTORICAL_SCHOLARLY_SOURCE_SCOPE",source_layer="Hebrew works of Abraham ibn Ezra",invariants=["Arabic scientific material remains traceable in the documented transmission"]),
  L("H03.S2.LATIN_RECEPTION","Latin translation and medieval Jewish/Christian reception of Ibn Ezra's works","Latin-language translation/reception layer in medieval Western scholarly contexts",["Latin_translation","astronomy","astrology","medieval_reception","Ibn_Ezra"],["language, audience and reception context change across Hebrew-to-Latin transmission"],"HISTORICAL_SCHOLARLY_SOURCE_SCOPE",source_layer="Latin translations/reception of Hebrew Ibn Ezra works",invariants=["documented work/source lineage remains traceable through translation"])]}
]
for fam in FAMILIES:
    for layer in fam["layers"]:layer["provenance"]=list(fam["source_refs"])

CASES=[
 C("HOL-H01-01","H01.YIJING",["H01.S0.GRAPHIC_SYMBOLS","H01.S1.HEXAGRAM_LINE_STATEMENTS"],"SEMANTIC_TRANSPORT","ALLOW_WITH_LOSS",H01,["hexagram identity remains addressable"],["graphic symbolic role is expanded by textual statements"]),
 C("HOL-H01-02","H01.YIJING",["H01.S1.HEXAGRAM_LINE_STATEMENTS","H01.S2.TEN_WINGS"],"SEMANTIC_TRANSPORT","ALLOW_WITH_LOSS",H01,["hexagram/line materials remain objects of interpretation"],["later philosophical/cosmological commentary changes decoder role"]),
 C("HOL-H01-03","H01.YIJING",["H01.S2.TEN_WINGS","H01.S3.ZHU_XI_COMMENTARY"],"SEMANTIC_TRANSPORT","ALLOW_WITH_LOSS",H01,["classic and commentary remain distinguishable textual strata"],["later commentary retrospectively reorganizes earlier materials"]),
 C("HOL-H01-04","H01.YIJING",["H01.S0.GRAPHIC_SYMBOLS","H01.S1.HEXAGRAM_LINE_STATEMENTS","H01.S2.TEN_WINGS","H01.S3.ZHU_XI_COMMENTARY","H01.S0.GRAPHIC_SYMBOLS"],"HOLONOMY_LOOP","NONZERO_HOLONOMY_EXPECTED",H01,["original graphic address remains identifiable"],["statement, philosophical and meta-commentarial role changes cannot be projected back as original-role identity"]),
 C("HOL-H01-05","H01.YIJING",["H01.S0.GRAPHIC_SYMBOLS","H01.S0.GRAPHIC_SYMBOLS"],"SAME_LAYER_CONTROL","ZERO_HOLONOMY_CONTROL",H01),
 C("HOL-H02-01","H02.KABBALAH",["H02.S0.PREMODERN","H02.S1.EARLY_MODERN_SAFEDIAN"],"SEMANTIC_TRANSPORT","ALLOW_WITH_LOSS",H02,["selected exegetical/theosophical continuities remain source-supported"],["early-modern schools/canonization change historical context and emphasis"]),
 C("HOL-H02-02","H02.KABBALAH",["H02.S1.EARLY_MODERN_SAFEDIAN","H02.S2.MODERN"],"SEMANTIC_TRANSPORT","ALLOW_WITH_LOSS",H02,["some recurrent themes remain historically connected"],["modern technologies, social forms, vernacularization and historical conditions produce autonomous modern configurations"]),
 C("HOL-H02-03","H02.KABBALAH",["H02.S2.MODERN","H02.S0.PREMODERN"],"SEMANTIC_EQUIVALENCE","HOLD_EQUIVALENCE",H02,notes=["Source-supported continuity does not establish backward identity/equivalence."]),
 C("HOL-H02-04","H02.KABBALAH",["H02.S0.PREMODERN","H02.S1.EARLY_MODERN_SAFEDIAN","H02.S2.MODERN","H02.S0.PREMODERN"],"HOLONOMY_LOOP","NONZERO_HOLONOMY_EXPECTED",H02,["preserve explicitly source-backed continuities"],["autonomy and modern transformations prevent lossless return to premodern role/context"]),
 C("HOL-H02-05","H02.KABBALAH",["H02.S0.PREMODERN","H02.S0.PREMODERN"],"SAME_LAYER_CONTROL","ZERO_HOLONOMY_CONTROL",H02),
 C("HOL-H03-01","H03.IBN_EZRA_TRANSMISSION",["H03.S0.ARABIC_SOURCES","H03.S1.HEBREW_IBN_EZRA"],"SEMANTIC_TRANSPORT","ALLOW_WITH_LOSS",H03,["documented Arabic-source lineage remains attached"],["selection/translation/reformulation in the Hebrew transmission layer"]),
 C("HOL-H03-02","H03.IBN_EZRA_TRANSMISSION",["H03.S1.HEBREW_IBN_EZRA","H03.S2.LATIN_RECEPTION"],"SEMANTIC_TRANSPORT","ALLOW_WITH_LOSS",H03,["Ibn Ezra work/source lineage remains traceable"],["language, audience and reception context change across Hebrew-to-Latin translation"]),
 C("HOL-H03-03","H03.IBN_EZRA_TRANSMISSION",["H03.S0.ARABIC_SOURCES","H03.S2.LATIN_RECEPTION"],"SEMANTIC_EQUIVALENCE","HOLD_EQUIVALENCE",H03,notes=["Historical transmission does not imply source/translation identity or lossless equivalence."]),
 C("HOL-H03-04","H03.IBN_EZRA_TRANSMISSION",["H03.S0.ARABIC_SOURCES","H03.S1.HEBREW_IBN_EZRA","H03.S2.LATIN_RECEPTION"],"PATH_ORDER_COMPARE","NONCOMMUTATIVE_EXPECTED",H03,["documented transmission order is part of provenance"],["permuting Arabic->Hebrew->Latin order destroys the documented transmission path"],["Compare canonical source order against a deliberately permuted path; path composition should not be treated as commutative."]),
 C("HOL-H03-05","H03.IBN_EZRA_TRANSMISSION",["H03.S1.HEBREW_IBN_EZRA","H03.S1.HEBREW_IBN_EZRA"],"SAME_LAYER_CONTROL","ZERO_HOLONOMY_CONTROL",H03)
]
PACKET={
 "artifact":"ATHENA.MYTHIC.HOLONOMY.HELDOUT.V0",
 "version":"MCK.HOLONOMY.BENCH.V0",
 "knowledge_base":"c0065074e5ba2f7d0dcc92b0ba9aa202aa769a54",
 "parent_issue":193,
 "standing":"FROZEN_HELD_OUT_SOURCE_PACKET_CANDIDATE",
 "families":FAMILIES,
 "cases":CASES,
 "distance_semantics":{
   "vector":[
     "role_delta: 0 if semantic_role unchanged else 1",
     "decoder_delta: 0 if decoder_role unchanged else 1",
     "ontology_delta: Jaccard distance over explicit ontology_tags",
     "authority_delta: 0 if authority_scope unchanged else 1; stronger authority without external evidence is a hard violation",
     "standing_delta: output standing may not exceed min(input, bridge evidence ceiling); positive amplification is a hard violation",
     "provenance_delta: fraction of required source/path provenance identifiers missing from output",
     "invariant_violations: count of declared bridge/path invariants not preserved",
     "unaccounted_loss: count of typed feature changes not covered by declared_loss ledger"
   ],
   "scalarization":"DISABLED_V0",
   "standing_ranks":{"UNKNOWN":0,"MODERN_RECONSTRUCTION":1,"TRADITION_INTERNAL":1,"SECONDARY_SCHOLARSHIP":2,"LIVING_TRADITION_SOURCE":2,"PRIMARY_EVIDENCE":3}
 },
 "firewalls":[
   "HELD_OUT_SOURCE_CASE != PRACTITIONER_VALIDATION",
   "SEMANTIC_DRIFT != ERROR_BY_DEFAULT",
   "CONTINUITY != IDENTITY",
   "TRANSLATION != LOSSLESS_EQUIVALENCE",
   "COMMENTARY != ORIGINAL_LAYER",
   "H_gamma != METAPHYSICAL_QUANTITY",
   "SOURCE_DERIVED_FEATURE_ENCODING != OBJECTIVE_SEMANTIC_GROUND_TRUTH",
   "SELF_GENERATED_SCORE != INDEPENDENT_WITNESS",
   "BENCHMARK_GAIN != MCK_V2_PROMOTION"
 ]
}


def canonical_packet_sha256(packet=PACKET):
    payload=json.dumps(packet,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()
