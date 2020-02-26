import argparse
from ftis.common.utils import read_yaml
from ftis.process import FTISProcess

parser = argparse.ArgumentParser(description='The entry point to ftis.')
parser.add_argument('-c', '--config', type=str, required=True, help='A YAML configurations')
args = parser.parse_args()

# Create an instance of the FTISContainer which holds the lifecycle of an ftis process
process = FTISProcess()
process.config = read_yaml(args.config) # Load a configuration file
process.run_process()

# process.process_config() # Parse/process the YAML

# print(process.config)
