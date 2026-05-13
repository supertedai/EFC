# A Theory of Consciousness from a Theoretical Computer Science Perspective: Insights from the Conscious Turing Machine

**Authors:** Lenore Blum, Manuel Blum
**Journal:** Proceedings of the National Academy of Sciences of the United States of America (PNAS), 2022
**DOI:** [10.1073/pnas.2115934119](https://doi.org/10.1073/pnas.2115934119)
**PMC:** PMC9171770 - **PMID:** 35594400
**License:** PMC Open Access (PNAS Open Access; check PMC record for specific license terms)
**Source:** PubMed Central (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9171770/)
**Retrieved:** 2026-05-13

---

## Abstract

### Significance

This paper provides evidence that a theoretical computer science (TCS) perspective can add to our understanding of consciousness by providing a simple framework for employing tools from computational complexity theory and machine learning. Just as the Turing machine is a simple model to define and explore computation, the Conscious Turing Machine (CTM) is a simple model to define and explore consciousness (and related concepts). The CTM is not a model of the brain or cognition, nor is it intended to be, but a simple substrate-independent computational model of (the admittedly complex concept of) consciousness. This paper is intended to introduce this approach, show its possibilities, and stimulate research in consciousness from a TCS perspective.

This paper examines consciousness from the perspective of theoretical computer science (TCS), a branch of mathematics concerned with understanding the underlying principles of computation and complexity, including the implications and surprising consequences of resource limitations. We propose a formal TCS model, the Conscious Turing Machine (CTM). The CTM is influenced by Alan Turing's simple yet powerful model of computation, the Turing machine (TM), and by the global workspace theory (GWT) of consciousness originated by cognitive neuroscientist Bernard Baars and further developed by him, Stanislas Dehaene, Jean-Pierre Changeux, George Mashour, and others. Phenomena generally associated with consciousness, such as blindsight, inattentional blindness, change blindness, dream creation, and free will, are considered. Explanations derived from the model draw confirmation from consistencies at a high level, well above the level of neurons, with the cognitive neuroscience literature.

---

The quest to understand consciousness, once the purview of philosophers and theologians, is now actively pursued by scientists of many stripes. We study consciousness from the perspective of theoretical computer science (TCS), a branch of mathematics concerned with understanding the underlying principles of computation and complexity. This abstract theory has provided both a theoretical foundation for the computer revolution and (also) surprising new concepts and ingenious applications stemming from considerations of computational complexity. It deals with the consequences and unexpected insights that come from taking resource limitations into account. We claim that the perspective and unique insights of TCS add to the understanding of consciousness and related concepts, such as free will.

## 1. A TCS Perspective on Consciousness

Our view is that consciousness is a property of all properly organized computing systems, whether made of flesh and blood or metal and silicon. With this in mind, we give a simple abstract substrate-independent computational model of consciousness (section). We are not looking to model the brain nor to suggest neural correlates of consciousness, interesting as they are. We are looking to understand consciousness and its related phenomena.

We begin this introduction with a brief overview of TCS, its perspective, and an example of a relevant seemingly paradoxical concept that got defined and understood by TCS. We then outline how the perspective of TCS informs our model and understanding of consciousness. Following the Introduction, we present the Conscious Turing Machine (CTM), which is our formalization of a variant of the global workspace theory (GWT). The reader who wants the formal model first can go directly to section.

### 1.1. TCS

Alan Turing's seminal paper "On computable numbers, with an application to the Entscheidungsproblem" is arguably the genesis of TCS. That paper presents a mathematical definition of a "computing machine," now known as the Turing machine (TM). In it, Turing defines a simple theoretical universal programmable computer that can compute any function computable by any computer or supercomputer.

Theorems are the raison d'etre of mathematical theories, and Turing proves what might be called the first theorem of TCS, namely the unsolvability of the Halting problem. In modern parlance, this theorem proves there can be no universal (debugging) program for determining which computer programs halt and which do not; it is just not possible to construct one.

The unsolvability of the Halting problem is equivalent to the undecidability of elementary number theory, and implies a weak form of Kurt Godel's first incompleteness theorem.

After Godel and Turing, mathematical logicians started categorizing which problems were solvable and which were not as well as investigating the esoteric hierarchy of unsolvable problems.

With the advent and wider availability of computing machines in the 1960s, it soon became clear that a number of important problems that were solvable in principle could not in fact be solved, not even with the fastest conceivable computers, and that this was not a problem with the state of technology but something deeper.

Researchers in the emerging field of TCS [notably Jack Edmonds, Stephen Cook, Richard Karp, and Leonid Levin] realized that among natural finite (and therefore, solvable) problems, there appeared to be a dichotomy between those problems that were feasibly (efficiently) solvable and those that were not, mirroring the earlier dichotomy between solvable and unsolvable. Feasibly solvable became formalized mathematically as solvable (by some computer program) in polynomial time (P). Furthermore, the realization emerged that problems solvable in polynomial time and problems checkable in polynomial time (NP) might not be equivalent. Indeed, deciding the equivalence would answer the famous million dollar P = ?NP question.

Besides defining a hierarchy of serial fast (poly time) computational complexity classes, TCS defines a hierarchy of parallel superfast (polylog time) computational complexity classes. Both hierarchies inform the definitions and choices employed in our model. Michael Sipser's book is a great introduction to TCS.

Understanding the dichotomy between easy and hard, quick and slow, and their implications launched a complexity revolution with a rich theory, reframing of ideas, novel concepts, and stunning applications. Indeed, developments in computational complexity over the past 40 y have shown how to use hardness to our advantage to deal with seemingly impossible problems.

We illustrate with the (relevant) concept of a computer-generated random sequence, called a pseudorandom sequence.

On the face of it, the very idea of a pseudorandom sequence is so incongruous that von Neumann joked that "[a]nyone who considers arithmetical methods of producing random digits is, of course, in a state of sin."

More precisely, a pseudorandom sequence generator is a feasible (polynomial time) computer program for generating sequences that cannot be distinguished from truly random sequences (generated by independent tosses of a fair coin) by any feasible computer program. Thus, in the polynomial time world in which we live, pseudorandom sequences are, for all intents and purposes, truly random. This understanding was impossible without the clarifications made by TCS, including the distinctions between polynomial and superpolynomial complexity.

An application of the above ideas is to replace the use of random sequences in the (probabilistic) CTM by sequences produced by pseudorandom generators supplied with (short) random seeds. In particular, if the probabilistic CTM has "free will," as will be argued, then so does this deterministic variant of CTM. The free will of this deterministic CTM is counter to some (perhaps much) of the thinking on determinism (e.g., ref.).

### 1.2. Now for Consciousness

The TCS perspective is employed in defining the CTM, a simple machine that formalizes mathematically (and modifies with dynamics) the GWT of consciousness originated by cognitive neuroscientist Bernard Baars and extended by Dehaene and Mashour et al. in their global neuronal workspace theory (GNWT). In, Baars describes consciousness through a theater analogy as the activity of actors in a play performing on the stage of working memory, their performance under observation by a huge audience of unconscious processors sitting in the dark.

In the CTM, the stage of GWT is represented by short-term memory (STM) that at any moment in time contains CTM's conscious content. The audience members are represented by enormously powerful processors—each with its own expertise—that make up CTM's long-term memory (LTM) (section). These LTM processors make predictions and get feedback from CTM's world. Based on this feedback, learning algorithms internal to each processor improve that processor's behavior (section).

LTM processors, each with their own specialty, compete (sectionsand) to get their questions, answers, and information in the form of chunks (section) on the stage for immediate broadcast to the audience.

Conscious awareness—elsewhere called attention—is defined formally in the CTM as the reception by the LTM processors of the broadcast of CTM's conscious content. In time, some of these processors become connected via links (section) that turn conscious communication (through STM) into unconscious communication (through links) between these LTM processors. Communication via links about a broadcasted chunk reinforces its conscious awareness, a process that Dehaene, and Changeux call ignition.

While these definitions are natural, they are merely definitions; they do not provide a proof that the CTM feels conscious. We argue, however, that these definitions, together with explanations derived from the CTM model, capture commonly accepted intuitive concepts of consciousness and agree, at a high level, with cognitive neuroscience explanations of phenomena generally associated with consciousness.

Although inspired by Baars' GWT architecture, the CTM integrates additional features essential for its feeling of consciousness. These include its dynamics, its rich multimodal inner language (which we call Brainish) (section), and special LTM processors that enable it to create models of the world (sectionsand).

### 1.3. Complexity Considerations

The consequences of limited resources play a crucial role in our high-level explanations for consciousness-related phenomena, such as change blindness and the feeling of free will.

They also enter into fixing the detailed definition of CTM. These details include, for example,

Although inspired by Turing's simple yet powerful model of a computer, the CTM is not a standard TM. That is because what gives the CTM its "feeling of consciousness" is not its computing power nor its input-output maps but rather, its global workspace architecture, its predictive dynamics (cycles of prediction, feedback, and learning), its rich multimodal inner language, and certain special LTM processors such as the Model of the World processor.

As we have said, we are not looking for a model of the brain but for a simple model of consciousness, and even there, the CTM model can hardly be expected to explain everything; it is too simple for that. The reasonableness of the model (and its TCS perspective) should be judged by its contribution to the discussion and understanding of consciousness and related "hard" problems.

This paper presents an overview of the CTM model; we refer the reader to refs. and for additional details. Whereas ref. explores explanations for the feelings of pain and pleasure in the CTM, this paper presents additional phenomena generally associated with consciousness. We start (in section) with three examples related to vision (blindsight, inattentional blindness, and change blindness) and then, follow with a discussion of dreams and free will. We give explanations derived from the model and draw confirmation from consistencies at a high level with the cognitive neuroscience literature. Confirmation for the model also comes from agreement with aspects of other theories of consciousness.

In what follows, statements about the CTM are in roman. Statements particular to humans or animals are generally in italics.

## 2. CTM Model Overview

### 2.1. Basic CTM Structure and Definitions of Consciousness in the CTM

We assume that the CTM has a finite lifetime. Time is measured in discrete clock ticks, t = 0, 1, 2, …, ~ 10 (roughly 10 ticks per second,). The CTM is born at time 0.

The CTM is a seven-tuple,

< STM, LTM, Up Tree, Down Tree, Links, Input, Output >

with the following components.

#### 2.1.1. STM and LTM processors

In the CTM, is a small memory capable of holding a single, defined in section. LTM is a (massive) collection of processors, > 10, with each processor being a random access machine with a random access memory large enough to hold a small multiple of chunks. Processors are in only, not in STM, so when we say processor, we mean processor. Certain special LTM processors are particularly responsible for CTM's feeling of consciousness. These include especially a Model of the World processor, an Inner Speech processor, and other Inner generalized Speech processors for handling inner vision, inner tactile sensation, and so on (section).

#### 2.1.2. The Up Tree competition and Down Tree broadcast

The is a simple down-directed tree of height 1 with a single root in STM and edges directed from that root to the leaves, one leaf in each LTM processor.

The is an up-directed binary tree of height h with leaves, one leaf in each LTM processor, and a (single) root in STM. LTM processors, each with their own specialty, compete via the (section) to get their questions, answers, and information into STM for immediate via the Down Tree to the audience of all LTM processors. For simplicity in CTM, all LTM processors submit information to the competition for STM, and all processors receive all broadcasts from STM.

This bottom-up/top-down cycle is analogous to the global neuronal workspace (GNW) hypothesis that "conscious access proceeds in two successive phases … In a first phase, lasting from approximately 100 to approximately 300 ms, the stimulus climbs up the cortical hierarchy of processors in a primarily bottom-up and nonconscious manner. In a second phase, if the stimulus is selected for its adequacy to current goals and attention state, it is amplified in a top-down manner and becomes maintained by sustained activity of a fraction of GNW neurons, the rest being inhibited. The entire workspace is globally interconnected in such a way that only one such conscious representation can be active at any given time."

#### 2.1.3. Chunks, conscious content, conscious awareness, and stream of consciousness

Questions, answers, and information are conveyed in the form of (defined formally in section). The chunk that wins the Up Tree competition to get into STM is called the of CTM.

In the CTM, unlike Baars' theater, there is always exactly one and the same actor in STM (the stage). At every step in time, that actor gets handed the winning chunk as a script for immediate broadcast via the Down Tree. We say that CTM becomes of this content when it is received by all LTM processors via this broadcast.

We have defined conscious awareness as the reception by all LTM processors of STM's broadcast rather than the appearance in STM of the winning chunk to emphasize that the feeling of consciousness arises after processors, including especially the Model of the World and Inner Speech, receive the broadcast.

Our definition of conscious awareness in the CTM aligns roughly with what cognitive neuroscientists call "attention" (for example, refs. and). What we call the feeling of consciousness in the CTM (section) aligns roughly with what cognitive neuroscientists call "awareness" or "subjective consciousness."

CTM is constantly bubbling with the activity of chunks competing for STM, its winners being (constantly) broadcast from STM to LTM. The time-ordered chunks that are broadcast from STM to LTM form a. This stream, as argued in section, is part of the subjective feeling of consciousness.

#### 2.1.4. Links, unconscious communication, and global ignition

All communications between processors initially occur via STM. For example, processor A can submit a query to the Up Tree competition for STM. If the query wins the competition, it is broadcast to all LTM processors. Processor B may then submit an answer via the competition, which if it wins, gets broadcast and so on.

If A acknowledges that B's answer is useful sufficiently often, then a bidirectional forms between A and B.

In addition to processors sending chunks to the Up Tree competition, processors send chunks over links. In this way, (through STM) between A and B can turn into direct by chunks being sent (through links) between A and B. As additional links form between A and B, we say that the link between A and B is strengthened.

Links are channels for transmitting information between processors. Those chunks sent between linked processors following the broadcast of CTM's conscious content can reenforce and sustain conscious awareness.

#### 2.1.5. Input and Output maps: Sensors and actuators

CTM's (Env) is a subset of R(t), where R denotes the real numbers, m is a positive integer dimension, and t (a nonnegative integer) is time. take (time-varying) environmental information acquired by CTM's (which for simplicity, we assume are part of the input maps) and send it to designated LTM processors that convert the environmental information into chunks (section). take command information from LTM processors to (which we assume are part of the output maps) to act on the environment.

#### 2.1.6. Summary of connections

In summary, there are five kinds of connections in the CTM that provide paths and mechanisms for transmitting information. The five, also shown in (connections in the CTM to and from an LTM processor), are

**Fig. 1.** Connections in the CTM to and from an LTM processor.

### 2.2. Brainish (the CTM's Multimodel Inner Language), Gists, and Chunks

is CTM's inner language used to communicate between processors whether via the competition and broadcasts or directly through links. On the other hand, languages used internally by processors vary in general from one processor to another; they include but are not restricted to Brainish.

Brainish is the language used to express inner speech, inner vision, inner sensations, imaginings, and dreams. It includes coded representations of inputs and outputs all expressed with succinct multimodal Brainish words and phrases called gists. A gist can hold the essence of a scene or the (high-level expandable) idea of a proof. It can be an answer to a query, an insight of some sort, a dream image, a (description of) pain, and so on. Brainish is able to express and manipulate images, sounds, tactile sensations, and thoughts—including unsymbolized thoughts—better than outer languages, like English, Chinese, or "Doggish" (see ref.). We claim that having an expressive inner language is an important component of the feeling of consciousness (section).

Information is carried on all edges, between processors, between STM and LTM, from input to LTM, and from LTM to output by chunks.

A is a six-tuple

,

where

We note that the size of the chunk (and hence, the size of its components, including its gist) will necessarily be bounded by computational complexity considerations (section and ref. have more specifics).

### 2.3. The (Probabilistic) Up Tree Competition: The Coin-Flip Neuron and Competition Function

The is the mechanism that determines which LTM processor will get its chunk into STM. At each clock tick t = 0, 1, …,, the t competition starts with each processor p putting its chunk into the node that is the processor's leaf of the Up Tree. After a chunk is submitted to the Up Tree competition and while it moves up the "competition tree", its address, t, gist, and weight remain unchanged, but its intensity and mood get updated to incorporate ever more global information.

Deciding whether or not a chunk moves up a level or drops out is made by a fast tiny parallel circuit, with one such circuit located in each of the nonleaf nodes of the Up Tree, each making its decision in one clock tick (the time between two successive clock ticks).

In the, which we discuss here, each node of the Up Tree has and uses a in its built-in circuit. A coin-flip neuron is a device that takes as input a (ordered) pair (a, b) of nonnegative real numbers (a >= 0 and b >= 0) and in one step, does the following:

At each clock tick, the circuit in a nonleaf node v runs a local competition that probabilistically selects one of v's two (sibling) children based on a comparison of the chunks they contain and then moves (a variant of) the chosen chunk into v. That chunk is said to be the at/for v.

The local competition employs the Up Tree's f, a function that maps chunks to nonnegative real numbers in a fraction of a clock tick, to choose the.

Specifically, suppose at level s, 0 < s <= h, and node v at that level, chunk and chunk are the chunks in v's left and right children, respectively. Then,

We now specify the chunk that moves into v. Suppose that the local winner at v is the variant of chunk having address, t, gist, and weight. Then, the chunk that moves into v will be gist = gist; weight = weight; intensity = (intensity) + (intensity); and mood = (mood) + (mood).

Note that intensity = sum(intensity) and mood = sum(mood), where the two sums are over all LTM processors p' in the subtree rooted at v.

Updating the chunk at node v consists of computing the probabilities needed to select the local winner and then, to make the needed modifications of its intensity and mood. This must all be done in one clock tick. This puts bounds on both the amount of computation that can be performed in a node and on the size of the chunk in that node (section and ref. have more specifics).

By a simple induction, the winner of the Up Tree competition (the conscious content of CTM at time t + h) will look like where intensity = sum(intensity) and mood = sum(mood).

Let t >= h. The current mood of CTM at time t, mood, is defined to be the mood of the chunk that is broadcast from STM at time t. Thus, CTM becomes consciously aware of mood at time t + 1.

mood = sum mood, so mood/ is the average mood of the chunks submitted to the competition at time th.

is a measure of CTM's "optimism/happiness" if positive, or "pessimism/sadness" if negative at time t.

is a measure of CTM's level of "energy/enthusiasm/confidence" at time t.

We say that a competition function f is if f(chunk(v)) = f(chunk(v)) + f(chunk(v)). Examples of additive competition functions include f(chunk = intensity or more generally,

We call a CTM with a probabilistic Up Tree competition a. In this paper, unless otherwise stated, all CTMs will from now on be probabilistic.

**Theorem.** If the competition function f of a probabilistic CTM is additive, then every chunk submitted to the Up Tree competition gets a fraction of time in STM proportional to its importance as determined by f. Specifically, the probability that a submitted chunk gets into STM is

As a consequence, for additive f, the permutation chosen to assign processors to leaves of the Up Tree has no effect on the sequence of broadcasts from STM. Additionally, even those chunks with low f value have some chance of getting into STM. (Ref. has more specifics, including the statements of this and other theorems and their proofs.)

### 2.4. Complexity of Computation and Time Delay for Conscious Awareness

For t > 0 and s > 0, the computation to update the chunk at node v in the Up Tree competition consists of

These computations, all three of which must be completed in 1 time unit, put a bound on both the size of the chunk in a node and the amount of computation that can be performed in that node.

### 2.5. Memories and the High-Level Story

We assume that each processor p stores in its internal memory the sequence of tuples, ordered by time t, consisting of the chunk that it submitted to the competition, the chunk it received at time t by broadcast from STM, and a select subset of chunks it received at time t from links or from input maps. These sequences are a substantial part of CTM's.

This "history" provides a of what p saw and did. High-level stories account in large part for CTM's sense of self in its feeling of consciousness (section). CTM calls on high-level stories coupled with prediction algorithms to create dreams (section).

Periodically, this stored information may be pruned so only "salient" chunks remain, the most salient being those that represent terrible, wonderful, or unexpected events. In general (section), every processor makes predictions regarding the chunks it generates, modifies, and stores.

### 2.6. Predictive Dynamics = Prediction + Feedback + Learning (Sleeping Experts Algorithm)

Processors require feedback to assess correctness and detect errors in their predictions and to learn how to both boost correctness and diminish and correct errors.

There is a continuous cycling of prediction, feedback, and learning within CTM. The CTM needs to be alerted to anything unusual, surprises of any kind, in order to deal with such things if necessary and to improve its understanding of the world in any case. Prediction errors (e.g., "surprises") are minimized by this cycling.

Processors especially need to know if they were too timid or too bold in setting their |weights|, so they can correct their weight-assigning algorithms. (SEAs) are a class of learning algorithms employed by LTM processors to do just that [Blum and coworkers (-)]. Here is one of the simplest versions of the SEAs.

Embolden a processor (raise the intensity it gives its chunks) if

Hush a processor (lower the intensity it gives its chunks) if

SEAs play a role in whether or not processors get their chunks into STM. They also play a role in whether or not processors "pay attention" to gists in chunks that are sent to them via links. The |weight| of a chunk is an indication of how important the processor that generated the chunk believes its gist to be, and this will influence whether or not a processor that receives the chunk will pay attention to it.

### 2.7. Comparison of CTM with the GWT Model

We conclude this section with a comparison between the CTM and Baars' GWT model.

Aiming for simplicity, we have eliminated or simplified many features. For example, the CTM has just one "actor" on stage holding just one chunk at a time. Additionally, all processors in the CTM are in LTM. We have eliminated the central executive since its functions can be handled by processors. In the CTM, inputs and outputs go directly to and from LTM processors, not directly through STM.

In the CTM, chunks compete in a well-defined competition to get onto the stage (STM). Conscious awareness (attention) is the reception by all LTM processors of the broadcasted winning chunk (i.e., CTM's conscious content), not an event that occurs between input and STM. The roles of Baddeley and Hitch's verbal rehearsal and visuospatial sketchpads are assumed by LTM processors.

(cycles of prediction, feedback, and learning) and a multimodal inner language (Brainish) as well as computational and complexity considerations are explicit key CTM features.

Finally, as in the "extended mind theory", CTM can have access to existing technology, such as Google, Wikipedia, WolframAlpha, AlphaGo, and so on, in the form of LTM processors tasked to use these apps. This is one way to ensure that CTM has a huge collection of powerful processors at the start of its life (t = 0), a collection that is augmentable throughout its life.

Key features of the CTM model and its dynamics resonate with properties of consciousness that Dennett outlines.

**Fig. 2.** Sketches of models: Baars' GWT model (left) and the CTM (right).

> [Neither] a Master Scheduler, nor a Boss Neuron, nor a Homunculus or Res Cogitans [govern the transitions of our conscious minds]. [What governs] must be a dynamical, somewhat competitive process of contents vying for fame, for cerebral celebrity … or relative clout against the competition. What determines the winners? Something like micro-emotions, the strength of positive and negative valences that accompany and control the destiny of all contents, not just obviously emotionally salient events such as obsessive memories of suffering or embarrassment or lust, but the most esoteric and abstract theoretical reflections.

## 3. The Feeling of Consciousness

While CTM is by definition of the conscious content broadcast from STM (section), this definition does not explain what generates the feeling of consciousness in CTM.

We argue that the feeling of consciousness in CTM is a consequence principally of its extraordinarily expressive Brainish language, coupled with CTM's architecture, certain special processors, and CTM's predictive dynamics (prediction, feedback, and learning).

These processors inform the "eyes" and "skin" in CTM's models of the world that "see" whatever the CTM recalls from visual memory and "tactily sense" whatever CTM recalls from sensory memory. These eyes and skin are CTM's mind's eye and mind's skin. We consider these processors to be Inner generalized Speech processors.

We also add

We now return to the Model of the World processor to describe a central task, that of tagging various constituent parts of its models as either self or not self (else unknown).

How does the Model of the World processor determine what is or is not self? If the broadcast of a chunk (a CTM thought) is immediately followed by an actuator carrying out an action in the environment—and that same thought leads to the same action consistently and repeatedly—then that indicates the actuator is part of self. The Model of the World processor has additional important jobs that give the CTM its sense of self, including creating imaginings, creating maps of its environment and registering movements in its environment, helping to plan actions in the environment, helping to predict the actions of self and not self in the environment, and correcting predicted actions of self and not self.

When (through broadcasts) the CTM detects itself thinking about its own consciousness, the Model of the World processor tags the "CTM" in its models as "conscious."

We now look at why the CTM considers itself conscious. It cannot be because the Model of the World processor or any other processor feels it is conscious, as processors are just machines running algorithms—and (such) machines have no feelings. We propose that CTM as a whole feels conscious, as the term is normally understood, as a consequence in part of the fact that the Model of the World processor views the "CTM" in its models of the world as conscious and that this view is broadcast to all processors. Here, "CTM" is a simple learned representation of the much more complex CTM. Our explanation for CTM's feeling of consciousness aligns closely with the attention schema theory of Michael Graziano et al.

1) The multimodal Brainish language describes the sensory world exactly as it is perceived. This perception consists of gists in the multimodal language of sensations. Its words include gists for odors (the odors as they are perceived by the nostrils), pains (the terribly unpleasant sensations of pain), faces (what one sees when looking at someone's face), and so on. Dreams are important because they show what gists can express when the CTM has neither input nor output.

2) This includes the Up Tree competition to gain access to STM (section) and subsequent global Down Tree broadcast of the winner to all LTM processors (particularly all processors that play a special role in generating the feeling of consciousness.

3) We single out a few such processors, which have specialized algorithms built into them at birth.

## 4. High-Level Explanations

We now explore how CTM might experience a variety of phenomena generally associated with consciousness. We believe that our explanations, derived from the model, provide a high-level understanding of how conscious experiences are or might be generated. These draw confirmation from consistencies with the psychology and neuroscience literature at a high level.

Previously, we explored explanations for the feelings of pain and pleasure in the CTM. Here, we consider additional phenomena, again from the perspective of the CTM. We start with three examples related to vision (blindsight, inattentional blindness, and change blindness) and then follow with a discussion of dreams and free will.

### 4.1. Blindsight

Blindsight provides a striking example of the difference between conscious and unconscious awareness. What is going on?

In the CTM, visual input goes directly from the vision sensors to a subset of LTM processors that process visual input. However, in the blindsighted CTM due to some malfunction, perhaps a break in the Up Tree or some other inability for the vision processors to enter chunks competitively into the competition, this information does not get up to STM and hence, does not get globally broadcast. For this reason, CTM is not consciously aware that it can see. However, information can still be communicated between (unconscious) processors via links. So, visual information received by the vision processors can be sent through links to the walk processor that controls the leg actuators.

### 4.2. Inattentional Blindness

Inattentional blindness occurs when an individual fails to perceive a visual stimulus that is in plain sight. It is "the failure to notice the existence of something unexpected when attention is focused on some other task."

What is going on?

Let us suppose the CTM is viewing the gorilla film. The input query about the white-shirted players gains access to STM and is then immediately broadcast to all LTM processors. To carry out the task, CTM's vision processor assigns high intensities to white-shirted gists and very low intensities to anything black. The chunk with the "gorilla" gist has little chance to enter STM. The CTM does not consciously see the gorilla.

The CTM explanation of inattentional blindness reduces to the differential intensities given to gists, lower intensities given to irrelevant ones, and the competing advantages of chunks with higher intensities.

In our view, blocking the "sensory processing" in human brains of black objects is roughly equivalent to the CTM dramatically lowering the intensity of black gists in chunks, thus lowering the chances of those chunks entering STM. The effect of differential intensities in the CTM is also consistent with theoretical implications

### 4.3. Change Blindness

Change blindness occurs when individuals fail to notice large changes in pictures or scenes. It is "the failure to notice when something has changed from one moment to another."

An instructive example is the Whodunnit video. A detective enters a murder scene proclaiming, "Clearly somebody in this room murdered Lord Smythe" and immediately interrogates each suspect in turn. The maid proclaims, "I was polishing the brass in the master bedroom." The butler says, "I was buttering his Lordships scones," and Lady Smythe says, "I was planting my petunias in the potting shed" (enough information for the clever detective to solve the murder on the spot).

However, why did we not notice the many incongruous scene morphs between the beginning screen shot and the end?

From the perspective of the CTM, in viewing the Whodunnit video, CTM has the impression of seeing the whole but does not notice the changes that take place as the trench coat, flowers, painting, and so on are replaced by variants. That is because of the following.

Under these conditions, the CTM experiences change blindness.

Again, the CTM explanation is consistent with the literature on change blindness in humans.,

> [g]iven that change detection requires adequate representation of the pre- and post-change scenes as well as a comparison, any task characteristics that influence the richness of the representation or the tendency to compare representations should affect detection. The semantic importance of the changing object appears to have the biggest influence on the likelihood the subject will attend, and therefore notice, the change.

### 4.4. Illusions

Inattentional blindness and change blindness might be considered examples of illusions.

The CTM is consciously aware by definition of the gists (in chunks) that are broadcast from STM. (Those gists reached STM from LTM. LTM got them directly from sensors via input maps, from other LTM processors through links, and from STM by broadcasts.) The gists are stored in LTM memories for many reasons, one being to supply the processors' high-level stories (section), such as those that occur in dreams.

In CTM, the stream of consciousness is the sequence of gists broadcast from STM (section). Each visual gist at each moment gives the CTM the sense that it sees the entire scene before its eyes, although it sees at most a tiny fraction of the scene. The illusion of the whole has several explanations, the main one being that a multimodal Brainish gist can describe a hugely complex scene, like "I'm standing before a Japanese style garden containing a brook, path, bridge, and trees." Could that gist contain the details of a 12-million-pixel photograph from an iPhone camera, which is what it feels like we are seeing? The illusion of the whole is a consequence of the highly suggestive (succinct) information in a gist. The CTM conjures up the scene in a kind of magic act. Keith Frankish calls this the illusionism theory of consciousness.

### 4.5. Dream Creation

Dreams are the ultimate illusions.

In the CTM, a built-in keeps track of time, habits, day/night, etc. and has internal algorithms to monitor the need for sleep. If and when the Sleep processor determines that sleep is needed, it takes control by raising the intensity of its own chunks enough to get them into STM and to keep other chunks out. This has roughly the same effect as lowering the intensities of chunks from other LTM processors. It also blocks or greatly reduces the intensity of various inputs (eyes and ears), and it blocks signals that activate outputs (such as to limbs). The CTM sleeps. This is the.

The Sleep processor continuously monitors the need for sleep and as that need diminishes, reduces the intensity of its own chunks proportionately. This eventually permits (in chunks) to reach STM. This is the. Finally, when the Sleep processor releases its choke hold on inputs and outputs, the CTM. That is in the CTM.

When CTM is in the dream state, a processor acting as becomes active (that is, starts getting its chunks into STM). The gists in these chunks contain kernels of ideas (typically based on earlier CTM activities, concerns, imaginations). When these chunks are broadcast, all processors, including those that play key roles in the feeling of consciousness, receive those broadcasts and compete to respond. This gives the CTM the same sense of being alive while in the dream state as when it is awake.

The Dream Creator and the other processors take turns interacting back and forth. The conversation—the back-and-forth interaction—between Dream Creator and the gamut of processors is the sequence of gists that constitutes the. This sequence is the.

The dream essentially stitches together this sequence of chunks to produce a dream stream of consciousness (inner movie) that 1) sees, hears, and senses the dream world and 2) affects what appears in that dream world. Such an (interactive) inner movie displays a range of sensory inputs (images, smells, and sounds) and generates a range of actions.

