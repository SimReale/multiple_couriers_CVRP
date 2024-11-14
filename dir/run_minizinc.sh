#!/bin/bash
SOLVER="org.gecode.gecode"
MODEL="CP_proj.mzn"
DATA="inst06.dzn"
minizinc --solver $SOLVER $MODEL $DATA