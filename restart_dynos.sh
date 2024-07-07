#!/bin/bash

curl -n -X DELETE https://api.heroku.com/apps/in-betweens/dynos \
-H "Accept: application/vnd.heroku+json; version=3" \
-H "Authorization: Bearer $API_KEY"