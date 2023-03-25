#!/usr/bin/env bash

tput clear

tput cup 9 50
tput setaf 1
tput bold
echo "THIS IS WHAT YOUR INSATIABLE CURIOSITY GETS YOU!"
tput sgr0

tput cup 12 42
echo '------------------------------ [X] ------------------------------'
tput cup 15 37
echo '+-------------------------------------------------------------------------+'
tput cup 16 37
echo '| id      | 3                                                             |'
tput cup 17 37
echo '| site    | fonseca.com                                                   |'
tput cup 18 37
echo '| user    | micas                                                         |'
tput cup 19 37
echo '| pwd     | Zo(1<&^|jTn3                                                  |'
tput cup 20 37
echo '| comment | nice coment                                                   |'
tput cup 21 37
echo '| time    | 2021-01-26 04:49:55                                           |'
tput cup 22 37
echo '+-------------------------------------------------------------------------+'
tput cup 35 37
read -p 'Press any key to exit. ' choice
echo "${choice}" > /dev/null
tput clear
tput sgr0
tput rc