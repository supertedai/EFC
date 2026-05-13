# PyPhi: A toolbox for integrated information theory

**Authors:** William G. P. Mayner, William Marshall, Larissa Albantakis, Graham Findlay, Robert Marchman, Giulio Tononi
**Journal:** PLoS Computational Biology, 2018
**DOI:** 10.1371/journal.pcbi.1006343
**PMC:** PMC6080800 · **PMID:** 30048445
**License:** Creative Commons Attribution License (PLoS open access)
**Source:** PubMed Central (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6080800/)
**Retrieved:** 2026-05-13

---

## Abstract

Integrated information theory provides a mathematical framework to fully characterize the cause-effect structure of a physical system. Here, we introduce, a Python software package that implements this framework for causal analysis and unfolds the full cause-effect structure of discrete dynamical systems of binary elements. The software allows users to easily study these structures, serves as an up-to-date reference implementation of the formalisms of integrated information theory, and has been applied in research on complexity, emergence, and certain biological questions. We first provide an overview of the main algorithm and demonstrate PyPhi’s functionality in the course of analyzing an example system, and then describe details of the algorithm’s design and implementation. PyPhi can be installed with Python’s package manager via the command ‘’ on Linux and macOS systems equipped with Python 3.4 or higher. PyPhi is open-source and licensed under the GPLv3; the source code is hosted on GitHub at. Comprehensive and continually-updated documentation is available at. Themailing list can be joined at. A web-based graphical interface to the software is available at.

This is aSoftware paper.

## Introduction

Integrated information theory (IIT) has been proposed as a theory of consciousness. The central hypothesis is that a physical system has to meet five requirements (‘postulates’) in order to be a physical substrate of subjective experience: (1)(the system must be able to make a difference to itself); (2)(it must be composed of parts that have causal power within the whole); (3)(its causal power must be specific); (4)(its causal power must not be reducible to that of its parts); and (5)(it must be maximally irreducible) [–].

From these postulates, IIT develops a mathematical framework to assess the cause-effect structure (CES) of a physical system that is applicable to discrete dynamical systems. This framework has proven useful not only for the study of consciousness but has also been applied in research on complexity [–], emergence [–], and certain biological questions [].

The main measure of cause-effect power,(denoted Φ), quantifies how irreducible a system’s CES is to those of its parts. Φ also serves as a general measure of complexity that captures to what extent a system is both integrated [] and differentiated (informative) [].

Here we describe, a Python software package that implements IIT’s framework for causal analysis and unfolds the full CES of discrete Markovian dynamical systems of binary elements. The software allows users to easily study these CESs and serves as an up-to-date reference implementation of the formalisms of IIT.

Details of the mathematical framework are published elsewhere [,]; in § Results we describe the output and input of the software and give an overview of the main algorithm in the course of reproducing results obtained from an example system studied in []. In § Design and implementation we discuss specific issues concerning the algorithm’s implementation. Finally in § Availability and future directions we describe how the software can be obtained and discuss new functionality planned for future versions.

## Results

## Output

The software has two primary functions: (1) to unfold the full CES of a discrete dynamical system of interacting elements and compute its Φ value, and (2) to compute the maximally-irreducible cause-effect repertoires of a particular set of elements within the system. The first is function is implemented by, which returns aobject (). The system’s CES is contained in the ‘’ attribute and its Φ value is contained in ‘’. Other attributes are detailed in the.

The CES is composed ofobjects, which are the output of the second main function:(). Eachis specified by a set of elements within the system (contained in its ‘’ attribute). Acontains a maximally-irreducible cause and effect repertoire (‘’ and ‘’), which are probability distributions that capture how the mechanism elements in their current state constrain the previous and next state of the system, respectively; avalue (‘’), which measures the irreducibility of the repertoires; and several other attributes discussed below and detailed in the.

## 10.1371/journal.pcbi.1006343.g001

## Fig 1

Output.

