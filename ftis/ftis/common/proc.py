from concurrent.futures import ThreadPoolExecutor
from rich.progress import Progress, BarColumn

def multiproc(name: str, process, workables):
    """
    This function wraps up the necessary functionality for a multithreaded loop with progres bar
    """
    with Progress() as progress:
        task = progress.add_task(name, total=len(workables))
        with ThreadPoolExecutor() as pool:
            for work in workables:
                pool.submit(process, work, task, progress)


def staticproc(name: str, process):
    """For processes where progress can not be determined"""
    with Progress(f"[magenta]{name}...", BarColumn()) as progress:
        task = progress.add_task(name, start=False)
        process()



