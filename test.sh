python3 -m unittest discover || echo "to run live test set API_KEY env variable"
mypy nuclino --ignore-missing-imports
