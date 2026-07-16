from enum import StrEnum

class FlowStatus(StrEnum):
    ACTIVE="ACTIVE"; PENDING="PENDING"; CLOSED="CLOSED"; SPLIT="SPLIT"; SKIPPED="SKIPPED"; ARCHIVED="ARCHIVED"
class Stage(StrEnum):
    UNDERSTANDING="UNDERSTANDING"; PRACTICING="PRACTICING"; EXTRACTING="EXTRACTING"; ASSESSING="ASSESSING"; DONE="DONE"
class Mastery(StrEnum):
    UNTESTED="UNTESTED"; FRAGILE="FRAGILE"; DEVELOPING="DEVELOPING"; RELIABLE="RELIABLE"; MAINTAINED="MAINTAINED"
class Importance(StrEnum):
    CORE="CORE"; NORMAL="NORMAL"; LOW="LOW"
class TestResult(StrEnum):
    INDEPENDENT="INDEPENDENT"; HINTED="HINTED"; REVEALED="REVEALED"; FAILED="FAILED"; NOT_TESTED="NOT_TESTED"
class EvidenceLevel(StrEnum):
    NONE="NONE"; GENERAL="GENERAL"; REFERENCE="REFERENCE"; OBJECTIVE="OBJECTIVE"
class ReviewPool(StrEnum):
    SHORT="SHORT"; ROUND="ROUND"; LONG="LONG"

SUBJECTS=("数学","408","英语","政治")
TERMINAL={FlowStatus.CLOSED,FlowStatus.SPLIT,FlowStatus.SKIPPED,FlowStatus.ARCHIVED}

def mastery_from_results(recall: TestResult, application: TestResult, prior: Mastery, independent_passes: int) -> Mastery:
    if TestResult.FAILED in (recall, application): return Mastery.FRAGILE
    if TestResult.NOT_TESTED in (recall, application): return Mastery.DEVELOPING if TestResult.INDEPENDENT in (recall,application) else Mastery.UNTESTED
    if recall==TestResult.INDEPENDENT and application==TestResult.INDEPENDENT:
        return Mastery.MAINTAINED if independent_passes >= 2 else Mastery.RELIABLE
    return Mastery.DEVELOPING