Theobject is the main output of the software. It represents the results of the analysis of the system in question. It has several attributes (grey boxes): ‘’ is aobject containing all of the system’s; ‘’ is aobject that represents the minimum-information partition (MIP) of the system (the partition of the system that makes the least difference to its CES); ‘’ is theofspecified by the system after applying the MIP; and ‘’ is the Φ value, which measures the difference between the unpartitioned and partitioned CES.Arepresents the maximally-irreducible cause (MIC) and maximally-irreducible effect (MIE) of a mechanism in a state. The ‘’ attribute contains the indices of the mechanism elements. The ‘’ and ‘’ attributes containandobjects that describe the mechanism’s MIC and MIE, respectively; each of these contains a purview, repertoire, MIP, partitioned repertoire, andvalue. The ‘’ attribute contains the concept’svalue, which is the minimum of thevalues of the MIC and MIE.

## Input

The starting point for the IIT analysis is a discrete Markovian dynamical systemcomposed ofinteracting elements. Such a system can be represented by a directed graph of interconnected nodes, each equipped with a function that outputs the node’s state at the next timestep+ 1 given the state of its parents at the previous timestep(). At present, PyPhi can analyze both deterministic and stochastic discrete Markovian dynamical systems consisting of elements with two states.

Such a discrete dynamical system is completely specified by its transition probability matrix (TPM), which contains the probabilities of all state transitions fromto+ 1. It can be obtained from the graphical representation of the system by perturbing the system into each of its possible states and observing the following state at the next timestep (for stochastic systems, repeated trials of perturbation/observation will yield the probabilities of each state transition). In PyPhi, the TPM is the fundamental representation of the system.

Formally, if we letbe the random variable of the system state at, the TPM specifies the conditional probability distribution over the next stategiven each current state:where Ωdenotes the set of possible states. Furthermore, given a marginal distribution over the previous states of the system, the TPM fully specifies the joint distribution over state transitions. Here IIT imposes uniformity on the marginal distribution of the previous states because the aim of the analysis is to capture direct causal relationships across a single timestep without confounding factors, such as influences from system states before− 1 [,,,,]. The marginal distribution thus corresponds to an interventional (causal), not observed, state distribution.

Moreover, IIT assumes that there is no instantaneous causation; that is, it is assumed that the elements of the dynamical system influence one another only from one timestep to the next. Therefore we require that the system satisfies the following Markov condition, called the: each element’s state at+ 1 must be independent of the state of the others, given the state of the system at[],For systems of binary elements, a TPM that satisfiescan be represented in state-by-node form (, right), since we need only store each element’s marginal distribution rather than the full joint distribution.

In PyPhi, the system under analysis is represented by aobject. Ais created by passing its TPM as the first argument:(see § Setup). Optionally, a connectivity matrix (CM) can also be provided, wherevia thekeyword argument:. Because the TPM completely specifies the system, providing a CM is not necessary; however, explicit connectivity information can be used to make computations more efficient, especially for sparse networks, because PyPhi can rule out certain causal influencesif there are missing connections (see § Connectivity optimizations). Note that this means providing an incorrect CM can result in inaccurate output. If no CM is given, PyPhi assumes full connectivity;., it assumes each element may have an effect on any other, which guarantees correct results.

Once theis created, a subset of elements within the system (called a), together with a particular system state, can be selected for analysis by creating aobject. Hereafter we refer to a candidate system as a.

## 10.1371/journal.pcbi.1006343.g002

## Fig 2

A network of nodes and its TPM.

Each node has its own TPM—in this case, the truth-table of a deterministic logic gate. Yellow signifies the “ON” state; white signifies “OFF”. The system’s TPM (right) is composed of the TPMs of its nodes (left), here shown in state-by-node form (see § Representation of the TPM and probability distributions). Note that in PyPhi’s TPM representation, the first node’s state varies the fastest, according to the little-endian convention (see § 2-dimensional state-by-node form).

## Demonstration

The mathematical framework of IIT is typically formulated using graphical causal models as representations of physical systems of elements. The framework builds on the causal calculus of the(⋅) operator introduced by Pearl []. In order to assess causal relationships among the elements, interventions (manipulations, perturbations) are used to actively set elements into a specific state, after which the resulting state transition is observed.

For reference, we define a set of graphical operations that are used during the IIT analysis. Toan element is to use system interventions to keep it in the same state for every observation. Toan element is to use system interventions to set it into a state chosen uniformly at random. Finally, toa connection from a source element to a target element is to make the source appear noised to the target, while the remaining, uncut connections from the source still correctly transmit its state.

