#!/usr/bin/env bash

export APPLICATION_SETTINGS="$PWD/selfie/configs/env_dev.py"

echo '########################'
echo ' Launch selfie portal in development env'
echo '########################'
python run_dev.py
