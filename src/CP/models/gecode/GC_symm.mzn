include "globals.mzn";
include "gecode.mzn";

% ========= PARAMETERS ========= %

int: m;		% couriers
int: n; 	% items
array[1..m] of int: l;
array[1..n] of int: s;
array[1..n+1, 1..n+1] of int: distances;



% ========= DECISION VARIABLES ========= %

% couriers assignments
array[1..n] of var 1..m: bins;
% paths assignments
array[1..m, 1..n+1] of var 1..n+1: x;



% ========= AUXILIARY VARIABLES ========= %

% loads assignments
int: min_load = min(s);
int: max_load = max(l);
array[1..m] of var min_load..max_load: load;


% ========= CONSTRAINTS ========= %

% the load carried by each courier must be lower than the maximum load given in input
constraint bin_packing_capa(l, bins, s);

% load assignment
constraint bin_packing_load(load, bins, s);

% each courier must take an item
constraint forall(i in 1..m)(
 	x[i, n+1] != n+1
);

% couriers assignment for each pack
constraint forall(i in 1..m, j in 1..n)( 
	if bins[j] == i then x[i,j] != j else x[i,j] == j endif
);

%path construction
constraint forall(i in 1..m)(	
	subcircuit(x[i,..])
);



% ========= SYMMETRY BREAKING CONSTRAINTS ========= %

constraint forall(i in 1..n, j in i+1..n)(
	if s[i] == s[j] /\ load[bins[i]] == load[bins[j]] then lex_lesseq([bins[i]], [bins[j]]) endif
);

%constraint forall(i in 1..m, j in i+1..m)(
%	if l[i] == l[j] then load[i]<=load[j] endif
%	);



% ========= OBJECTIVE FUNCTION ========= %

int: min_dist = max(i in 1..n)( distances[n+1, i] + distances[i, n+1] );
int: max_dist = sum(i in 1..n+1)(max(distances[i,..]));

var min_dist..max_dist: dist = max(i in 1..m)( sum(j in 1..n+1 where x[i,j] != j)( distances[j, x[i,j]] ) );



solve 
	:: int_default_search(afc_size_max, indomain_random)
%	:: int_search([x[i,j] | i in arg_sort(l), j in 1..n+1], first_fail, indomain_min)
	:: restart_luby(m*n)
	:: relax_and_reconstruct(array1d(x), 80)
minimize dist;