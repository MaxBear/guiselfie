#!/usr/bin/env bash

export APPLICATION_SETTINGS="$PWD/selfie/configs/env_prod.py"

echo '########################'
echo ' Launch nocadmin portal in production env'
echo '########################'
python run_dev.py
