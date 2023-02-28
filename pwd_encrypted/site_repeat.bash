#!/usr/bin/env bash

tput clear

tput cup 7 81
tput setaf 1
tput bold
echo "WARNING!"
tput sgr0

tput cup 9 76
echo '--------- [X] ---------'
tput cup 11 58
echo "{warning_str}"
tput cup 14 58
