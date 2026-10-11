# Meta-review — EFC Model Family Reconciliation

**Verdict ID:** `deleg_7f3e9a1c-meta-verdict`  
**Manuscript:** `docs/papers/efc/EFC_Model_Family_Reconciliation/EFC_Model_Family_Reconciliation.tex`  
**Basis:** manuscript, round-1 review files, round-2 advocate/attacker reviews, six named package indexes, preregistration files, status register, and reproduction artifact. Manuscript was not edited.

## Executive verdict

Manuskriptet er holdbart som provenance-/statusreconciliation, ikke som fysisk lukket modellreconciliation. De fire pinnede faktaene er låst: (1) DOI `10.6084/m9.figshare.31940469` er pakken `Energy-Flow_Cosmology_Empirical_Validation_of_the_EFC_Screening_Model_Track_1`, ikke dangling; (2) `Gamma_B`-formen i 31942821 er en kildeinkonsistens; (3) `related_packages` er ikke tomme for 31941465 og 31878760, slik at manuskriptets kategoriske påstand er feil; (4) `axis_e_sparc_rar.md` er `INVALID until fixed` fordi tre `a_0`-kandidater sirkulerer. Agentkonsensus er ikke brukt som evidens.

De sentrale endringene er presiseringer, ikke omskriving av status: dimensjons-/normaliseringsgapet og Gamma-rolle-identifikasjonen må synliggjøres; «orthogonal/independent» må nedgraderes til descriptive axes; B må inn i tabellen; `alpha`-symbolene må skilles; `a_0` må beskrives som importert/ufrosset kalibreringsspørsmål; sirenformelen må beskrives som en klasse-observabel, ikke EFC-unik; og `related_packages`-setningen må korrigeres.

## Status vocabulary

Alle `claim_status`-felt i `verdict.json` bruker ledger-vokabularet `proposed`, `declared_derived` eller `declared_companion_upgrade`. Status betyr ikke empirisk støtte; `declared_derived` betyr deklarert avledning under modellens egne premisser, og `declared_companion_upgrade` betyr deklarert relasjon, med `supersession_status=not_established`.

## Claim-for-claim vurdering

### C01 — Reconciliationen er ikke en ny empirisk test, fysisk bekreftelse, supersession-påstand eller uavhengig fagfellevurdering; ingen ny fit utføres.

**1. Eksakt påstand:** Reconciliationen er ikke en ny empirisk test, fysisk bekreftelse, supersession-påstand eller uavhengig fagfellevurdering; ingen ny fit utføres.  

**2. Premisser:** Manuskriptets uttrykkelige scope må leses som avgrensning, og kildepakker/ledger må ikke forveksles med nye resultater.  

**3. Derivasjon gyldig?:** Ja som dokument-scope; dette er ikke en fysisk derivasjon.  

**4. Empirisk testet?:** Nei; scopepåstanden er verifisert dokument-/metadata-messig, ikke empirisk.  

**5. Støttende evidens:** EFC_Model_Family_Reconciliation.tex:83-91,215-225; reproduction.json:46-55; alle seks index.json med null fit-felt der relevant.  

**6. Konflikterende evidens:** Ingen kilde viser at manuskriptet faktisk utfører en fit; reviewerinnvendinger om manglende fysisk lukking gjelder ikke denne smale scopepåstanden.  

**7. Enklere forklaring:** En ren provenance-/statusinventering forklarer observasjonen uten å kreve en lukket samlet teori.  

**8. Falsifikator:** Motbevis hvis manuskriptet eller build-artefaktet inneholdt en ny, reproduserbar fit eller hevdet fysisk bekreftelse.  

**9. Uløst:** Om alle workflow- og AI-review-påstander skal omfattes av samme scope; dette endrer ikke status.  

**10. Claim-status:** `proposed`  


### C02 — De seks Table-1-slugene og DOI-parene er de tilsiktede kildemappingene.

**1. Eksakt påstand:** De seks Table-1-slugene og DOI-parene er de tilsiktede kildemappingene.  

**2. Premisser:** Repo-stier må finnes og hver index.json må ha samme DOI/figshare_url som manuskriptet.  

**3. Derivasjon gyldig?:** Ja, identitetsmappingen er direkte kontrollert.  

**4. Empirisk testet?:** Ikke empirisk; kilde-/repo-testet.  

**5. Støttende evidens:** claim_map.json:12-18; provenance_review.json:4-29; seks index.json; manuskript:104-123.  

**6. Konflikterende evidens:** Ingen feil i de seks primære mappingene. DOI 31940469 er en separat, kildeverifisert informs-relasjon og ikke en dangling Table-1-mapping.  

**7. Enklere forklaring:** En enkel fil-/DOI-identitetskontroll forklarer funnet.  

**8. Falsifikator:** Falsifiseres av manglende sti eller mismatchende DOI i en autoritativ index.json.  

**9. Uløst:** Figshare-versjonshistorikk er ikke vurdert for denne identitetsclaimen.  

**10. Claim-status:** `proposed`  


### C03 — Gamma er dS/drho, og sigma_s=Gamma(rho) dot-rho følger ved kjerneregelen.

**1. Eksakt påstand:** Gamma er dS/drho, og sigma_s=Gamma(rho) dot-rho følger ved kjerneregelen.  

**2. Premisser:** Felles definisjon av S, rho-enheter, differensierbar S(rho), og en felles normalisering for alle former.  

**3. Derivasjon gyldig?:** Kjerneregelen er gyldig per eksplisitt definert modell; felles bruk for A/B/C er ikke etablert fordi Gamma_B mangler prefaktor/dimensjonskonvensjon, og kildene viser også Gamma i Box phi=Gamma(ρ).  

**4. Empirisk testet?:** Nei. Ingen fit eller måling av denne identifikasjonen.  

