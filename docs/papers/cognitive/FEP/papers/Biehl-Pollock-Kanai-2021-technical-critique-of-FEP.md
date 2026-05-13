# A Technical Critique of Some Parts of the Free Energy Principle

**Authors:** Martin Biehl, Felix A. Pollock, Ryota Kanai (per article record)
**Journal:** Entropy, 2021
**DOI:** 10.3390/e23030293
**PMC:** PMC7997279 . **PMID:** 33673663
**License:** Not provided in PMC tool response (PMC open-access)
**Source:** PubMed Central (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7997279/)
**Retrieved:** 2026-05-13

---

## Abstract

We summarize the original formulation of the free energy principle and highlight some technical issues. We discuss how these issues affect related results involving generalised coordinates and, where appropriate, mention consequences for and reveal, up to now unacknowledged, differences from newer formulations of the free energy principle. In particular, we reveal that various definitions of the "Markov blanket" proposed in different works are not equivalent. We show that crucial steps in the free energy argument, which involve rewriting the equations of motion of systems with Markov blankets, are not generally correct without additional (previously unstated) assumptions. We prove by counterexamples that the original free energy lemma, when taken at face value, is wrong. We show further that this free energy lemma, when it does hold, implies the equality of variational density and ergodic conditional density. The interpretation in terms of Bayesian inference hinges on this point, and we hence conclude that it is not sufficiently justified. Additionally, we highlight that the variational densities presented in newer formulations of the free energy principle and lemma are parametrised by different variables than in older works, leading to a substantially different interpretation of the theory. Note that we only highlight some specific problems in the discussed publications. These problems do not rule out conclusively that the general ideas behind the free energy principle are worth pursuing.

## 1. Overview

In [], it was argued that the internal coordinates of an ergodic random dynamical system with a Markov blanket necessarily appear to engage in active Bayesian inference. Here, we reproduce the argument supporting this interpretation in detail and highlight at which points it faces technical issues. In the course of our critique, we also mention issues of some closely related alternative arguments. In cases where our results have clear consequences for the more recent related publications [,], we also mention those. In particular, we point out a conceptual difference in these latter works that has not previously been acknowledged. However, our analysis thereof does not go beyond a few remarks. In an additional section, we discuss the effect of our argument on []. The logical structure of the present paper is depicted in. We note that the technical issues presented here do not affect the validity of approaches where a (expected) free energy minimizing agent is assumed a priori, as presented in, e.g., []. None of [,,,] make this assumption; they instead aim to identify the conditions under which such agents will emerge within a given stochastic process. We criticize specific formal issues in the latter publications but leave open whether they can be fixed. We now briefly introduce the setting of [] and then sketch the content of this paper. We now briefly introduce the setting of [] and then sketch the content of this paper.

The starting point is a random dynamical system whose evolution is governed by the stochastic differential equation: where the system state and vector field are multi-dimensional and is a Gaussian noise term. There is an additional assumption that the system is ergodic, such that the steady state probability density is well defined (In the original paper, the ergodic density is simply denoted. We here add a star to highlight that it is a time independent probability density.). In this case, plays the role of a potential function, in the sense that can be formulated in terms of its gradients [,].

It is then assumed that there is a coordinate system with,,, and, referred to as external, sensory, active, and internal coordinates (these are called "states" in []), respectively, such that the following condition holds:

This particular structure is described as "[formalizing] the dependencies implied by the Markov blanket" []. In contrast, more recent works [,] formulated the Markov blanket in terms of the statistical dependencies of the ergodic density. Specifically, the following condition is presented:

In other words, the internal and external coordinates are independently distributed when conditioned on the sensory and active coordinates. This means we have two different formal expressions of what constitutes a Markov blanket in these publications, and their relationship has not previously been established.

Taking Condition 1 to hold, the argument of [] then proceeds along the following steps:

In the present paper, we make the following main observations:

The latter [] presents an argument almost identical to the one in the original []. In, we discuss how our observations apply to this publication.

### Condition 1

The function can be written as:

(2) f x ( ) = . f ψ ( , , ) ψ s a f s ( , , ) ψ s a f a ( , , ) s a λ f λ ( , , ) s a λ

### Condition 2

The ergodic density factorises as:

(3) p * p * p * p * ( , , , ) ψ s a λ ( | , ) ψ s a ( | , ) λ s a ( , ) s a = .

## 2. Expression via the Gradient of the Ergodic Density

