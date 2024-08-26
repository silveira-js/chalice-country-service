#!/bin/bash

# Create a minimal config for deletion
python delete_config.py

# Run chalice delete
chalice delete --stage dev