**5. Støttende evidens:** Manuskript:127-131; Derivation.../index.json:24-27,49-55; relativistic-action.../index.json:147-182,205-217.  

**6. Konflikterende evidens:** FORM-001/002 og attacker_review:15-31 viser manglende identifikasjon mellom dS/drho, Box phi-kilde og relativistisk Gamma.  

**7. Enklere forklaring:** Separate package-roller eller separate entropikonvensjoner kan forklare samme symbol uten én felles fysisk respons.  

**8. Falsifikator:** Falsifiseres/avklares av en eksplisitt dimensjonskonsistent mapping eller ved at autoritativ kilde viser at objektene faktisk er identiske med samme enheter.  

**9. Uløst:** Felles S, enheter, normalisering og mapping Gamma→feltligning→observabel mangler.  

**10. Claim-status:** `proposed`  


### C04 — Korpuset inneholder tre distinkte deklarerte former Gamma_A, Gamma_B og Gamma_C.

**1. Eksakt påstand:** Korpuset inneholder tre distinkte deklarerte former Gamma_A, Gamma_B og Gamma_C.  

**2. Premisser:** Formene må gjengis kildefidel og skilles fra påstanden om at de allerede er dimensjonelt forenlige eller empirisk selektert.  

**3. Derivasjon gyldig?:** Ja som transkripsjon av deklarerte uttrykk; nei som påstand om samme normaliserte fysiske observable.  

**4. Empirisk testet?:** Nei. Korpusformen er dokumentert, ikke testet.  

**5. Støttende evidens:** Manuskript:133-141; 31942821/index.json:49-55,108; 31942800/index.json:41-47; form_status_register.json:10-45.  

**6. Konflikterende evidens:** 31942821 er internt inkonsistent (A i main_finding/core equation, B i key_result); Gamma_B har dimensjon sqrt([rho]) uten prefaktor.  

**7. Enklere forklaring:** Dokument-/metadata-bifurkasjon, eller separate modellroller, forklarer tre uttrykk uten felles responsfunksjon.  

**8. Falsifikator:** En autoritativ kilde som kollapser formene til samme reparameterisering, eller dimensjonsanalyse som ikke krever normalisering.  

**9. Uløst:** Normering av B og felles felt-/observabelmapping er uløst.  

**10. Claim-status:** `proposed`  


### C05 — A er proposed; B er declared_derived, non-saturating og ikke superseded; C er declared_companion_upgrade/untested og ikke superseded.

**1. Eksakt påstand:** A er proposed; B er declared_derived, non-saturating og ikke superseded; C er declared_companion_upgrade/untested og ikke superseded.  

**2. Premisser:** Form_status_register.json er autoritativt statusregister; statusord skal ikke leses som empirisk bevis.  

**3. Derivasjon gyldig?:** Ja som statusmapping; ingen fysisk derivasjon følger av etikettene.  

**4. Empirisk testet?:** Nei. Registeret sier tested=false/åpne forhold.  

**5. Støttende evidens:** Manuskript:143-149; form_status_register.json:10-45; claim_map:C05.  

**6. Konflikterende evidens:** Ingen kilde støtter at statusetikettene innebærer empirisk seleksjon, ekvivalens eller forbedring.  

**7. Enklere forklaring:** Dette er metadata-livssyklus, ikke en fysisk modenhetskjede.  

**8. Falsifikator:** Falsifiseres av register-/manuskriptmismatch; fysisk supersession krever separat test.  

**9. Uløst:** Hvorvidt B+ faktisk bør kalles upgrade eller bare proposed companion form må author-gates.  

**10. Claim-status:** `declared_companion_upgrade`  


### C06 — A/B/C utgjør en shape bifurcation, ikke en empirisk A→B→C-modenhetskjede; B→B+ er bare deklarert relasjon.

**1. Eksakt påstand:** A/B/C utgjør en shape bifurcation, ikke en empirisk A→B→C-modenhetskjede; B→B+ er bare deklarert relasjon.  

**2. Premisser:** Bifurcation må uttrykkelig være en reconciliation-label, ikke et teorem; supersession er not_established.  

**3. Derivasjon gyldig?:** Gyldig som forsiktig provenance-syntese; ikke som fysisk modellteorem uten felles dynamikk.  

**4. Empirisk testet?:** Nei. Ingen felles likelihood eller seleksjon.  

**5. Støttende evidens:** Manuskript:151-153; form_status_register.json:28-45; falsification.md:11-24,26-34.  

**6. Konflikterende evidens:** Kildekonflikten og manglende normalisering/feltmapping gjør fysisk bifurkasjon uavklart; B→B+ kan ikke innebære forbedring.  

**7. Enklere forklaring:** Metadata-/provenance-bifurkasjon forklarer alt som faktisk er etablert.  

**8. Falsifikator:** Falsifiseres som corpusclaim av autoritativ kilde; fysisk påstand falsifiseres/seleksjoneres av låst A/B/C-sammenligning.  

**9. Uløst:** Regime, felles observabel, normalisering og beslutningsregel mangler.  

**10. Claim-status:** `proposed`  


### C07 — Det finnes to ortogonale modellfamilieakser: E-eksponent alpha=1 vs 1/2 og Gamma-density-shape.

**1. Eksakt påstand:** Det finnes to ortogonale modellfamilieakser: E-eksponent alpha=1 vs 1/2 og Gamma-density-shape.  

**2. Premisser:** Det kreves felles modellrom, viste kombinasjoner/faktorisering og identifiserbarhet for fysisk ortogonalitet.  

**3. Derivasjon gyldig?:** Kun som organisatorisk taksonomi; formell ortogonalitet/uavhengighet er ikke vist, og B mangler i tabellen.  

**4. Empirisk testet?:** Nei. Ingen joint derivation, metric eller joint fit.  