Here, we introduce the expression of the system's dynamics Equation () in the form used for the free energy lemma (Lemma 2.1 in []). This form expresses the dynamics of the internal and active coordinates of the given ergodic random dynamical system in terms of the gradient of the ergodic density. In accordance with the results of [], is rewritten as (see Equation (2.5) in []): where is the diffusion matrix, which we will take to be block diagonal (in [], and later work such as [], is taken to be proportional to the identity matrix), and is an antisymmetric matrix, defined through the relation: with Here, and in all of [,,,], both and are assumed constant. We emphasise here that, for general nonlinear models, these matrices can vary with the coordinates and Equation () holds only approximately [,] (the exact conditions under which these matrices can be chosen to be constant can be found in [,] and, for the discrete state case, []). Moreover, Equation () is derived in the literature under the explicit assumption that the fluctuations be Gaussian and Markov [,]. For the counterexamples we present here, we restrict ourselves to the class of Ornstein-Uhlenbeck processes, for which and are always constant, and the ergodic density is necessarily a multivariate Gaussian with zero mean. Specifically, following [], where is a row vector and is a suitable normalisation constant. From Equation (), it can be seen that, though we emphasise here that strict relations between and can only be made because of the assumption that and are coordinate independent []. This concludes Step 2.

Before moving on to Step 3, we note that, under the assumptions implicit in Step 2, we can express Conditions 1 and 2 in terms of the matrices and (in the nonlinear case, these matrices can still be defined in terms of the derivatives of the force vector field and potential, respectively; however, they will be generally coordinate-dependent, even when and are not []). Firstly, since it effectively states that, with a block sub-matrix of in general. Secondly, because of the multivariate Gaussian nature of, the dependencies of conditional distributions are encoded in the inverse of the covariance matrix; we therefore have that: where is a block sub-matrix of. These implications bring us to our first observation:

Henceforth, unless otherwise stated, we will assume both Conditions 1 and 2. Any implications that fail to hold in this special case cannot hold generally.

### Observation 1

Neither Condition 1 (the vector field dependency structure) nor Condition 2 (conditional independence in the ergodic distribution) imply the other:

(11) Condition 1 Condition 2 (12) Condition 1 Condition 2 .

Proof. In, we provide direct counterexamples, using the equivalent constraints on the matrices and in Equations () and (), for the implication in either direction. That is, there exists a system obeying Condition 1 that does not obey Condition 2 (proving Equation ()), and there exists one obeying Condition 2 that does not obey Condition 1 (proving Equation (12)).

## 3. Re-Expression Using Only Partial Gradients

For Step 3, we focus on the components and of. Without loss of generality, we can rewrite them from Equation () as: where () is the block of () connecting derivatives with respect to the coordinates to the time derivatives of the coordinates. The expectation value with respect to leaves the left-hand side of these equations unchanged. A few manipulations ([] cf. Equation (12.14), p. 129) reveal that, on the right-hand side, this leads to the ergodic density being replaced by the marginalised ergodic density so that we get: Since, the terms involving drop out: We are not aware of how to further simplify this equation without additional assumptions. However, in (Equations (2.5) and (2.6) of []), all of the off-diagonal terms are implicitly assumed to vanish, i.e., Equation () is equated with: This equation is the result of Step 3.

More recently (Appendix B of []), a more detailed discussion of Equation () was presented, where it was claimed that Condition 1 implies Condition 2 (cf. our Observation 1) along with the following simplification of Equations () and (18) ([], Equations (12.8)-(12.11), (12.15), pp. 126-129):

However, Equations () and (22) are still provably less general than Equations () and (), even when both Conditions 1 and 2 are satisfied.

In order to arrive at Equations () and (22) from Equations () and (18) in general, one must remove the offending "solenoidal flow" terms by fiat. That is, one assumes. In [], Equation (12.4), the following, even stronger, condition was assumed as an alternative starting point (along with Condition 2):

This is claimed to imply, but not the full Condition 1. However, in [], both Conditions 1 and 3 were assumed (along with). This prompts our next observation.

In this case, the four sets of coordinates interact in a chain, and it is questionable whether the and coordinates can be meaningfully interpreted, respectively, as sensory inputs to the internal coordinates or their boundary-mediated influence on the external coordinates.

### Observation 2

Given a random dynamical system obeying Equation (), ergodicity, and both Conditions 1 and 2, none of Equations ()-(22) generally hold.

Proof. By counterexample, see. There, we show explicitly that a model satisfying the above assumptions does not satisfy the equations in question.

### Condition 3