In this section we demonstrate some of the capabilities of the software by unfolding the CES of a small deterministic system of logic gates as described in [] while describing how the algorithm is implemented in terms of TPM manipulations, which we link to the graphical operations defined above. A schematic of the algorithm is shown in Figsand, and a more detailed illustration is given in.

## 10.1371/journal.pcbi.1006343.g003

## Fig 3

Algorithm schematic at the mechanism level.

PyPhi functions are named in boxes, with arguments in grey. Arrows point from callee to caller. Functions are organized by the postulate they correspond to (left). ⊗ denotes the tensor product;denotes the power set.

## 10.1371/journal.pcbi.1006343.g004

## Fig 4

Algorithm schematic at the system level.

PyPhi functions are named in boxes, with arguments in grey. Arrows point from callee to caller. Functions are organized by the postulate they correspond to (left).denotes the power set.

## Setup

The first step is to create theobject. Here we choose to provide the TPM in 2-dimensional state-by-node form (see § 2-dimensional state-by-node form). The TPM is the only required argument, but we provide the CM as well, since we know that there are no self-loops in the system and PyPhi will use this information to speed up the computation. We also label the nodes,, andto make the output easier to read.

We select a subsystem and a system state for analysis by creating aobject. System states are represented by tuples ofs ands, withmeaning “ON” andmeaning “OFF.” In this case we will analyze the entire system, so the subsystem will contain all three nodes. The nodes to include can be specified with either their labels or their indices (note that in other PyPhi functions, nodes must be specified with their indices).

If there are nodes outside the subsystem, they are considered asfor the causal analysis []. In the graphical representation of the system, the background conditions arein their current state while the subsystem is perturbed and observed in order to derive its TPM. In the TPM representation, the equivalent operation is performed bythe system TPM on the state atof the nodes outside the subsystem and thenthose nodes at+ 1 (illustrated in). In PyPhi, this is done when the subsystem is created; the subsystem TPM can be accessed with theattribute,..

## Cause/Effect repertoires (mechanism-level information)

The lowest-level objects in the CES of a system are theandof a set of nodes within the subsystem, called a, over another set of nodes within the subsystem, called aof the mechanism. The cause (effect) repertoire is a probability distribution that captures the information specified by the mechanism about the purview by describing how the previous (next) state of the purview is constrained by the current state of the mechanism.

In terms of graphical operations, the effect repertoire is obtained by (1)the mechanism nodes in their state at; (2)the non-mechanism nodes at time, so as to remove their causal influence on the purview; and (3) observing the resulting state transition fromto+ 1 while ignoring the state at+ 1 of non-purview nodes, in order to derive a distribution over purview states at+ 1.

The cause repertoire is obtained similarly, but in that case, the purview nodes at time− 1 are noised, and the resulting state transition from− 1 tois observed while ignoring the state of non-mechanism nodes. Bayes’ rule is then applied, resulting in a distribution over purview states at− 1. The corresponding operations on the TPM are detailed in § Calculation of cause/effect repertoires from the TPM and illustrated in.

Note that, operationally, we enforce that each input from a noised node conveysnoise during the perturbation/observation step. In this way, we avoid counting correlations from outside the mechanism-purview pair as constraints due to the current state of the mechanism. Graphically, this process would correspond to replacing each noised node that is a parent of multiple purview nodes (for the effect repertoire) or mechanism nodes (for the cause repertoire) with multiple, independent “virtual nodes” (as in [, Supplementary Methods]). However, the equivalent definition of repertoires in Eqs () and () obviates the need to actually implement virtual nodes in PyPhi.

With themethod of the, we can obtain the cause repertoire of, for example, mechanismover the purviewdepicted in Fig. 4 of []:

We see that mechanismin its current state, ON (), specifies information by ruling out the previous states in whichandare OFF (). That is, the probability that eitherorwas the previous state, given thatis currently ON, is zero:

Note that repertoires are returned in multidimensional form, so they can be indexed with state tuples as above. Repertoires can be reshaped to be 1-dimensional if needed,. for plotting, but care must be taken that NumPy’s FORTRAN (column-major) ordering is used so that PyPhi’s little-endian convention for indexing states is respected (see § 2-dimensional state-by-node form). PyPhi provides thefunction for this:

## Minimum-information partitions (mechanism-level integration)

Having assessed the information of a mechanism over a purview, the next step is to assess its(denoted) by quantifying the extent to which the cause and effect repertoires of the mechanism-purview pair cannot be reduced to the repertoires of its parts.

In terms of graphical operations, the irreducibility of a mechanism-purview pair is tested by partitioning it into parts andthe connections between them. By applying the perturbation/observation procedure after cutting the connections we obtain a. Since the partition renders the parts independent, in terms of TPM manipulations, the partitioned repertoire can be calculated as the product of the individual repertoires for each of the parts. If the partitioned repertoire is no different than the original unpartitioned repertoire, then the mechanism as a whole did not specify integrated information about the purview. By contrast, if a repertoire cannot be factored in this way, then some of its selectivity is due to the causal influence of the mechanismon the purview, and the repertoire is said to be.

The amount of irreducibility of a mechanism over a purview with respect to a partition is quantified as the distance between the unpartitioned repertoire and the partitioned repertoire (calculated with). There are many ways to divide the mechanism and purview into parts, so the irreducibility is measured for every partition and the partition that yields the minimum irreducibility is called the(MIP). The integrated information () of a mechanism-purview pair is the distance between the unpartitioned repertoire and the partitioned repertoire associated with the MIP. PyPhi supports several distance measures and partitioning schemes (see § Configuration).

The MIP search procedure is implemented by theandmethods. Each returns aobject that contains the MIP, as well as thevalue, mechanism, purview, temporal direction (cause or effect), unpartitioned repertoire, and partitioned repertoire. For example, we compute the effect MIP of mechanismover purviewfrom Fig. 6 of [] as follows:

Here we can see that the MIP attempts to factor the repertoire ofoverinto the product of the repertoire ofoverand the repertoire of the empty mechanism ∅ over. However, the repertoire cannot be factored in this way without information loss; the distance between the unpartitioned and partitioned repertoire is nonzero (). Thus mechanismover the purviewis irreducible.

## Maximally-irreducible cause-effect repertoires (mechanism-level exclusion)

Next, we apply IIT’s postulate of exclusion at the mechanism level by finding the(MIC) and(MIE) specified by a mechanism. This is done by searching over all possible purviews for theobject with the maximalvalue. Theandmethods implement this search procedure; they return aand aobject, respectively. The MIC of mechanism, for example, is the purview(Fig. 8 of []). This is computed like so:

## Concepts

If the mechanism’s MIC has> 0 and its MIE has> 0, then the mechanism is said to specify a. Thevalue of the concept as a whole is the minimum ofand.

We can compute the concept depicted in Fig. 9 of [] using themethod, which takes aand returns aobject containing thevalue, the MIC (in the ‘’ attribute), and the MIE (in the ‘’ attribute):

Note that in PyPhi, the repertoires are distributions over purview states, rather than system states. Occasionally it is more convenient to represent repertoires as distributions over the entire system. This can be done with theandmethods of theobject, which assume the unconstrained (maximum-entropy) distribution over the states of non-purview nodes:

Also note thatwill return aobject when= 0 even though these are not concepts, strictly speaking. For convenience,evaluates toif> 0 andotherwise.

## Cause-effect structures (system-level information)

The next step is to compute the CES, the set of all concepts specified by the subsystem. The CES characterizes all of the causal constraints that are intrinsic to a physical system. This is implemented by thefunction, which simply callsfor every mechanism, whereis the power set of subsystem nodes. It returns aobject containing thosefor which> 0.

We see that every mechanism inexcept forspecifies a concept, as described in Fig. 10 of []:

## Irreducible cause-effect structures (system-level integration)

At this point, the irreducibility of the subsystem’s CES is evaluated by applying the integration postulate at the system level. As with integration at the mechanism level, the idea is to measure the difference made by each partition and then take the minimal value as the irreducibility of the subsystem.

We begin by performing a. Graphically, the subsystem is partitioned into two parts and the edges going from one part to the other are, rendering them causally ineffective. This is implemented as an operation on the TPM as follows: Letdenote the set of directed edges in the subsystem that are to be cut, where each edge∈has a source nodeand a target node. For each edge, we modify the individual TPM of node() by marginalizing over the states ofat. The resulting TPM specifies the function implemented bywith the causal influence ofremoved. We then combine the modified node TPMs to recover the full TPM of the partitioned subsystem. Finally, we recalculate the CES of the subsystem with this modified TPM (the).