**5. Støttende evidens:** Manuskript:155-179; 31941465/index.json:53-71; 31942800/index.json:41-51; claim_map:C07.  

**6. Konflikterende evidens:** FORM-003/004; attacker_review:73-85; provenance_review:123-133.  

**7. Enklere forklaring:** To dokumentkategorier med ulik kilde-/observabelrolle kan organiseres som descriptive axes uten fysisk uavhengighet.  

**8. Falsifikator:** En felles modellmatrise eller joint likelihood som viser kobling/ikke-identifiserbarhet falsifiserer ortogonalitetslesningen.  

**9. Uløst:** Alle kombinasjoner, Alpha-symbol, B/B+ plassering og identifikasjon er uløst.  

**10. Claim-status:** `proposed`  


### C08 — E proportional sqrt(g) følger fra den minimale tre-term gradient-coupled grid action.

**1. Eksakt påstand:** E proportional sqrt(g) følger fra den minimale tre-term gradient-coupled grid action.  

**2. Premisser:** Grid-actionens egne antakelser og regimet alpha*g >> kappa_0 må gjelde; dette må ikke utvides automatisk til relativistisk EFT eller makroskopisk gravitasjonsrespons.  

**3. Derivasjon gyldig?:** Ja som deklarert intern grid-regimeskalering; nei som full mikro-til-makro/EFC-feltderivasjon.  

**4. Empirisk testet?:** Nei; index har null delta_chi2/significance og no new fit.  

**5. Støttende evidens:** Manuskript:160; 31941465/index.json:28-75,74-88; reproduction.json:46-49.  

**6. Konflikterende evidens:** Attacker_review:35-52; 31878760/index.json:114-121,187-192 beskriver kinematisk/ufullstendig bro; EFT-index:235-249 sier BE-formen er postulated as effective relation og feil fortegn i klassisk handling.  

**7. Enklere forklaring:** En lokal dispersjons-/grid-teorem kan eksistere uten at den definerer samme felt som EFT-responsen.  

**8. Falsifikator:** Falsifiseres for den konkrete implementationen av en låst robust KC1-test; bred E-teorem krever eksplisitt mapping.  

**9. Uløst:** Felles handling, variabelmapping, macro response og prefactor/normalisering.  

**10. Claim-status:** `declared_derived`  


### C09 — KC1: hvis lineær mu foretrekkes og sqrt-formen ekskluderes ved >=5 sigma under robust bias-kontroll, falsifiseres E proportional sqrt(g).

**1. Eksakt påstand:** KC1: hvis lineær mu foretrekkes og sqrt-formen ekskluderes ved >=5 sigma under robust bias-kontroll, falsifiseres E proportional sqrt(g).  

**2. Premisser:** Frosset a0, sample, likelihood, nuisance/systematics, threshold og eksplisitt E→mu-implikasjon.  

**3. Derivasjon gyldig?:** Kriteriet er logisk betinget; implikasjonen fra mu-preferanse til hele E-teoremet er ikke demonstrert.  

**4. Empirisk testet?:** Nei; bare proposed/no fit.  

**5. Støttende evidens:** Manuskript:181-190; 31941465/index.json:102-107; form_status_register.json:67-73; falsification.md:36-46.  

**6. Konflikterende evidens:** Kilden sier delta_chi2/significance null og no new fit; claim om mulig executed-but-unrecorded er for sterk.  

**7. Enklere forklaring:** En framtidig fenomenologisk modelltest kan falsifisere mu-implementasjonen uten å falsifisere alle E proportional sqrt(g)-modeller.  

**8. Falsifikator:** Forhåndsdefinert robust >=5 sigma eksklusjon av sqrt-formen etter alle låser; uten mapping gjelder den kun konkret mu-implementasjon.  

**9. Uløst:** Hva “robust/bias-controlled/diverse” betyr og om E→mu er entydig.  

**10. Claim-status:** `proposed`  


### C10 — Grid-actionens interne PDF favoriserer square-root operator og kaller linear operator too steep.

**1. Eksakt påstand:** Grid-actionens interne PDF favoriserer square-root operator og kaller linear operator too steep.  

**2. Premisser:** PDF-en må verifiseres direkte; index alene støtter ikke ordrett PDF-sitat.  

**3. Derivasjon gyldig?:** Ikke avgjort i requested index-scope; kan være korrekt intern retning, men ikke etablert her som kildeclaim.  

**4. Empirisk testet?:** Nei som empirisk påstand.  

**5. Støttende evidens:** Manuskript:188; claim_map:C10; advocate_review:93-103.  

**6. Konflikterende evidens:** Kun index-støtte for generell operator uniqueness, ikke sitatet; ingen ekstern fit.  

**7. Enklere forklaring:** En intern kildeargumentasjon uten data forklarer retningen.  

**8. Falsifikator:** Direkte PDF-kontroll eller motsatt PDF-tekst.  

**9. Uløst:** Full PDF/proveniens av sitatet.  

**10. Claim-status:** `proposed`  


### C11 — KC1s >=5 sigma SPARC comparison har åpen provenance; ingen executed result promoteres.

**1. Eksakt påstand:** KC1s >=5 sigma SPARC comparison har åpen provenance; ingen executed result promoteres.  

**2. Premisser:** Index null-felt/no-fit må leses bokstavelig; manuscript skal ikke holde executed fit som like plausibelt.  

**3. Derivasjon gyldig?:** Ja for åpen provenance-status; Level-3-alternativet i manuskriptet bør snevres.  

**4. Empirisk testet?:** Nei.  

**5. Støttende evidens:** Manuskript:190; 31941465/index.json:74-88; form_status_register.json:67-73.  

**6. Konflikterende evidens:** provenance_review.json:71-81 sier executed-but-unrecorded ikke støttes og kolliderer med no new fit.  

**7. Enklere forklaring:** Ekstern, unreproduced claim eller metadatafeil forklarer manglende tall; ingen evidence for executed fit.  

