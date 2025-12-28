from . import step_0_welcome
from . import step_1_transaction
from . import step_2_flink
from . import step_3_detective
from . import step_4_judge
from . import step_5_enforcer
from . import step_6_summary

STEP_REGISTRY = {
    0: step_0_welcome,
    1: step_1_transaction,
    2: step_2_flink,
    3: step_3_detective,
    4: step_4_judge,
    5: step_5_enforcer,
    6: step_6_summary
}
