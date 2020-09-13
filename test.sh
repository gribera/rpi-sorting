#!/bin/bash

gpio -g mode 6 out
gpio -g mode 13 out
gpio -g mode 19 out
gpio -g mode 26 out

gpio -g write 6 0
gpio -g write 13 0
gpio -g write 19 0
gpio -g write 26 0