**8. Falsifikator:** Kilde som leverer identifiserbar fit/proveniens, eller som avviser at noen fit eksisterte.  

**9. Uløst:** Author må velge “unexecuted/unsubstantiated or external reference” og fjerne executed alternative.  

**10. Claim-status:** `proposed`  


### C12 — Ledger-vokabularet skiller proposed, declared derived og declared companion upgrade fra prose descriptors.

**1. Eksakt påstand:** Ledger-vokabularet skiller proposed, declared derived og declared companion upgrade fra prose descriptors.  

**2. Premisser:** Registerets claim maturity er autoritativt; tekstlige ord skal ikke endre feltstatus.  

**3. Derivasjon gyldig?:** Ja, dette er schema-/statusdefinisjon.  

**4. Empirisk testet?:** Nei; ikke empirisk.  

**5. Støttende evidens:** Manuskript:192-204; form_status_register.json:6-9.  

**6. Konflikterende evidens:** Ingen substansiell konflikt.  

**7. Enklere forklaring:** Et eksplisitt statusregister forklarer dette uten fysisk evidens.  

**8. Falsifikator:** Register og manuskript måtte ha ulik vokabulardefinisjon.  

**9. Uløst:** Ingen vesentlig uløst claim.  

**10. Claim-status:** `proposed`  


### C13 — To preregisterte discriminator-proposals er foreslått og ikke utført: SPARC/RAR for E og GW/EM for propagation; Gamma har ingen egen prereg.

**1. Eksakt påstand:** To preregisterte discriminator-proposals er foreslått og ikke utført: SPARC/RAR for E og GW/EM for propagation; Gamma har ingen egen prereg.  

**2. Premisser:** De separate prereg-filer og pinned fakta gjelder; teststatus må ikke blandes med source index.  

**3. Derivasjon gyldig?:** Ja som statusbeskrivelse; testene er ikke valid/frozen.  

**4. Empirisk testet?:** Nei.  

**5. Støttende evidens:** Manuskript:206-213; axis_e_sparc_rar.md:1-5,44-67; axis_dl_gw_em.md:1-5,19-34,85-91; test_spec.json:45-64,110-129.  

**6. Konflikterende evidens:** Ingen konflikt med pinned facts; round-1 objection that tests are executed/valid is rejected.  

**7. Enklere forklaring:** Dette er testprotokoll-intensjon med eksplisitte blockers, ikke resultat.  

**8. Falsifikator:** Falsifiseres av en valid, executed prereg med frozen fields eller utført fit.  

**9. Uløst:** Final sample, likelihood, nuisance og exact decision rules remain open.  

**10. Claim-status:** `proposed`  


### C14 — Foreløpig normative a0=1.2e-10 m s^-2; canonical value is author-gated, several candidates circulate, SPARC test invalid until one is fixed.

**1. Eksakt påstand:** Foreløpig normative a0=1.2e-10 m s^-2; canonical value is author-gated, several candidates circulate, SPARC test invalid until one is fixed.  

**2. Premisser:** Pinned prereg facts; distinguish MOND/SPARC empirical input from EFC output and a0,eff.  

**3. Derivasjon gyldig?:** Statusclaim is valid; calling the number an EFC prediction is not.  

**4. Empirisk testet?:** Nei. Prereg invalid; no fit.  

**5. Støttende evidens:** Manuskript:211; axis_e_sparc_rar.md:44-67; 31878760/index.json:41-43,143-146; 31878334/index.json:57-60,162-166.  

**6. Konflikterende evidens:** attacker_review:56-69 and physics_review:38-44 show imported calibration and rescaling issue.  

**7. Enklere forklaring:** MOND-calibrated a0 or fitted nuisance can reproduce RAR without EFC-specific derivation.  

**8. Falsifikator:** Author-frozen protocol plus same-normalization comparison against MOND and explicit EFC derivation; absence of independent derivation falsifies “predicted” wording, not the test idea.  

**9. Uløst:** Origin of a0, C, exponent scale, M/L and cross-model fair comparison.  

**10. Claim-status:** `proposed`  


### C15 — Relativistic-action package supplies dL^GW/dL^EM=sqrt(F(phi0)/F(phiz)), F=1+alpha phi, as future standard-siren discriminator.

**1. Eksakt påstand:** Relativistic-action package supplies dL^GW/dL^EM=sqrt(F(phi0)/F(phiz)), F=1+alpha phi, as future standard-siren discriminator.  

**2. Premisser:** Action-level derivation, F>0, field normalization/background and frozen parameters are required.  

**3. Derivasjon gyldig?:** Formula is source-traceable candidate; not a closed numeric EFC prediction.  

**4. Empirisk testet?:** Nei; no dataset/fit.  

**5. Støttende evidens:** Manuskript:213; 31876324/index.json:28-35,58-70,281-301; axis_dl_gw_em.md:19-34.  

**6. Konflikterende evidens:** Formula tests propagation sector/class, not uniquely EFC; alternatives and degeneracies remain.  

**7. Enklere forklaring:** Generic running-Planck-mass modified gravity or systematics can yield same ratio.  

**8. Falsifikator:** Frozen EFC curve rejected by hierarchical siren likelihood with GR and generic modified-gravity alternatives.  

**9. Uløst:** Field solution, normalization, positivity, waveform/lensing/host systematics and parameters.  

**10. Claim-status:** `proposed`  


### C16 — GW/EM siren discriminator is paradigm-resistant because it does not depend on Lambda-CDM prior; alpha and phi0 not frozen.

**1. Eksakt påstand:** GW/EM siren discriminator is paradigm-resistant because it does not depend on Lambda-CDM prior; alpha and phi0 not frozen.  

**2. Premisser:** Only narrow null-comparison sense can be meant; no uniqueness against modified-gravity alternatives.  

