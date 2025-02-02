# CDMO_MCCVRP

This repository contains the code and the project report for the **Multi Courier Capacitated Vehicle Routing Problem** (MCCVRP) repository for the **CDMO-2024 exam**.

## Usage

To reproduce our results, please ensure Docker is installed on your system. Once Docker is installed, to run the docker the following scripts should be executed from the terminal while in the Dockerfile directory:

- To build the docker
```
docker build -t <docker_name> .
```
- To run the docker
```
docker run -t <docker_name> [--instances <instance(s)_name> --approach <approach> --solver_name <solver_name> --model_name <model_name> --timeout <timeout>]
```

### Usage rules
 * All the parameters are optional, if you would like to run everything you simply non specify nothing. 
 * You can specify more than one instance, separated by a comma without space. The instances names are those in the instance directory, without .dat -> inst01,inst02,inst10 or simply inst07
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
    - **SMT**: `base`, `symm` . `symm` only available for `z3_py` solver. 
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
docker run -t <docker_name>
```

Run a specific instance settings with a specfic approach, solver, base and timeout:
```
docker run -t <docker_name> --instances inst01 --approach MIP --solver_name gurobi --model_name base --timeout 300
```

## Authors

- Francesco Baiocchi
- Christian Di Buò
- Simone Reale