The blocks of the R matrix appearing in Equation () coupling coordinates to lambda and psi coordinates and psi coordinates to lambda coordinates vanish, i.e.,

(23) R ψ s R ψ a R ψ λ R s λ R a λ = = = = = . 0

### Observation 3

In a system satisfying both Conditions 1 and 3, the internal coordinates cannot be directly influenced by the sensory coordinates:, and the external coordinates cannot be directly influenced by the active coordinates:.

Proof. From Equation (), it follows that: with the inverse replaced by a pseudoinverse if is not invertible. Therefore, if and for blocks of coordinates labelled by and, then: and. Condition 3 implies that only the nonzero blocks of are,,,,, and, and is assumed to be block diagonal. As noted in Equation (), Condition 1 requires that. Through Equation (), these together imply that, and hence that: as shown.

## 4. Free Energy Lemma

The relation of the dynamics of the internal coordinates to Bayesian beliefs is made by introducing a density (called the variational density) that is then interpreted as encoding a Bayesian belief. It is parameterized by the internal coordinates and claimed to be "arbitrary". We take this "at face value" and consider to be parameterized only by and, therefore, to be independent of. (We note that there is a convention in the literature on variational Bayesian inference, e.g., in [], to drop the observed variables/data in the variational density. It is possible that in [], was seen as observed variables and dropped from the variational density as in this convention. However, the reason that dropping the observed variables is justified in the established convention is that those observed variables are fixed throughout the minimization of the variational free energy and the parameters of the variational density do not influence the observed data in any way. In other words, the variational density is optimized for a single data point. In [], the data point was continuously changing and partially doing so with dependence on the parameter as. These differences and their consequences are non-trivial and beyond the scope of this paper, so we assume that the variational density does not depend on.) If is allowed to depend on, Observation 4 does not apply, and the free energy lemma is made trivially true by setting. The existence of the variational density is asserted by the free energy lemma (see Lemma 2.1 in []) (Explicitly, the free energy lemma asserts the existence of a free energy in terms of which can be expressed and not the existence of. However, since the free energy is defined as a functional of, it exists if and only if a suitable exists.).

More precisely, the free energy lemma (and Step 4) asserts that for every ergodic density (equivalently as expressed in [], for every Gibbs energy) of a system obeying Equations () and (20), there is a free energy, defined as: in terms of the "posterior density" (here, we keep the conditioning argument, as in [], and do not explicitly assume Condition 2, though our conclusions are unaffected by it), such that Equations () and (20) can be rewritten as:

It is worth considering what a proof of the free energy lemma could look like. A proof of the existence of a free energy (and therefore of the free energy lemma) would need to show that, for every system satisfying the given assumptions, there always exists a such that the right-hand sides of Equations () and () are equal to the right-hand sides of Equations () and (). Expanding Equations () and () using (28) leads to: For the equality of the right-hand sides to those of Equations () and (20), we need: In other words, these equations say that the free energy lemma holds if any of the following three conditions (of strictly increasing strengths) are given:

The free energy lemma can then be proven by showing that one of these three cases follows from the conditions of the lemma. However, no attempt was made in [] to establish this. Instead, the given proof discusses the purported consequences of the existence of a suitable. These will be discussed in Steps 5 and 6.

Even if the free energy lemma does not hold for systems obeying Equations () and (), one might expect that the systems instead only satisfy the more general Equations () and () or the most general Equations () and (). For these systems, the free energy lemma would require that there is a such that: or: hold, respectively. However, we find this not to be the case in general.

Before proceeding, we note that later works presented an alternative version of the free energy lemma, where the conditioning argument of was replaced by the most likely value of conditional on the coordinates [,]. We here concern ourselves with the version apparent in [], where is parametrised by the internal states themselves, but we briefly comment on the interpretation of the alternative approach in Step 7.

### Observation 4

Given a random dynamical system obeying Equation (), ergodicity, Conditions 1 and 2, there need not exist a free energy expressed in terms of a variational density such that:

(i) Equations () and () hold if Equations () and () do;

(ii) Equations () and () hold if Equations () and () do not hold, but Equations () and () do;

(iii) Equations () and () hold if neither Equations () and () nor Equations () and () hold, but Equations () and () do.

Proof. In, we derive a set of conditions on the and matrices and on the putative variational density, which follow from each of the pairs of equations in Cases (i-iii). We show that, in general, each pair leads to a contradiction, and in each case, we provide a counterexample that falls into the according system class.

## 5. Vanishing Gradients

