# Pavlovian Conditioning-Induced Hallucinations Result from Overweighting of Perceptual Priors

**Authors:** Albert R. Powers, Christoph Mathys, P. R. Corlett
**Journal:** Science, 2017
**DOI:** 10.1126/science.aan3458
**PMC:** PMC5802347 · **PMID:** 28798131
**License:** PubMed Central Open Access
**Source:** PubMed Central (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5802347/)
**Retrieved:** 2026-05-13

---

## Abstract

Some people hear voices that others do not, but only some of those people seek treatment. Using a Pavlovian learning task, we induced conditioned hallucinations in four groups of people who differed orthogonally in their voice-hearing and treatment-seeking statuses. People who hear voices were significantly more susceptible to the effect. Using functional neuroimaging and computational modeling of perception, we identified processes that differentiated voice-hearers from non-voice-hearers and treatment-seekers from non-treatment-seekers and characterized a brain circuit that mediated the conditioned hallucinations. These data demonstrate the profound and sometimes pathological impact of top-down cognitive processes on perception and may represent an objective means to discern people with a need for treatment from those without.

## Main Text

Perception is not simply the passive reception of inputs. We actively infer the causes of our sensations. These inferences are influenced by our prior experiences. Priors and inputs might be combined according to Bayes' rule. Prediction errors, the mismatch between priors and inputs, contribute to belief updating. Hallucinations (percepts without external stimulus) may arise when strong priors cause a percept in the absence of input. We tested this theory by engendering new priors about auditory stimuli in human observers using Pavlovian conditioning.

Even in healthy individuals, the repeated co-occurrence of visual and auditory stimuli can induce auditory hallucinations. We examined this effect with functional imaging. Some argue that, in patients with psychosis, weak priors lead to aberrant prediction errors, resulting in auditory verbal hallucinations (AVH). Others have observed strong priors in patients, but the effects were not specific to hallucinations. Such inconsistencies may reflect the hierarchical organization of perception; perturbations may impact some levels of the hierarchy and not others. We used computational modeling to infer the strength of participants' hierarchical perceptual beliefs from their behavioral responses during conditioning. Importantly, our model captured how priors are combined with sensory evidence, allowing us to directly test the strong prior hypothesis.

Participants worked to detect a 1-kHz tone occurring concurrently with presentation of a checkerboard visual stimulus. First, we determined individual thresholds for detection and psychometric curves. Then, at the start of conditioning, the tone was presented frequently at threshold, engendering a belief in audio-visual association. This belief was then tested with increasingly frequent sub-threshold and target-absent trials. Conditioned hallucinations occurred when subjects reported tones that were not presented, conditional upon the visual stimulus.

We recruited four groups of subjects: people with a diagnosed psychotic illness who heard voices (P+H+, n=15); those with similar diagnoses who did not hear voices (P+H−, n=14); an active control group who heard daily voices, but had no diagnosed illness (P-H+, n=15; they attributed their experiences metaphysically); and finally, controls without diagnosis or voices (P-H−, n=15).

Groups were matched demographically. Rates of detection of tones at threshold were similar across groups. All groups demonstrated conditioned hallucinations. However, those with daily hallucinations endorsed more conditioned hallucinations than those without, regardless of diagnosis (F=19.59; p=5.82×10). This effect remained after accounting for differences in detection thresholds. Group differences in propensity to report tones were observed only in the No-Tone and 25% Likelihood of Detection conditions (intensity-by-hallucination status F=13.59, p=5.73×10).

Participants also rated their decision confidence by holding down the response button. Participant confidence varied with stimulus intensity ("yes": R=0.39; p=7.46×10; "no": R=0.22; p=9.02 × 10). However, hallucinators were more confident in their conditioned hallucinations than non-hallucinators (F=6.50; p=0.045). Both conditioned hallucinations and confidence correlated with hallucination severity outside of the laboratory.

