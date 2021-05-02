#!/usr/bin/env bash

parse() {
	echo "parsing log"
	python parser.py
}

repository() {
	echo "updating repo"
	git add --all
	git commit -m "update"
	git push -u origin master
}

database() {
	echo "connecting to database"
	mysql -h $SQLhost -u $SQLuser --password=$SQLpass
}

helper() {
	echo "commands:"
	echo "parse       parses log"
	echo "repo        updates repository"
	echo "database    logs into database (use 'source parse.sql' afterwards)"
}

while true
do
	echo -n "shgmg>"
	read text

	if [ $text = "parse" ]; then parse
	elif [ $text = "repo" ]; then repository
	elif [ $text = "database" ]; then database
	elif [ $text = "help" ]; then helper
	elif [ $text = "exit" ]; then exit
	fi
done
