#!/usr/bin/env bash

tput clear

tput cup 9 43
tput setaf 1
tput bold
echo "WHAT KNOWLEDGE WILL WE RIP OUT OF THE HANDS OF THE GODS, TODAY?"
tput sgr0

tput cup 12 42
echo '------------------------------ [X] ------------------------------'
tput cup 15 42
read -p "[>>»]: " choice
echo "${choice}" > srch_q_choice.txt
tput clear
tput sgr0
tput rc