In order to establish whether conditioned hallucinations involved true percepts, we first identified tone-responsive regions from thresholding runs (peaks at [−60 −20 2] and [62 −28 10]). As observed with elementary hallucinations, activity in tone-responsive regions was greater during conditioned hallucinations compared to correct rejections (t=4.93, p=7.59×10). Electrical stimulation of this region in human patients produces AVH. Taken together, these findings are consistent conditioned hallucinations involving actual perception.

Whole-brain analysis revealed that conditioned hallucinations also engaged anterior insula cortex (AIC), inferior frontal gyrus, head of caudate, anterior cingulate cortex (ACC), auditory cortex, and posterior superior temporal sulcus (STS). A meta-analysis of symptom-capture-based studies examining neural activity of AVH highlighted similar regions. AIC and ACC responses frequently correlate with stimulus salience. However, their activation prior to near-threshold stimulus presentation predicts detection. Caudate is engaged during audiovisual associative learning. Likewise, AIC and ACC are engaged during multisensory integration.

There were no significant between-group differences in brain responses during conditioned hallucinations. However, hallucinators deactivated ACC more (peak at [−16, 54, 14]; cluster-extent thresholded, starting value 0.005, critical k= 99) during correct rejections compared to non-hallucinators.

To further dissect conditioned hallucinations we modeled their underlying computational mechanisms using the Hierarchical Gaussian Filter (HGF). We defined a perceptual model consisting of low-level perceptual beliefs (X1), visual-auditory associations (X2), and the volatility of those associations (X3), as well as learning rates encoding the relationships between levels. Critically, our perceptual model allowed for variability in weighting between sensory evidence and perceptual beliefs (ν). For balanced ν, prior and observation have equal weight; for high ν the prior has more weight than the observation (strong priors); and for low ν the observation has more weight than the prior (weak priors). The resultant posterior probability of a tone is then fed to a separate response model.

Model parameters were fit to behavioral data and the model was optimized using log model evidence and simulations of observed behavior. Mean trajectories of perceptual beliefs were compared across groups. Participants with hallucinations exhibited stronger beliefs at layers 1 and 2 (X1: F=4.8, p=3.89 × 10; X2: F=3.89, p=1.84×10). X3 beliefs evolved less in those with psychosis, who failed to recognize the increasing volatility in contingencies (F=2.11, p=0.018).

Consistent with strong-prior theory, ν was significantly larger in those with hallucinations when compared to their non-hallucinating counterparts, regardless of diagnosis (F=13.96, p=4.45×10). Response model parameters did not differ across the groups.

We regressed model parameters onto task-induced brain responses. The X1 trajectory co-varied with several conditioned hallucination-responsive regions including STS. X3 trajectories, by contrast, covaried with hippocampus/parahippocampal gyrus and medial cerebellum. Parameter estimates from the X1-sensitive STS ([−46, −36, 0], T=2.09, p=0.042) and AIC ([36, 8, −8], T=2.26, p=0.027) were significantly greater in those with hallucinations versus those without. This is consistent with STS conferring auditory expectations that are responsive to incoming visual input. Parameter estimates from the X3-responsive cerebellar vermis ([−2, −52, −16]) were lower in participants with psychosis compared to those without (T=2.05, p=0.045). In the model, subjects with psychosis were significantly less sensitive to the changes in contingency as the task progressed. Psychotic symptoms are often associated with pathological rigidity. Belief updating correlated with responses in the hippocampus and cerebellum. Hippocampal activity correlates with uncertainty in perceptual predictions. The cerebellum has likewise been associated with production and updating of predictive models.

Our X1, X2, and ν findings are consistent with a strong prior theory of hallucinations. The X3 findings in psychotic patients may reflect a strong prior that contingencies are fixed. On the other hand, they could reflect a weak prior on volatility. These beliefs were not associated with hallucinations but rather psychosis more broadly. Under chronic uncertainty, secondary to consistent belief violation, it may be adaptive to resist updating beliefs.

Consistent with previous work applying signal detection theory (SDT) to AVH, we found liberal criteria and low perceptual sensitivity in our H+ groups. A liberal criterion may reflect poor reality monitoring.

