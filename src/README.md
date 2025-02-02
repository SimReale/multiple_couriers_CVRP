# CDMO_MCCVRP

This repository contains the code and the project report for the **Multi Courier Capacitated Vehicle Routing Problem** (MCCVRP) repository for the **CDMO-2024 exam**.

## Usage

To reproduce our results, please ensure Docker is installed on your system. Once Docker is installed, you can solve the different instances by running the following bash script in your terminal:

```{bash}
$ ./run_docker.sh <docker_name> --instances <instance(s)_name> --approach <approach> --solver_name <solver_name> --model_name <model_name> --timeout <timeout>
```

### Usage rules
 * All the parameters are optional, if you would like to run everything you simply non specify nothing. 
 * If you specify the model_name or the solver_name you have to specify also the approach, otherwise a parse error will be raised.
 * If you specify the model_name then the solver_name must be specified, otherwise a parse error will be raised.
### Flags value

* `<instances>`: name of one or more instances, seprated by a comma, contained in the instances directory. You can choose either to run one instance -> inst01, or more than one inst01,inst10
* `<approach>`: approach to use (`CP`, `SAT`, `SMT`, `MIP`).
* `<solver_name>`: Solver to employ (depends on the chosen method):
    - **CP**: `gecode`, `chuffed`
    - **SAT**: `z3`
    - **SMT**: `z3_py`, `z3`, `cvc4`, `cvc5`
    - **MIP**: `highs`, `scip`, `gurobi`
* `<model_name>`: Formulation to use (depends on the chosen method):
    - **CP**: `base`, `implied`, `symm`. Only with gecode as solver `implied_lns`
    - **SAT**: `base`
    - **SMT**: `base`, `symm` . `Symm` only available for `z3_py` solver. 
    - **MIP**: `base`, `implied`, `impl_SB`

* `<time>`: Maximum time in seconds allowed for the solver to run.

> [!IMPORTANT]
> To use MIP, you need to obtain an AMPL license. After acquiring your license, modify the corresponding line in the Dockerfile accordingly.

```{dockerfile}
AMPL_LICENSE="your_license"
```

### Example Usage:
Run everything:
```
$ ./run_docker.sh <docker_name> 
```

Run a specific instance settings with a specfic approach, solver, base and timeout:
```{bash}
$ ./run_docker.sh <docker_name> --instances inst01 --approach MIP --solver_name gurobi --model_name base --timeout 300
```

## Authors

- Francesco Baiocchi
- Christian Di Buò
- Simone Reale