**3. Derivasjon gyldig?:** Mechanism is plausible; “single paradigm-resistant” is unsupported overclaim.  

**4. Empirisk testet?:** Nei.  

**5. Støttende evidens:** Manuskript:213; 31876324/index.json:281-301; axis_dl_gw_em.md:85-91.  

**6. Konflikterende evidens:** PHYS-SIREN-001/002, alternatives:58-82, attacker:89-99.  

**7. Enklere forklaring:** A generic tensor-friction observable plus systematics explains any nonzero mismatch.  

**8. Falsifikator:** Unique EFC attribution would require pre-frozen curve, common likelihood and alternatives; otherwise only concrete curve can be falsified.  

**9. Uløst:** Alpha/phi normalization/evolution, GR limit, nuisance and model class.  

**10. Claim-status:** `proposed`  


### C17 — Ingen nye fits, selections, independent validations eller physical falsifications utføres/hevdes.

**1. Eksakt påstand:** Ingen nye fits, selections, independent validations eller physical falsifications utføres/hevdes.  

**2. Premisser:** Scope lines and null metadata are accurate.  

**3. Derivasjon gyldig?:** Ja som scope/status claim.  

**4. Empirisk testet?:** Nei; it is a negative procedural claim, not an empirical result.  

**5. Støttende evidens:** Manuskript:215-225; six index metadata; reproduction.json:46-55.  

**6. Konflikterende evidens:** No evidence of a new fit; review requirements for future validation do not conflict.  

**7. Enklere forklaring:** A provenance reconciliation with explicit non-testing section.  

**8. Falsifikator:** Build or manuscript showing an executed selection/fit/validation.  

**9. Uløst:** None material beyond workflow audit scope.  

**10. Claim-status:** `proposed`  


### C18 — Repo metadata for 31941465 corrected while published Figshare record retains old wording; version bump required.

**1. Eksakt påstand:** Repo metadata for 31941465 corrected while published Figshare record retains old wording; version bump required.  

**2. Premisser:** Requires direct Figshare/version-history evidence beyond six indexes.  

**3. Derivasjon gyldig?:** Ikke verifisert in requested evidence; no derivation.  

**4. Empirisk testet?:** Nei.  

**5. Støttende evidens:** Manuskript:228-237 only; claim_map:C18.  

**6. Konflikterende evidens:** Six-index review cannot establish prior public record.  

**7. Enklere forklaring:** A draft limitation note can be true, but may also be unverified repository state.  

**8. Falsifikator:** Direct Figshare/version-history readback.  

**9. Uløst:** External publication state and whether bump has occurred.  

**10. Claim-status:** `proposed`  


### C19 — Package is machine-readable/reproducible by construction with generators/build/checksum, but byte-for-byte reproducibility not achieved.

**1. Eksakt påstand:** Package is machine-readable/reproducible by construction with generators/build/checksum, but byte-for-byte reproducibility not achieved.  

**2. Premisser:** Named scripts/files must exist and execution must support each component.  

**3. Derivasjon gyldig?:** Partly: buildability and non-determinism verified; “by construction/full stack/CI determinism” needs broader inspection.  

**4. Empirisk testet?:** No physical test; workflow executed.  

**5. Støttende evidens:** reproduction.json:2-37; manuscript:240-243; build log.  

**6. Konflikterende evidens:** Overfull hbox/float warnings; determinism false; broad CI/generator claim not fully established by reproduction artifact.  

**7. Enklere forklaring:** A successful build plus differing hashes explains non-byte reproducibility, not complete reproducibility.  

**8. Falsifikator:** Missing named artifact or deterministic CI failure would falsify corresponding subclaim.  

**9. Uløst:** Full stack/CI and exact workflow claim.  

**10. Claim-status:** `proposed`  


### C20 — Manuscript is draft, DOI-PENDING, no Figshare record, no authorized repository merge.

**1. Eksakt påstand:** Manuscript is draft, DOI-PENDING, no Figshare record, no authorized repository merge.  

**2. Premisser:** Internal manuscript status is current and not contradicted by an external publication.  

**3. Derivasjon gyldig?:** Ja as internal document-state claim.  

**4. Empirisk testet?:** Nei.  

**5. Støttende evidens:** Manuskript:34-36,244,249-250.  

**6. Konflikterende evidens:** No requested source contradicts it.  

**7. Enklere forklaring:** A draft status line is sufficient for this internal claim.  

**8. Falsifikator:** External DOI/Figshare/merge readback contradicting the text.  

**9. Uløst:** Current external publication state not independently queried.  

**10. Claim-status:** `proposed`  


## Funn fra runde 1 og 2

Fordeling: `accepted` 15, `already-covered` 25, `author-gate` 10, `rejected` 4.

`accepted` betyr at manuskriptet må endres med teksten under. `author-gate` betyr at funnet er reelt og blokkerer en senere fysisk/testmessig bruk, men skal ikke fremstilles som allerede løst. `rejected` betyr at funnet bygger på en feil lesning eller låst kildekonflikt. `already-covered` betyr at manuskriptet allerede har korrekt status eller at et duplikat er dekket av et annet funn.

### FORM-001 — formal_review.md

- **Alvorlighet/type:** `high` / dimensional consistency
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Etter ligningene: "Here \rho and \rho_{\mathrm{crit}} are treated as dimensional densities. \Gamma_A and \Gamma_C are dimensionless; the declared \Gamma_B expression has residual dimension \sqrt{[\rho]} and is not used as a common normalized response until a source-supplied prefactor/reference scale is specified."`
- **Begrunnelse:** Matematisk korrekt under stated density dimensions; pinned source inconsistency must remain visible, not silently repaired.

### FORM-002 — formal_review.md

- **Alvorlighet/type:** `high` / chain-rule scope
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Erstatt "with the associated entropy production rate $\sigma_s = \Gamma(\rho)\,\dot{\rho}$ (chain rule)." med "For any explicitly defined, differentiable model-specific entropy function $S_i(\rho)$, $\dot S_i=(\mathrm dS_i/\mathrm d\rho)\dot\rho$; a common $\sigma_s$ convention across A/B/C is not assumed until units and normalizations are fixed."`
- **Begrunnelse:** Kjerneregelen er gyldig per modell, men felles S/units er ikke etablert.

