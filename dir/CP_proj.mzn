include "globals.mzn";

%%%%%%%%% PARAMETERS %%%%%%%%%%%

int: m; 
int: n;
array[1..m] of int: l; 
array[1..n] of int: s;
array[1..n+1, 1..n+1] of int: distances;

int: max_dist = sum([max([distances[i, j] | j in 1..n+1]) | i in 1..n+1]);
int: max_load = max(l);



%%%%%%%%%% VARIABLES %%%%%%%%%%%%

% path
array[1..m, 1..n+1] of var 1..n+1: x;
% distance traveled
array[1..m] of var 0..max_dist: y;
% load carried
array[1..m] of var 0..max_load: load;



%%%%%%%%%% CONSTRAINTS %%%%%%%%%%%

% the load carried by each courier must be lower than the maximum load given in input
constraint forall(i in 1..m)(
	load[i] = sum([(if x[i,j] != j then s[j] else 0 endif) | j in 1..n]) /\
	load[i] <= l[i]
	);

% the courier must end in the depot
constraint forall(i in 1..m)(
	if x[i,n+1] != n+1 then count([x[i,j] | j in 1..n+1], n+1, 1)
	else forall(k in 1..n+1)(x[i,k] = k) endif
	);

% total path
constraint forall(i in 1..m)(
	y[i] = sum([(if x[i,j] != j then distances[j,x[i,j]] else 0 endif) | j in 1..n+1])
	);
	
% resources, one per column
constraint forall(j in 1..n)(
	count([x[i,j] | i in 1..m], j, m-1)
	);
	
% path construction
constraint forall(i in 1..m)(
	subcircuit([x[i,j] | j in 1..n+1])
	);

% redundant
constraint forall(i in 1..m)(
	alldifferent([x[i,j] | j in 1..n+1])
	);




%%%%%%%%%% SYMMETRY BRAKING CONSTRAINTS %%%%%%%%%%%%
%constraint forall(i,j in 1..m where i!=j)(
%	if l[i] == l[j] then load[i] <= load[j] endif
%	);

constraint forall(i in 1..m)(
	load[i] > 0
	);

solve minimize max(y);