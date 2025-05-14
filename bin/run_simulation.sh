#!/bin/bash

# Wrapper script for the Health Insurance AU simulation

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the Python application with the provided arguments
python3 -m health_insurance_au.main "$@"