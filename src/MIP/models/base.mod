#parameters
param m >=0;
param n >=0;

#set
set COURIERS := {1..m};
set ITEMS := {1..n};
set V := {1..n+1}; #n+1 is the depot

#additional parameters
param l{COURIERS} integer; #array of capacity of each couriers
param s{ITEMS} integer; #array of size of each packs
param D{i in V, j in V} integer; #matrix of D

#variables
var x {V, V, COURIERS} binary; #xijc = 1 iﬀ vehicle c moves from node i to j; 0 otherwise
var y {ITEMS, COURIERS} binary; #yic = 1 iﬀ vehicle c visits node i ; 0 otherwise
var u {ITEMS, COURIERS} >= 1 <= n; #uic is the cumulated demand serviced by vehicle c when arriving at node i

#Upper and Lower Bound variables and constraints
var UpBound{i in V};  
var LoBound;

subject to MaxUp_def{i in V, j in V}: UpBound[i] >= D[i, j];  
subject to MaxLo_def{i in ITEMS}: LoBound >= D[n+1, i] + D[i, n+1];

#Objective variable and relative constraints
var max_distance;

subject to ObjLowerBound: max_distance >= LoBound;
subject to ObjUpperBound: max_distance <= sum{i in V} UpBound[i]; 

subject to objective_function {c in COURIERS}: sum{i in V, j in V} D[i,j]*x[i,j,c] <= max_distance;

minimize max_distance_obj: max_distance;

################### constraints ###################

#A customer is visited by exactly one vehicle
subject to Customer_once {i in ITEMS}: sum {c in COURIERS} y[i, c] = 1;

#load carried lower than the capacity of the courier
subject to Load_carried {c in COURIERS}: sum {i in ITEMS} y[i, c]*s[i] <= l[c];

#cannot move from one position to itself
subject to Pos_itself {c in COURIERS, i in V}: x[i, i, c] = 0;

#every courier must end and start at the depot
subject to Start_depot {c in COURIERS}: sum {i in V} x[n+1, i, c] = 1;

#Path-flow
subject to Path_flow {j in ITEMS, c in COURIERS}: sum {i in V} x[i, j, c] = sum {i in V} x[j, i, c];

#Coupling (or Channelling)
subject to Coupling {i in ITEMS, c in COURIERS}: sum {j in V} x[i,j,c] = y[i,c];

#Miller, Tucker and Zemlin constraint
subject to MTZ {c in COURIERS, i in ITEMS, j in ITEMS: i != j}: u[i, c] - u[j, c] + 1 <= n *(1- x[i, j, c]);