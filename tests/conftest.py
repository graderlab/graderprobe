import os
import tempfile

# Tests are offline by design: cache goes to a temp dir and the sync endpoint
# points at a dead local port so nothing ever leaves the machine.
os.environ["GRADERPROBE_CACHE_DIR"] = tempfile.mkdtemp(prefix="graderprobe-tests-")
os.environ["GRADERPROBE_SYNC_URL"] = "http://127.0.0.1:1/api/graderlab/sync"