When the CTM is asleep but not dreaming, most processors cannot get their chunks into STM. Exceptions include detectors of especially loud noises and the sleep processor itself. The Sleep processor's chunk in STM blocks most other processors' chunks from reaching STM. By design, it holds an empty gist, so the CTM is not conscious or barely so.

After the CTM leaves the sleep state to enter the dream state, a fraction of LTM processors, such as the Inner Vision processor, can get their chunks into STM. Thus, while dreaming, the CTM is conscious and can experience events vividly.

As discussed earlier (section), key processors, such as those for Inner Speech, inner Vision, Inner Sensations, and Model of the World, play special roles in generating the feeling of consciousness in CTM. These processors play similar roles when CTM is dreaming.

Here are some examples of how processors help with dream creation.

Dreams demonstrate the power of Brainish gists. What CTM sees, hears, feels, and does in a dream is necessarily fabrications by processors that can recall, modify, and submit creations to the competition for STM. These fabrications are realistic because they use the same gists that are generated while awake. Thus, dreams generate the sense of a realistic world even while CTM is completely divorced from external inputs. As a consequence, they can appear so realistic that for CTM,, it may become hard to distinguish dreams from reality.

High level confirmation comes from research [ref. referring to],

Dreams also enable the CTM to test itself in unknown and possibly dangerous situations. In both humans and CTM, dreams can be laboratories for experimenting with various possible solutions.

