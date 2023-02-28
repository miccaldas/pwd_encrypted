#!/usr/bin/env bash

tput clear

tput cup 7 81
tput setaf 1
tput bold
echo "ADD PASSWORD"
tput sgr0

tput cup 9 76
echo '--------- [X] ---------'
tput cup 11 75
read -p '[»»] What is the name of the site? : ' choice
echo "${choice}" > sitio_choice.txt
tput cup 13 71
read -p "[»»] What is the username? : " choice
echo "${choice}" > username_choice.txt
tput cup 15 58
read -p "('[»»] Do you want to name the password yourself? [y/n] ',): " choice
echo "${choice}" > author_choice.txt
tput clear
tput sgr0
tput rc