include "globals.mzn";
include "gecode.mzn";

% ========= PARAMETERS ========= %

int: m;		% couriers
int: n; 	% items
array[1..m] of int: l;
array[1..n] of int: s;
array[1..n+1, 1..n+1] of int: distances;
int: perc = if n<=20 then 0 else 80 endif;


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
constraint bin_packing_capa(l, bins, s) ::bounds;

% load assignment
constraint bin_packing_load(load, bins, s) ::bounds;

% each courier must take an item
constraint forall(i in 1..m)(
 	x[i, n+1] != n+1
)::bounds;
%constraint count(i in 1..m)(x[i,n+1]==n+1) == 0 ::domain;

% couriers assignment for each pack
constraint forall(i in 1..m, j in 1..n)( 
	if bins[j] == i then x[i,j] != j else x[i,j] == j endif
)::bounds;

%path construction
constraint forall(i in 1..m)(	
	subcircuit(x[i,..])
) ::bounds;



% ========= OBJECTIVE FUNCTION ========= %

int: min_dist = max(i in 1..n)( distances[n+1, i] + distances[i, n+1] );
int: max_dist = sum(i in 1..n+1)( max(distances[i,..]) );

var min_dist..max_dist: dist = max(i in 1..m)( sum(j in 1..n+1 where x[i,j] != j)(distances[j, x[i,j]]) );



solve 
	:: int_default_search(afc_size_max, indomain_random)
	:: restart_luby(m*n)
	:: relax_and_reconstruct(array1d(x), perc)
minimize dist;