import subprocess
import logging

logger = logging.getLogger(__name__)

def run_shell(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        logger.info("Command executed: %s", cmd)
        return output
    except Exception as e:
        logger.exception("Shell execution failed")
        return str(e)
