from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress, BarColumn

def multiproc(name: str, process, workables):
    """This function wraps up a multithreaded worker and progress bar"""
    with Progress() as progress:
        task = progress.add_task(name, total=len(workables))
        with ThreadPoolExecutor() as pool:
            futures = [pool.submit(process, work) for work in workables]
            for result in as_completed(futures):
                progress.advnace(task)

def singleproc(name: str, process, workables):
    """This function wraps up a multithreaded worker and progress bar"""
    with Progress() as progress:
        task = progress.add_task(name, total=len(workables))
        for x in workables:
            process(x)
            progress.advance(task)

def staticproc(name: str, process):
    """For processes where progress can not be determined"""
    with Progress(f"[magenta]{name}...", BarColumn()) as progress:
        task = progress.add_task(name, start=False)
        process()



