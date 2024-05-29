from .. import SourceStream;

#tasks
from .tasks import upstreamUpgrade, repackPackages, service

def run():
    TASKS_ENABLED = SourceStream.TASK_TYPES_ENABLED;
    if(SourceStream.AS_SERVICE):
        service.run()
        

    elif(TASKS_ENABLED["REPACK_PACKAGES"]):
        repackPackages.run()

    elif(TASKS_ENABLED["UPSTREAM_UPGRADE"]):
        upstreamUpgrade.run()