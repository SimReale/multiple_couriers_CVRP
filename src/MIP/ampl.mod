#parameters
param m >=0;
param n >=0;

#set
set COURIERS := {1..m};
set ITEMS := {1..n};
set V := {1..n+1}; #n+1 is the depot

#additional parameters
param l{COURIERS} integer; #array of capacity of each coureirs
param s{ITEMS} integer; #array of size of each packs
param D{i in V, j in V} integer; #matrix of D

param UpBound := sum{i in V}(max{j in V}(D[i, j]));
param LoBound := max{i in ITEMS}(D[n+1,i] + D[i,n+1]);

#param max_dist := sum {i in 0..n} max {j in 0..n} D[i, j];

#variables
var x {V, V, COURIERS} binary; #xijc = 1 iﬀ vehicle c moves from node i to j; 0 otherwise
var y {ITEMS, COURIERS} binary; #yic = 1 iﬀ vehicle c visits node i ; 0 otherwise
var u {V, COURIERS} >= 1 <= n + 1; #uic is the cumulated demand serviced by vehicle c when arriving at node i

#Objective
minimize max_distance: max{c in COURIERS} sum{i in V, j in V} D[i,j]*x[i,j,c];

#bound on the obejective functions
subject to ObjUpBound: max{c in COURIERS} sum{i in V, j in V} D[i,j]*x[i,j,c] <= UpBound;
subject to ObjLoBound: max{c in COURIERS} sum{i in V, j in V} D[i,j]*x[i,j,c] >= LoBound;
#constraints

#every location must be visited exactly once
#subject to VisitedOnce_row {i in ITEMS}: sum {j in V, c in COURIERS} x[i, j, c] = 1;
#subject to VisitedOnce_columns {i in ITEMS}: sum {j in V, c in COURIERS} x[j, i, c] = 1; #useless since we add x[i, j, c] = x[j, i, c]

#A customer is visited by exactly one vehicle
subject to Customer_once {i in ITEMS}: sum {c in COURIERS} y[i, c] = 1; #ok

#every courier leave the depot
#subject to All_depart: sum {c in COURIERS} y[0, c] = m;

#load carried lower than the capacity of the courier
subject to load_carried {c in COURIERS}: sum {i in ITEMS} y[i, c]*s[i] <= l[c]; #ok

#cannot move from one position to itself
subject to pos_itself {c in COURIERS, i in V}: x[i, i, c] = 0; #ok

#every courier must end and start at the depot
subject to end_depot {c in COURIERS}: sum {i in V} x[i, n+1, c] = 1; #ok
subject to start_depot {c in COURIERS}: sum {i in V} x[n+1, i, c] = 1; #ok

#Path-flow
subject to Path_flow {j in ITEMS, c in COURIERS}: sum {i in V} x[i, j, c] = sum {i in V} x[j, i, c]; #ok

#subject to Path_flow1 {c in COURIERS, i in ITEMS}: sum {j in V} x[n+1, j, c] - sum {j in V} x[j, n+1, c] = 1;

#Coupling
subject to Coupling {i in ITEMS, c in COURIERS}: sum {j in V} x[i,j,c] = y[i,c]; #ok

#subject to Coupling0 {c in COURIERS}: sum {j in V} x[j,0,c] = y[0,c];
subject to Coupling2 {j in ITEMS, c in COURIERS}: sum {i in V} x[i,j,c] = y[j,c]; #ok

#Miller, Tucker and Zemlin constraint
subject to MTZ {c in COURIERS, i in ITEMS, j in V: i != j}: u[i, c] - u[j, c] + 1 <= (n)*(1- x[i, j, c]);

subject to MTZ2 {c in COURIERS, i in ITEMS}: u[i, c] <= x[n+1, i, c] + (n+1)*(1-x[n+1, i, c]);

subject to MTZ3 {c in COURIERS, i in ITEMS, j in V: i!=j}: u[j, c] >= (u[i, c] +1)*x[i, j, c];