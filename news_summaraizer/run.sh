#!/bin/bash

docker build -t techcrunch-summarizer .
docker run --rm -e GEMINI_API_KEY="GEMINI_API_TOKEN" techcrunch-summarizer