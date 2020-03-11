import argparse
from ftis.process import FTISProcess

parser = argparse.ArgumentParser(description="The entry point to ftis.")
parser.add_argument(
    "-c", "--config", type=str, required=True, help="A YAML configurations"
)
args = parser.parse_args()

if __name__ == "__main__":
    # Create an instance of the FTISProcess
    process = FTISProcess(args.config)
    process.run_process()
