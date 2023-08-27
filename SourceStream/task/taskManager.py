from .. import SourceStream;

#tasks
from .tasks import modifyEdition, repackPackages

def run():
    TASKS_ENABLED = SourceStream.TASK_TYPES_ENABLED;

    if(TASKS_ENABLED["REPACK_PACKAGES"]):
        repackPackages.run()

    if(TASKS_ENABLED["MODIFY_EDITION"]):
        modifyEdition.run()