The irreducibility of a CES with respect to a partition is the distance between the unpartitioned and partitioned CESs (calculated with; several distances are supported; see § Configuration). This distance is evaluated for every partition, and the minimum value across all partitions is the subsystem’s integrated information Φ, which measures the extent to which the CES specified by the subsystem is irreducible to the CES under the minimal partition.

This procedure is implemented by thefunction, which returns aobject (). We can verify that the Φ value of the example system in [] is 1.92 and the minimal partition is that which removes the causal connections fromto:

## Complexes (system-level exclusion)

The final step in unfolding the CES of the system is to apply the postulate of exclusion at the system level. We compute the CES of each subset of the network, considered as a subsystem (that is,the external nodes as background conditions), and find the CES with maximal Φ, called the(MICS) of the system. The subsystem giving rise to it is called the; any overlapping subsets with lower Φ are excluded. Non-overlapping subsets may be further analyzed to find additional complexes within the system.

In this example, we find that the whole systemis the system’s major complex, and all proper subsets are excluded:

Note that sinceis a function of the, rather than a particular, it is necessary to specify the state in which the system should be analyzed.

## Design and implementation

PyPhi was designed to be easy to use in interactive, exploratory research settings while nonetheless remaining suitable for use in large-scale simulations or as a component in larger applications. It was also designed to be efficient, given the high computational complexity of the algorithms in IIT. Here we describe some implementation details and optimizations used in the software.

## Representation of the TPM and probability distributions

PyPhi supports three different TPM representations: 2-,, and. The state-by-node form is the canonical representation in PyPhi, with the 2-dimensional form used for input and visualization and the multidimensional form used for internal computation. The state-by-state representation is given as an input option for those accustomed to this more general form. If the TPM is given in state-by-state form, PyPhi will raise an error if it does not satisfy(conditional independence).

## 2-dimensional state-by-node form

A TPM in state-by-node form is a matrix where the entry (,) gives the probability that thenode will be ON at+ 1 if the system is in thestate at. This representation has the advantage of being more compact than the state-by-state form, with 2×entries instead of 2× 2, whereis the number of nodes. Note that the TPM admits this representation because in PyPhi the nodes are binary; both Pr(= ON) and Pr(= OFF) can be specified by a single entry, in our case Pr(= ON), since the two probabilities must sum to 1.

Because the possible system states atare represented implicitly as row indices in 2-dimensional TPMs, there must be an implicit mapping from states to indices. In PyPhi this mapping is achieved by listing the state tuples in lexicographical order and then interpreting them as binary numbers where the state of the first node corresponds to the least-significant bit, so that. the stateis mapped to the row with index 8 (the ninth row, since Python uses zero-based indexing []). Designating the first node’s state as the least-significant bit is analogous to choosing the little-endian convention in organizing computer memory. This convention is preferable because the mapping is stable under the inclusion of new nodes: including another node in a subsystem only requires concatenating new rows and a new column to its TPM rather than interleaving them. Note that this is opposite convention to that used in writing numbers in positional notation; care must be taken when converting between states and indices and between different TPM representations (themodule provides convenience functions for these purposes).

## Multidimensional state-by-node form

When a state-by-state TPM is provided to PyPhi by the user, it is converted to state-by-node form and the conditional independence property () is checked. Note that any TPM in state-by-node form necessarily satisfies. For internal computations, the TPM is then reshaped so that it has+ 1 dimensions rather than two: the firstdimensions correspond to the states of each of thenodes at, while the last dimension corresponds to the probabilities of each node being ON at+ 1. In other words, the indices of the rows (current states) in the 2-dimensional TPM are “unraveled” intodimensions, with thedimension indexed by thebit of the 2-dimensional row index according to the little-endian convention. Because the TPM is stored in a NumPy array, this multidimensional form allows us to take advantage of NumPy indexing [] and use a state tuple as an index directly, without converting it to an integer index:

The first entry of this array signifies that if the state of the system isat, then the probability of the first nodebeing ON at+ 1 is Pr(= ON) = 1. Similarly, the second entry means Pr(= ON) = 0.25 and the third entry means Pr(= ON) = 0.75.