As mentioned in Step 4, the proof of the free energy lemma in [] only discussed its consequences. The first proposed consequence is that expressing the vector field in terms of a free energy as in Equations () and (30) "requires" that the gradients with respect to and of the KL divergence vanish, i.e., that Equations () and (36) hold.

We mentioned in Step 4 that the implication in the opposite direction holds. This can be seen from Equations () and (34). However, if the nullspace of or is non-trivial, then the gradient may be a non-zero element of this subspace and Equations () and () will still hold. In that case, the vanishing gradients would not be necessary for the free energy lemma.

The conditions under which a non-trivial nullspace exists were discussed in []. In short, the nullspace is guaranteed to be trivial in the special case where is positive definite. Whether or not ergodic systems with a Markov blanket can ever admit a non-trivial nullspace, and hence divergences in Equations () and () with non-vanishing gradients, is not immediately clear. However, in order to establish the necessity of Equations () and (), this remains to be proven.

## 6. Equality of and

The proof of the free energy lemma in [] also proposes that the vanishing of the gradients of the KL divergence, of the variational density from the conditional ergodic density, implies the equality of these densities. We mentioned in Equations (5) that the implication in the opposite direction holds. This can also be seen from Equations () and (). Concerning the implication in the direction proposed by [], let us now assume that for a given system of Equations () and () holds, a variational density does exist, and the gradients of the KL divergence of the variational and ergodic densities vanish, i.e., Equations () and () hold. Then, consider the argument by [] in this direct quote (comments in square brackets by us):

The first problem in the above quote is that the minimization of the divergence does not follow from the vanishing gradients. On the contrary, since Equations () and (36) must hold for all, the KL divergence: cannot depend on; it therefore has no extremum (and thus no minimum) with respect to either of these coordinates.

The second problem pertains to the identification of the two distributions at a minimum. In general, if we try to find the minimum of a KL divergence between a given probability density and a family of densities parameterized by, then the lowest possible value of zero is achieved only if there is a parameter such that. If there is no such, then the minimum value will be larger than zero. Therefore, even if the divergence were minimized, it would not need to be zero. More generally, the divergence need not be zero for any value of.

There is therefore no satisfactory reason given why the variational density and the posterior density should be equal or have low KL divergence. In fact, they need not be (Note that, since any that does not depend on is an element of the set of those that do, Observation 5 remains true for the case where we allow this dependence. In that case, the free energy lemma holds because we can set, and thus, a exists for which the densities are actually equal. However, the claim here is that for every that obeys the conditions in Observation 5, we must have equality.).

> "However, Equation (2.6) [Equations () and () above] requires the gradients of the divergence to be zero [Equations () and ()], which means the divergence must be minimized with respect to internal states. This means that the variational and posterior densities must be equal:
>
> In other words, the flow of internal and active states minimizes free energy, rendering the variational density equivalent to the posterior density over external states."

### Observation 5

Given a random dynamical system obeying Equation (), ergodicity, Conditions 1 and 2. Then if, additionally, then there is no for which it can be guaranteed that:

In particular, it does not follow from these conditions that:

(i) Equations () and () hold and the free energy lemma holds, i.e., there exists a probability density such that Equations () and () hold, or

(ii) Equations () and () hold and there exists such that Equations () and () hold, or

(iii) Equations () and () hold and there exists such that Equations () and () hold,

(41) D K L [ | | q ( | ) Psi lambda ( | , , ) Psi s a lambda ] < . c p * (42) q ( | ) Psi lambda ( | , , ) Psi s a lambda = . p *

Proof. By example, see. To show that the implication does not generally hold for a given system and densities that obey Equations (), (), (), and (), Equations (), (), (), and (), or Equations (), (), (), and (), we only have to consider a system that obeys all three pairs of equations, Equations () and (), Equations () and (), and Equations () and (), and for which a suitable exist. For this system, we then need to show that the that obey Equations () and (30) are not necessarily equal (or similar) to.

We use a variant of the model used in as such a counterexample. This system obeys all three of Equations () and (), Equations () and (), and Equations () and (), and the nullspace of the associated is trivial. We identify a set of possible satisfying Equations () and (30), which implies that the gradients of the KL divergence between those and vanish, i.e., Equations () and (36) hold. We then demonstrate that for the in this set, the value of the KL divergence to can be arbitrarily large.

## 7. Interpretation

Finally, we turn our attention to the interpretation in terms of Bayesian inference, i.e., Step 7. We again quote directly from []:

