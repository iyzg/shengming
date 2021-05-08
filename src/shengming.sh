#!/usr/bin/env bash

parse() {
	echo "parsing log"
	python parser.py
}

repository() {
	echo "updating repo"
	git add --all
	git commit -m "update"
	git push
}

generate() {
	echo "generating static site"
	python generator.py
}

helper() {
	echo "commands:"
	echo "parse     parses log"
	echo "repo      updates repository"
	echo "gen	updates repository"
}

while true
do
	echo -n "shengming>"
	read text

	if [ $text = "parse" ]; then parse
	elif [ $text = "repo" ]; then repository
	elif [ $text = "gen" ]; then generate 
	elif [ $text = "help" ]; then helper
	elif [ $text = "exit" ]; then exit
	fi
done