However, meta-d' (a metric of participants' meta-cognitive sensitivity) did not differ significantly between groups. SDT is a descriptive tool that does not distinguish aberrant perceptions from decisions. Our modeling work, however, localized group differences to the perceptual model alone. The prior weighting parameter (ν) distinguished H+ from H− groups and also predicted confidence in conditioned hallucinations. Our observations support a strong perceptual prior explanation of hallucinations. They suggest precision treatments for hallucinations, like targeting cholinergically mediated priors and interventions to mollify psychosis more broadly, like cerebellar transcranial magnetic stimulation.

## Supplementary Material

SCID-I = Structured Clinical Interview for DSM-4 Axis I Disorders; CPZ equivs = chlorpromazine equivalents (mgs); WRAT3 = Wide-Range Achievement Test, 3rd edition.

SCID II = Structured Clinical Interview for DSM-IV Axis II Disorders. P values corrected using Holm-Sidak method of correction for multiple comparisons.

AHRS = Auditory Hallucinations Rating Scale. P values corrected using Holm-Sidak method of correction for multiple comparisons.

LSHS-R = Launay-Slade Hallucination Scale (Revised); AH = Auditory Hallucinations subset of LSHS-R; VDD = Vivid Daydreams subset; VT = Vivid Thoughts subset; IT = Intrusive Thoughts subset; VH = Visual Hallucinations subset; PANSS = Positive and Negative Syndrome Scale; BPRS = Brief Psychiatric Rating Scale.

Main effect of hallucination status on conditioned hallucinations, covarying for threshold at baseline.

Clusters listed are significantly more active when participants report the presence of a tone compared to when they report its absence during trials when it is in fact absent. FDR-corrected, p < 0.05. MNI coordinates are given for cluster peak.

Identified by fitting imaging data w/ individual X1 trajectories. Cluster-extent thresholded with starting value of p = 0.01, k= 100.

Identified by fitting imaging data w/ individual X1 trajectories. Cluster-extent thresholded with starting value of p = 0.05, k= 406.

Conditioned hallucination likelihood plotted as a function of detection threshold for each of the four groups, with lines of best fit for each group. No correlations meet statistical significance. Dotted line represents grand mean of detection threshold. Main effect of hallucination status, taking into account baseline differences in threshold, F=13.49; p=5.17×10.

Sensitivity (red) and specificity (black), plotted as a function of cutoff value for individual probability of reporting conditioned hallucinations. Participants in each group, illustrated as meeting (full-color dots) or not meeting (faded dots) the test criterion for experiencing hallucinations.

Correlations between two measures of clinical hallucination severity (PANSS P3 Score and Auditory Hallucination Rating Scale Score) and probability of answering "Yes" on no-tone trials and confidence in doing so.

Three iterations were tested in their abilities to recreate individual-subject behavioral data: 1) standard HGF implementation but including the ability for individual trajectories to vary freely in their starting points; 2) adding the parameter Nu, which allows for individual variability in the weighting between sensory evidence and perceptual beliefs during perceptual inference; 3) adjusting the priors on Nu to allow for a more flexible influence of the parameter on the overall model. Simulated responses were then compared to observed behavioral responses, comparing the proportion of simulated responses that were identical to observed responses, individual phi coefficients measuring overall statistical similarity between observed and simulated responses, and proportion of "yes" responses on each of the experimental conditions.

Four models (including the unaltered custom-created Conditioned Hallucinations version of the HGF) were entered into Bayesian model comparison based upon their log model evidence. The final model (including parameter Nu with adjusted priors) was the clear winner.

Type 1 D-Prime analysis revealed significant main effects of psychosis (F= 7.17; p < 0.01) and hallucination status (F= 29.18; p < 0.001). Bias (criterion) estimates revealed a significant main effect of hallucination status (F= 5.25; p < 0.001). No group differences in Meta-D-Prime or metacognitive efficiency were found. Error bars represent 95% high-density (confidence) intervals (HDI) from the posterior estimates of metacognitive efficiency from hierarchical Meta-D-Prime estimation.

Although confidence measures were not used to fit HGF model parameters, model parameter Nu (prior weighting) was found to vary directly with the degree of confidence participants had in reporting conditioned hallucinations.
