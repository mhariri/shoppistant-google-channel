#!/bin/bash

gcloud preview app deploy app.yaml --project shoppistant-googl-channel
echo
gcloud preview app modules list --project shoppistant-googl-channel
echo
echo
echo "Now set the default serving version by the following command:"
echo gcloud preview app modules --project shoppistant-googl-channel set-default default --version X