### FORM-003 — formal_review.md

- **Alvorlighet/type:** `medium-high` / axes/table
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Erstatt i linje 158 "two orthogonal model-family axes" med "two presently separate descriptive model-family axes"; erstatt linje 164 "These two axes are independent" med "These choices are organized separately here; physical independence is not demonstrated"; oppdater tabellen til å liste $\Gamma_A$, $\Gamma_B$, og $\Gamma_C$ og marker realiserte versus hypotetiske kombinasjoner.`
- **Begrunnelse:** Orthogonalitet er ikke matematisk etablert, og B er utelatt.

### FORM-004 — formal_review.md

- **Alvorlighet/type:** `medium` / wording ambiguity
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Erstatt "each with a discriminant that a future test must select between" med "each is intended to admit a future discriminator; only the E-axis has a current preregistration proposal, while no $\Gamma$-shape discriminator is preregistered."`
- **Begrunnelse:** Fjerner logisk spenning mellom future discriminator og no preregistered Gamma test.

### FORM-005 — formal_review.md

- **Alvorlighet/type:** `medium` / notation/identification
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Erstatt $\alpha$ i $E\propto g^{\alpha}$ med $\alpha_E$, og skriv $F(\phi)=1+\beta_F\phi$; angi eksplisitt $[\beta_F\phi]=1$ og felt-normalisering.`
- **Begrunnelse:** Samme symbol skaper falsk kobling mellom E-aksen og siren-sektoren.

### FORM-006 — formal_review.md

- **Alvorlighet/type:** `medium` / B-to-B+ semantics
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Erstatt "declared companion upgrade" i den forklarende prose med "declared companion form/replacement claim" og legg til: "No implication $B\Rightarrow B^+$ or $B^+\Rightarrow\neg B$, improved fit, or dimensional consistency is established; supersession_status remains not_established."`
- **Begrunnelse:** Upgrade er statusvokabular, ikke fysisk forbedring.

### PHYS-GAMMA-001 — physics_review.md

- **Alvorlighet/type:** `critical` / missing GR/ΛCDM limit
- **Disposition:** **author-gate**
- **Påkrevd tekstendring:** `Behold claim som status/provenance og legg til: "No GR/\Lambda CDM limit, $G_{\rm eff}$, slip, $c_T$, background, growth, or perturbation mapping is established here; these are author-gated requirements for a physical model reconciliation."`
- **Begrunnelse:** Reell blokkering for fysisk lukking, men utenfor manuskriptets eksplisitte reconciliation-scope.

### PHYS-GAMMA-002 — physics_review.md

- **Alvorlighet/type:** `high` / dimensional consistency
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** FORM-001/002 aksepterer og presiserer samme funn; ikke dupliser.

### PHYS-GAMMA-003 — physics_review.md

- **Alvorlighet/type:** `high` / asymptotic regularity
- **Disposition:** **author-gate**
- **Påkrevd tekstendring:** `Legg i limitations: "The high-density growth of the declared $\Gamma_B$ form is not assigned a physical cutoff or stability/regularity domain here; no form is physically selected."`
- **Begrunnelse:** B non-saturation/divergence trenger cutoff og stabilitetsanalyse før fysisk bruk.

### PHYS-A0-001 — physics_review.md

- **Alvorlighet/type:** `high` / imported calibration
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Erstatt "normative screening scale" med "a provisional value recorded in source packages, not an EFC-derived prediction"; legg til: "The preregistration lists $1.2\times10^{-10}$, $6.5\times10^{-10}$, and $a_{0,\mathrm{eff}}=C^2a_0$; it is INVALID until exactly one is author-frozen. The origin of the frozen value must be labelled MOND/SPARC input, EFC output, or nuisance calibration."`
- **Begrunnelse:** Pinned prereg says invalid until fixed; attacker correctly identifies imported calibration risk.

### PHYS-A0-002 — physics_review.md

- **Alvorlighet/type:** `high` / RAR mapping
- **Disposition:** **author-gate**
- **Påkrevd tekstendring:** `Legg til i test-gate: "The SPARC/RAR proposal is a proxy for the E exponent, not a direct test of $\Gamma(\rho)$; the manuscript does not derive $g_{\rm obs}(g_{\rm bar})$, the exponent argument, or both Newtonian/deep-MOND limits."`
- **Begrunnelse:** Needed for valid future test, not an executed result.

### PHYS-SIREN-001 — physics_review.md

- **Alvorlighet/type:** `critical` / siren specificity
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Erstatt "This is the single paradigm-resistant discriminator in the set" med "This is a candidate propagation-sector discriminator; $d_L^{\rm GW}\ne d_L^{\rm EM}$ is not EFC-specific and does not by itself distinguish EFC from GR systematics or other modified-gravity friction models."`
- **Begrunnelse:** Pinned attacker point: class observable, not unique EFC discriminator.

### PHYS-SIREN-002 — physics_review.md

- **Alvorlighet/type:** `high` / field normalization
- **Disposition:** **author-gate**
- **Påkrevd tekstendring:** `Legg til: "The expression requires a declared field normalization and dimensionless, positive $F(\phi)=1+\beta_F\phi$ domain; $\beta_F$, $\phi_0$, and $\phi(z)$ are not frozen here."`
- **Begrunnelse:** Necessary before numeric prediction.

### PHYS-DEG-001 — physics_review.md