Most importantly, the multidimensional representation simplifies the calculation of marginal and conditional distributions and cause/effect repertoires, because it allows efficient “broadcasting” [] of probabilities when multiplying distributions. Specifically, the Python multiplication operator ‘’ acts as the tensor product when the operands are NumPy arraysandof equal dimensionality such that for each dimension, eitheror.

## Calculation of cause/effect repertoires from the TPM

The cause and effect repertoires of a mechanism over a purview describe how the mechanism nodes in a particular state atconstrain the possible states of the purview nodes at− 1 and+ 1, respectively. Here we describe how they are derived from the TPM in PyPhi.

## The effect repertoire

We begin with the simplest case: calculating the effect repertoire of a mechanism⊆over a purview consisting of a single element∈. This is defined as a conditional probability distribution over states of the purview element at+ 1 given the current state of the mechanism,It is derived from the TPM by conditioning on the state of the mechanism elements, marginalizing over the states of non-purview elements′ =\(these states correspond to columns in the state-by-state TPM), and marginalizing over the states of non-mechanism elements′ =\(these correspond to rows):

This operation is implemented in PyPhi by several subroutines. First, in a pre-processing step performed when theobject is created, aobject is created for each element in the subsystem. Eachcontains its own individual TPM, extracted from the subsystem’s TPM; this is a 2× 2 matrix whereis the number of the node’s parents and the entry (,) gives the probability that the node is in state(or) at+ 1 given that its parents are in stateat. This node TPM is represented internally in multidimensional state-by-node form as usual, with singleton dimensions for those subsystem elements that are not parents of the node. The effect repertoire is then calculated by conditioning the purview node’s TPM on the state of the mechanism nodes that are also parents of the purview node, via thefunction, and marginalizing out non-mechanism nodes, with.

In cases where there are mechanism nodes that are not parents of the purview node, the resulting array is multiplied by an array of ones that has the desired shape (dimensions of size two for each mechanism node, and singleton dimensions for each non-mechanism node). Because of NumPy’s broadcasting feature, this step is equivalent to taking the tensor product of the array with the maximum-entropy distribution over mechanism nodes that are not parents, so that the final result is a distribution over all mechanism nodes, as desired.

The effect repertoire over a purview of more than one element is given by the tensor product of the effect repertories over each individual purview element,Again, because PyPhi TPMs and repertoires are represented as tensors (multidimensional arrays), with each dimension corresponding to a node, the NumPy multiplication operator between distributions over different nodes is equivalent to the tensor product. Thus the effect repertoire over an arbitrary purview is trivially implemented by taking the product of the effect repertoires over each purview node with.

## The cause repertoire

The cause repertoire of a single-element mechanism∈over a purview⊆is defined as a conditional probability distribution over the states of the purview at− 1 given the current state of the mechanism,As with the effect repertoire, it is obtained by conditioning and marginalizing the TPM. However, because the TPM gives conditional probabilities of states at+ 1 given the state at, Bayes’ rule is first applied to express the cause repertoire in terms of a conditional distribution over states at− 1 given the state at,where the marginal distribution Pr() over previous states is the uniform distribution. In this way, the analysis captures how a mechanism in a state constrains a purview without being biased by whether certain states arise more frequently than others in the dynamical evolution of the system [,,,]. Then the cause repertoire can be calculated by marginalizing over the states of non-mechanism elements′ =\(now corresponding to columns in the state-by-state TPM) and non-purview elements′ =\(now corresponding to rows),

In PyPhi, the “backward” conditional probabilities Pr(|) for a single mechanism node are obtained by indexing into the last dimension of the node’s TPM with the stateand then marginalizing out non-purview nodes via. As with the effect repertoire, the resulting array is then multiplied by an array of ones with the desired shape in order to obtain a distribution over the entire purview. Finally, because in this case the probabilities were obtained from columns of the TPM, which do not necessarily sum to 1, the distribution is normalized with.

The cause repertoire of a mechanism with multiple elements is the normalized tensor product of the cause repertoires of each individual mechanism element,whereis a normalization factor that ensures that the distribution sums to 1. This is implemented in PyPhi viaand. For a more complete illustration of these procedures, see.

