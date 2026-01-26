# EFC Core Layer  
### Foundations of the Computational Model

The core layer implements the fundamental components of EFC.  
Its purpose is to provide stable, minimal, and reusable abstractions for:

- model parameters  
- thermodynamic fields  
- energy-flow computation  
- entropy gradients  
- rotation velocity profiles  
- full state evaluation

## Components

### 1. `EFCParameters`
A structured parameter set containing:
- entropy scale  
- length scale  
- flow constant  
- velocity scale  
- grid resolution  
- timestep count  
- random seed  

### 2. `EFCModel`
The main model class providing:
- energy-flow potential  
- entropy gradient  
- rotation velocity  
- combined state output  

### 3. Parameter loading
`load_parameters(path)` constructs an `EFCParameters` object from a JSON file.

## Role in the Architecture
The core layer is referenced by:
- entropy module  
- potential module  
- validation utilities  
- simulators  
- notebooks and analysis scripts  

It provides the stable base shared across all higher layers.