- **Alvorlighet/type:** `high` / siren degeneracy
- **Disposition:** **author-gate**
- **Påkrevd tekstendring:** `Legg til i future-test gate: "The siren ratio identifies endpoint combinations and is degenerate with field normalization and waveform/lensing/host/EM-distance systematics; a joint hierarchical likelihood is required."`
- **Begrunnelse:** Valid future-analysis requirement.

### PHYS-DEG-002 — physics_review.md

- **Alvorlighet/type:** `high` / SPARC degeneracy
- **Disposition:** **author-gate**
- **Påkrevd tekstendring:** `Legg til i Axis-1 gate: "Lock or predeclare M/L, distance, inclination, gas model, covariance, and holdout treatment for both exponent forms; locking $a_0$ alone is insufficient."`
- **Begrunnelse:** Directly supported by prereg/test_spec.

### PHYS-DEG-003 — physics_review.md

- **Alvorlighet/type:** `medium-high` / cosmology degeneracy
- **Disposition:** **author-gate**
- **Påkrevd tekstendring:** `Legg til i future validation scope: "A physical background claim requires explicit mapping and comparison against $\Lambda$CDM with shared nuisance/prior structure; no such fit is performed here."`
- **Begrunnelse:** Future model-comparison gate.

### FALS-001 — falsification.md

- **Alvorlighet/type:** `major` / Gamma bifurcation falsifiability
- **Disposition:** **author-gate**
- **Påkrevd tekstendring:** `Legg til: "The term shape bifurcation is a corpus/reconciliation label; a physical bifurcation requires a locked common likelihood, regime, normalization, and decision rule."`
- **Begrunnelse:** Makes physical interpretation testable without upgrading it.

### FALS-002 — falsification.md

- **Alvorlighet/type:** `major` / B-to-B+ test
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Supersession not established is already explicit at manuscript:148,153,204 and register:35-45.

### FALS-003 — falsification.md

- **Alvorlighet/type:** `major` / KC1 operationalization
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Erstatt Level-3 "either (a) an executed fit... or (b)..." med "The source metadata supports no new fit performed; the claimed $\ge5\sigma$ exclusion is therefore unexecuted or externally referenced and remains unsubstantiated until an author supplies provenance."`
- **Begrunnelse:** No-fit is pinned source fact; executed-but-unrecorded cannot remain equally live.

### FALS-004 — falsification.md

- **Alvorlighet/type:** `major` / axis orthogonality test
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** FORM-003 and C07 status cover unproved physical independence.

### FALS-005 — falsification.md

- **Alvorlighet/type:** `major` / SPARC prereg test
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** PHYS-A0-001/002 and C13/C14 retain test as proposed/invalid until freeze.

### FALS-006 — falsification.md

- **Alvorlighet/type:** `major` / siren prereg test
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** PHYS-SIREN-001/002 and C15/C16 retain candidate status and alternatives.

### ALT-001 — alternatives.md

- **Alvorlighet/type:** `major` / RAR alternatives
- **Disposition:** **author-gate**
- **Påkrevd tekstendring:** `Legg til: "RAR is not EFC-specific: future validation must compare EFC with MOND and a baryonic $\Lambda$CDM baseline under identical locked nuisance/holdout protocol; no such comparison is performed here."`
- **Begrunnelse:** MOND and ΛCDM can reproduce observable; future comparison needed.

### ALT-002 — alternatives.md

- **Alvorlighet/type:** `info` / S8 scope
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Alternatives review confirms manuscript contains no S8 result; no change to this reconciliation.

### ALT-003 — alternatives.md

- **Alvorlighet/type:** `major` / siren alternatives
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** PHYS-SIREN-001 plus required common likelihood covers class-observable objection.

### PROV-001 — provenance_review.json

- **Alvorlighet/type:** `info` / table slug support
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Supports C02; no text change.

### PROV-002 — provenance_review.json

- **Alvorlighet/type:** `info` / table DOI support
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Supports C02; no text change.

### PROV-003 — provenance_review.json

- **Alvorlighet/type:** `info` / Gamma statuses support
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Supports C05; no text change.

### PROV-004 — provenance_review.json

- **Alvorlighet/type:** `info` / A/B divergence support
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Supports C04/C06; no text change.

### PROV-005 — provenance_review.json

- **Alvorlighet/type:** `info` / KC1 null provenance support
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Supports C09/C11; no text change.

### PROV-006 — provenance_review.json

- **Alvorlighet/type:** `medium` / KC1 executed-fit alternative
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Samme eksakte endring som FALS-003: "The source metadata supports no new fit performed; the claimed $\ge5\sigma$ exclusion is therefore unexecuted or externally referenced and remains unsubstantiated until an author supplies provenance."`
- **Begrunnelse:** Confirms attacker/provenance finding.

### PROV-007 — provenance_review.json

- **Alvorlighet/type:** `info` / sqrt-g derivation support
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Supports C08 only as declared derivation, not empirical result.

### PROV-008 — provenance_review.json

- **Alvorlighet/type:** `info` / siren formula support
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Supports C15 formula provenance.

### PROV-009 — provenance_review.json

- **Alvorlighet/type:** `high` / prereg conflict
- **Disposition:** **rejected**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Pinned facts explicitly establish the named prereg axis_e_sparc_rar.md as INVALID until a0 is fixed and proposed; the conflicting sealed-package finding is outside the locked adjudication basis and does not overturn the actual referenced file.

### PROV-010 — provenance_review.json

- **Alvorlighet/type:** `medium` / orthogonal axes synthesis
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** FORM-003/C07 accepts only descriptive synthesis and rejects formal independence.

### PROV-011 — provenance_review.json