## Code organization and interface design

The postulates of IIT induce a natural hierarchy of computations [, Supplementary Information S2], and PyPhi’s implementation mirrors this hierarchy by using object-oriented programming () and factoring the computations into compositions of separate functions where possible. One advantage of this approach is that each level of the computation can be performed independently of the higher levels; for example, if one were interested only in the MIE of certain mechanisms rather than the full MICS, then one could simply callon those mechanisms instead of callingand extracting them from the resultingobject (this is especially important in the case of large systems where the full calculation is infeasible). Separating the calculation into many subroutines and exposing them to the user also has the advantage that they can be easily composed to implement functionality that is not already built-in.

## 10.1371/journal.pcbi.1006343.t001

## Table 1

Correspondence between theoretical objects and PyPhi objects.

## Theoretical object

## PyPhi object

## Discrete dynamical system

## Network

## Candidate system

## Subsystem

## System element

## in

## System state

## Pythoncontaining aorfor each node

## Mechanism

## Pythonof node indices

## Purview

## Pythonof node indices

## Repertoire over a purview

## NumPy array with || dimensions, each of size 2

## MIP

## Theattribute of thereturned byor

## MIC and MIE

## and

## Concept

## Concept

## φ

## Theattribute of a

## CES

## CauseEffectStructure

## Φ

## Theattribute of a

## MICS

## Theattribute of thereturned by

## Complex

## Theattribute of thereturned by

## Configuration

Many aspects of PyPhi’s behavior may be configured via theobject. The configuration can be specified in a YAML file []; anis available in the GitHub repository. When PyPhi is imported, it checks the current directory for a file namedand automatically loads it if it exists. Configuration settings can also be loaded on the fly from an arbitrary file with thefunction.

Alternatively,can load configuration settings from a Python dictionary. Many settings can also be changed by directly assigning them a new value.

Default settings are used if no configuration is provided. A full description of the available settings and their default values is available in the.

## Optimizations and approximations

Here we describe various optimizations and approximations used by the software to reduce the complexity of the calculations (see § Limitations). Memoization and caching optimizations are described in.

## Connectivity optimizations

As mentioned in § Input, providing connectivity information explicitly with a CM can greatly reduce the time complexity of the computations, because in certain cases missing connections imply reducibility.

For example, at the system level, if the subsystem is not strongly connected then Φ is necessarily zero. This is because a unidirectional cut between one system part and the rest can always be found that will not actually remove any edges, so the CESs with and without the cut will be identical (seefor proof). Accordingly, PyPhi immediately excludes these subsystems when finding the major complex of a system.

Similarly, at the mechanism level, PyPhi uses the CM to exclude certain purviews from consideration when computing a MIC or MIE by efficiently determining that repertoires over those purviews are reducible without needing to explicitly compute them. Suppose there are two sets of nodesandfor which there exist partitions= (,) and= (,) such that there are no edges fromtoand no edges fromto. Then the effect repertoire of mechanismover purviewcan be factored asand the cause repertoire of mechanismover purviewcan be factored asThus in these cases the mechanism is reducible for that purview and= 0 (seefor proof).

## Analytical solution to the earth mover’s distance

One of the repertoire distances available in PyPhi is the earth mover’s distance (EMD), with the Hamming distance as the ground metric. Computing the EMD between repertoires is a costly operation, with time complexity(2) whereis the number of nodes in the purview []. However, when comparing effect repertoires, PyPhi exploits a theorem that states that the EMD between two distributionsandover multiple nodes is the sum of the EMDs between the marginal distributions over each individual node, ifandare independent. This analytical solution has time complexity(), a significant improvement over the general EMD algorithm (note that this estimate does not include the cost of computing the marginals, which already have been computed to obtain the repertoires). By the conditional independence property (), the conditions of the theorem hold for EMD calculations between effect repertoires, and thus the analytical solution can be used for half of all repertoire calculations performed in the analysis. The theorem is formally stated and proved in.

## Approximations

Currently, two approximate methods of computing Φ are available. These can be used via settings in the PyPhi configuration file (they are disabled by default):

In both cases, the complexity of the calculation is greatly reduced by replacing the optimal partitioned CES by an approximate solution. The system’s Φ value is then computed as usual as the difference between the unpartitioned CES and the approximate partitioned CES.