We showed that, in general, there is no suitable variational density that is only parameterized by the internal coordinate. We then showed that, even if there is a suitable variational density (including those parameterized by all of), it can be arbitrarily different from the posterior density. Since the arguments for the internal flow appearing to minimize the divergence between variational and posterior density are therefore incorrect, there is no reason why the internal states should appear to have solved the problem of Bayesian inference.

As mentioned in Step 4, some newer works (e.g., [,]) formulated a different free energy principle, where the variational density of beliefs is parametrised not by the internal coordinates, but by, the most likely value of the internal coordinates given the sensory and active ones. In this case, Observations 4 and 5 do not apply. However, the new parameters are strictly a function of the sensory and active coordinates. This means we have a Markov chain (with capitalisations indicating random variables associated with the corresponding lower case coordinates (or functions of coordinates)) and, by the data processing inequality [], the mutual information between the both sensory and active coordinates and the belief parameter upper bounds that are between the internal coordinates and the belief parameter. It is therefore not clear to what extent the internal coordinates, rather than the active and sensory coordinates themselves, can be said to be encoding beliefs about the external coordinates. Note also that, on any given trajectory, unless the distribution is sufficiently peaked and unimodal, the internal coordinates are not guaranteed to spend most of their time close to their most likely conditional value, and (by definition if Condition 2 holds) they will not be better predictors of the external coordinates than those in the Markov blanket.

Generally,, and is the solution to an optimization problem that is assumed to be solved in these later works. Using this optimized variable to parametrise beliefs is therefore a considerable departure from []. Contrary to the impression created by the way it was referenced in [,], the older theory in [] should be clearly distinguished from the newer ones in these more recent papers.

> Because (by Gibbs inequality) this divergence [D] cannot be less than zero, the internal flow will appear to have minimized the divergence between the variational and posterior density. In other words, the internal states will appear to have solved the problem of Bayesian inference by encoding posterior beliefs about hidden (external) states, under a generative model provided by the Gibbs energy.

## 8. Consequences for Friston, K. et al. 2014

Reference [] argued for the same interpretation as [], but there were some differences in the argument.

The differences were the following:

The interpretation in terms of Bayesian inference was unchanged and still relied on the equality of the variational and the ergodic conditional density.

Since there were no explicit generalized coordinate versions of Steps 2, 3, 5 and 6 in [], we do not discuss those steps here. We only disprove the free energy lemma and the claim that when the free energy lemma holds, the variational and ergodic conditional density become equal. For this, we present a way to translate the counterexamples used in Observations 4 and 5 into counterexamples in generalized coordinates. The interpretation in terms of Bayesian inference given in [] is therefore equally as unjustified as the one in [].

For completeness, we first state the generalized coordinate versions of the stochastic differential Equation (): the less general version of the Markov blanket structure Equation (): the expression of the and components of the vector field in terms of the marginalised ergodic density Equations () and (20): and in terms of free energy Equations () and (30): The free energy lemma then requires that there exists such that the KL divergence between vanishes. Without going into further details of the difference between the proof in [] and that in [], we can prove the former wrong by translating the counterexample used for the latter into generalised coordinates.

This implies that the counterexamples used in proving Observations 4 and 5 directly translate to the setting of the generalised coordinates. The free energy lemma is therefore also wrong for generalised coordinates, and the variational density is not "ensured" [] to be equal to the conditional ergodic density.

### Observation 6

There is a general way to translate a system in ordinary coordinates into a system of generalised coordinates that corresponds to an infinite number of independent copies of the original system. This means all properties of the original system (e.g., linearity, ergodicity, the Gaussian and Markovian property of the noise, Conditions 1 and 2, the properties of) are preserved during this translation.

Proof. By construction, see.

## 9. Conclusions

We find that the two different Markov blanket conditions proposed in [,,] are independent of each other. We then show that under both of those Markov blanket conditions, among the six steps contained in the argument in [], three do not hold independently of each other. We also show that fixing the second of those steps (Step 3) does not provide a valid alternative. The line of reasoning of [] therefore does not support its claim that the internal coordinates of a Markov blanket "appear to have solved the problem of Bayesian inference by encoding posterior beliefs about hidden (external) [coordinates], ...". We also show that using generalised coordinates as in [] does not remedy the situation. Additionally, we identify a technical error in [] and an interpretational issue resulting from possibly too strong assumptions (both Conditions 1 and 3) in []. We also highlight that the latter publications both argued that it is the most likely internal coordinates given sensory and active coordinates that encode posterior beliefs about external states instead of the internal coordinates themselves. The resulting free energy principle and lemma are therefore a different proposal. This is not subject to our technical critique.