- **Alvorlighet/type:** `low` / paradigm-resistant wording
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Samme tekstendring som PHYS-SIREN-001: "This is a candidate propagation-sector discriminator; $d_L^{\rm GW}\ne d_L^{\rm EM}$ is not EFC-specific..."`
- **Begrunnelse:** Source supports formula, not comparative adjective.

### REPRO-001 — reproduction.json

- **Alvorlighet/type:** `info` / buildability
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Supports C19; no text change.

### REPRO-002 — reproduction.json

- **Alvorlighet/type:** `low` / build warnings
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Legg til i reproducibility section: "The build currently completes with Overfull hbox and float-placement warnings; warning-free layout is not claimed."`
- **Begrunnelse:** Concrete verified artifact issue.

### REPRO-003 — reproduction.json

- **Alvorlighet/type:** `info` / checksum record
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Supports C19.

### REPRO-004 — reproduction.json

- **Alvorlighet/type:** `info` / byte reproducibility
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Manuskriptet already states non-byte-determinism; reproduction confirms it.

### REPRO-005 — reproduction.json

- **Alvorlighet/type:** `medium` / Gamma provenance
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** C04-C06 and pinned source conflict cover it.

### REPRO-006 — reproduction.json

- **Alvorlighet/type:** `info` / KC1 provenance
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** C09/C11 and FALS-003 cover it.

### REPRO-007 — reproduction.json

- **Alvorlighet/type:** `info` / siren provenance
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** C15/C16 cover it.

### R2-ATT-001 — attacker_review.md

- **Alvorlighet/type:** `critical` / Gamma role identification
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Legg til: "The reconciliation does not establish that $\mathrm dS/\mathrm d\rho$, the source in $\Box\phi=\Gamma(\rho)$, and the relativistic-action $\Gamma$ are the same normalized physical object; this mapping is author-gated."`
- **Begrunnelse:** Central attacker finding is valid and stronger than merely A/B inconsistency.

### R2-ATT-002 — attacker_review.md

- **Alvorlighet/type:** `major` / grid-EFT bridge
- **Disposition:** **author-gate**
- **Påkrevd tekstendring:** `Erstatt "The square-root form derives from the gradient-coupled grid action" med "The grid-action package declares a square-root scaling in its stated regime; a bridge to the relativistic EFT and its macroscopic response is not established here."`
- **Begrunnelse:** Source conflict and missing bridge are real; do not erase declared_derived status, narrow wording.

### R2-ATT-003 — attacker_review.md

- **Alvorlighet/type:** `major` / a0 imported calibration
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Samme PHYS-A0-001 text: label $a_0$ as input/output/calibration and state prereg invalid until one value is frozen; do not call it parameter-free EFC prediction.`
- **Begrunnelse:** Pinned prereg and source indexes support this.

### R2-ATT-004 — attacker_review.md

- **Alvorlighet/type:** `major` / orthogonal axes
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** FORM-003/004 provide exact wording and table fix.

### R2-ATT-005 — attacker_review.md

- **Alvorlighet/type:** `critical` / siren class observable
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** PHYS-SIREN-001/PROV-011 provide exact narrowing; alternatives requirement is author-gate.

### R2-ADV-001 — advocate_review.md

- **Alvorlighet/type:** `info` / scope defense
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** C01/C17 and manuscript:215-225 explicitly cover no confirmation.

### R2-ADV-002 — advocate_review.md

- **Alvorlighet/type:** `info` / KC1 threshold not result
- **Disposition:** **rejected**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Correctly rejects straw-man reading; manuscript already says conditional/not reported result and metadata says no fit.

### R2-ADV-003 — advocate_review.md

- **Alvorlighet/type:** `info` / prereg proposed
- **Disposition:** **rejected**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Pinned prereg facts confirm advocate conclusion; no change required.

### R2-ADV-004 — advocate_review.md

- **Alvorlighet/type:** `medium` / siren minor wording
- **Disposition:** **already-covered**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Exact narrowing accepted under PHYS-SIREN-001.

### R2-ADV-005 — advocate_review.md

- **Alvorlighet/type:** `medium` / related_packages claim
- **Disposition:** **accepted**
- **Påkrevd tekstendring:** `Erstatt "their related packages fields are empty" med "related_packages fields are heterogeneous: four of six are empty, while 31941465 records builds_on/informs relations and 31878760 records a companion relation; the ledger remains the authoritative status graph."`
- **Begrunnelse:** Pinned fact says literal manuscript claim is false; 31940469 is not dangling.

### R2-ADV-006 — advocate_review.md

- **Alvorlighet/type:** `info` / 31940469 relation
- **Disposition:** **rejected**
- **Påkrevd tekstendring:** —
- **Begrunnelse:** Pinned fact says 31940469 is the informing package; reject dangling-DOI criticism, while retain related_packages wording correction.

## Konsolidert author-gate for neste versjon

1. Lever dimensjonskonsistent felles mapping `Gamma -> feltligning -> observabel`, eller kall A/B/C separate package forms; ikke bruk `Gamma_B` i felles likelihood før prefaktor/normalisering er levert.
2. Lever modellmatrise/joint-identifiability dersom fysisk uavhengighet av aksene skal hevdes; ellers bruk descriptive-axis wording.
3. Frys `a_0`, M/L, sample, likelihood, nuisance og holdout før SPARC-test; rapporter om `a_0` er MOND-input, EFC-output eller kalibrering.
4. For sirener: frys felt-normalisering, `alpha`/`phi_0`/`phi(z)`, positivitet og systematics; sammenlign GR og minst én generisk modified-gravity friction-modell.
5. Behandle KC1 som foreslått, ikke utført: source metadata sier `no new fit performed`; en påstått `>=5 sigma`-fit trenger separat provenance.

## Recommendation

Lag en wording/status-revisjon med de aksepterte endringene før publisering. Ikke oppgrader noen claim til empirisk validert, superseded eller falsified. Fysisk lukking, alternativkontroll og preregistreringsfrys er author-gates og krever separat arbeid.