However, unlike what occurs in waking consciousness, inconsistencies are more likely to occur unnoticed in dreams than while awake since the CTM's "consistency checkers" in its Model of the World processor are not getting input from the environment. Hence, the CTM can fly in its dreams.

Zadra and Stickgold assert that

### 4.6. Free Will

The problem of free will is ancient. It appears in Lucretius (first century BC): "If all movement is always interconnected, the new arising from the old in a determinate order—if the atoms never swerve so as to originate some new movement that will snap the bonds of fate, the everlasting sequence of cause and effect—what is the source of the free will possessed by living things throughout the earth?"

The paradox of free will is captured by Dr. Samuel Johnson's (1709 to 1784) observation: "All theory is against the freedom of the will; all experience is for it."

Stanislas Dehaene bestows a contemporary voice:

We add to Dehaene that computation takes time. To make a decision, CTM evaluates its alternatives in an evaluation that takes time, and during that time, the CTM is free, indeed can feel free, to choose whichever outcome it deems (computes) best.

The TCS perspective thus informs our definition of free will.

This definition incorporates both predictive dynamics (compute the consequences of different courses of action) and resource constraints (time, space, computational power, and information).

For example, consider a CTM that is called on to play a given position in a game of chess. Different processors suggest different moves. The CTM's main chess-playing processor (assuming one exists; otherwise, a processor that has a "hi-level" view of the game) indicates, by broadcast of a chunk in STM, that it recognizes it has a choice of possible moves and that the decision of which move to make merits a careful look at the consequences of each move. At this point, faced with a selection of possible moves but not yet having evaluated the consequences of those moves, the CTM is free to choose whichever move it reckons best within the time constraints.

Will the CTM feel that it has free will?

How important is randomness for this explanation of the feeling of free will? Notice that no quantum physics is required in the CTM for the above explanation. The only randomness is that of the coin-flip neurons in the Up Tree competition and whatever randomness, if any, the processors use in their probabilistic algorithms. It can be shown, moreover, that the above argument for the feeling of free will still applies for a completely deterministic CTM (e.g., one that uses pseudorandomness). It follows—and we expect this will be a source of contention—that even in a completely deterministic world, the CTM will feel it has free will.

## 5. Summary of Methods

We consider consciousness from the perspective of TCS, a nonexperimental area of mathematics. Inspired by Alan Turing's simple yet powerful model of a computer, the TM, and by Bernard Baars', we define a substrate independent computational model of consciousness, the CTM. Formal definitions of conscious content, conscious awareness, and the stream of consciousness in the CTM are followed by arguments that the CTM supports high-level explanations for these and other phenomena associated with consciousness, including the feeling of consciousness. One purpose of our model is to argue these claims. Another is to provide a TCS foundation for understanding consciousness.

and ref. extend this paper with additional figures and frequently asked questions (FAQ).

## Supplementary Material

Supplementary File
