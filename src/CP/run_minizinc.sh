#!/bin/bash
SOLVER="org.gecode.gecode"
MODEL="CP_proj.mzn"
DATA="inst02.dzn"
minizinc --solver $SOLVER $MODEL $DATA