## (the “cut one” approximation), and

(the “no new concepts” approximation).

## Cut one

The “cut one” approximation reduces the scope of the search for the MIP over possible system cuts. Instead of evaluating the partitioned CES for each of the 2unidirectional bipartitions of the system, only those 2bipartitions are evaluated that sever the edges from a single node to the rest of the network or vice versa. Since the goal is to find the minimal Φ value across all possible partitions, the “cut one” approximation provides an upper bound on the exact Φ value of the system.

## No new concepts

For most choices of mechanism partitioning schemes and distance measures, it is possible that the CES of the partitioned system contains concepts that are reducible in the unpartitioned system and thus not part of the unpartitioned CES. For this reason, PyPhi by default computes the partitioned CES from scratch from the partitioned TPM. Under the “no new concepts” approximation, such new concepts are ignored. Instead of repeating the entire CES computation for each system partition, which requires reevaluating all possible candidate mechanisms for irreducibility, only those mechanisms are taken into account that already specify concepts in the unpartitioned CES. In many types of systems, new concepts due to the partition are rare. Approximations using the “no new concepts” option are thus often accurate. Note, however, that this approximation provides neither a theoretical upper nor lower bound on the exact Φ value of the system.

## Limitations

PyPhi’s main limitation is that the algorithm is exponential time in the number of nodes,(53). This is because the number of states, subsystems, mechanisms, purviews, and partitions that must be considered each grows exponentially in the size of the system. This limits the size of systems that can be practically analyzed to ~10–12 nodes. For example, calculating the major complex of systems of three, five, and seven stochastic majority gates, connected in a circular chain of bidirectional edges, takes ~1 s, ~16 s, and ~2.75 h respectively (parallel evaluation of system cuts, 32 × 3.1GHz CPU cores). Using the “cut one” approximation, these calculations take ~1 s, ~12 s, and ~0.63 h. In practice, actual execution times are substantially variable and depend on the specific network under analysis, because network structure determines the effectiveness of the optimizations discussed above.

Another limitation is that the analysis can only be meaningfully applied to a system that is Markovian and satisfies the conditional independence property. These are reasonable assumptions for the intended use case of the software: analyzing a causal TPM derived using the calculus of perturbations []. However, there is no guarantee that these assumptions will be valid in other circumstances, such as TPMs derived from observed time series (., EEG recordings). Whether a system has the Markov property and conditional independence property should be carefully checked before applying the software in novel contexts.

## Availability and future directions

PyPhi can be installed with Python’s package manager via the command ‘’ on Linux and macOS systems equipped with Python 3.4 or higher. It is open-source and licensed under the GNU General Public License v3.0. The source code is version-controlled withand hosted in a public repository on GitHub at. Comprehensive and continually-updated documentation is available online at. Themailing list can be joined at. A web-based graphical interface to the software is available at.

Several additional features are in development and will be released in future versions. These include a module for calculating Φ over multiple spatial and temporal scales, as theoretically required by the exclusion postulate (in the current version, theis assumed to represent the system at the spatiotemporal timescale at which Φ is maximized [,]), and a module implementing a calculus for “actual causation” as formulated in [] (preliminary versions of these modules are available in the current release). The software will also be updated to reflect developments in IIT and further optimizations in the algorithm.

## Supporting information

## S1 Text

Calculating Φ.

Illustration of the algorithm.

## (PDF)

Click here for additional data file.

## S2 Text

Memoization and caching optimizations.

## (PDF)

Click here for additional data file.

## S3 Text

Proof of the strong connectivity optimization.

## (PDF)

Click here for additional data file.

## S4 Text

Proof of the block-factorable optimization.

## (PDF)

Click here for additional data file.

## S5 Text

Proof of an analytical solution to the EMD between effect repertoires.

## (PDF)

Click here for additional data file.

## S1 File

PyPhi v1.1.0 source code.

Note that installing PyPhi via ‘’ or downloading the source code from GitHub is recommended in order to obtain the most up-to-date version of the software.

## (ZIP)

Click here for additional data file.

## S2 File

PyPhi v1.1.0 documentation.

Note that accessing the documentation online atis recommended, as it is updated for each new version of the software.

## (ZIP)

Click here for additional data file.
