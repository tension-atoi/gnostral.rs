# Strata Q-010 — Supprimer les copies d'experts CPU Q2_K et Q3_K

**Statut courant : parité CPU qualifiée ; performance CUDA encore non qualifiée.**

## Question et observation

La comparaison Q-009 à VRAM appariée a observé 9,42 tok/s pour Strata contre 34,54 tok/s pour llama.cpp CPU-MoE sur le poste RTX 3070 8 Gio. Nous explorons une seule intervention causale : supprimer les copies de blocs quantifiés dans la boucle MoE CPU, sans revendication de supériorité produit.

Le chemin original ExpertResidencyRuntime::forward() appelait host.slice_to(expert, CPU) à chaque route non résidente. QTensor::expert_slice_to() finit par QStorage::from_data() et la création de Vec quantifiés via to_vec(). Il copiait donc des poids à chaque sélection d'expert. Le coût exact en ms/token reste à mesurer.

Le chemin x86 repack_x86::select() ne couvre pas Q2K ; c'est une hypothèse indépendante non modifiée ici.

## Correction bornée

- Nouvelle API QTensor::cpu_expert_matmul_k() : emprunt temporaire des blocs Q2K/Q3K à partir de la pile CPU originelle, sans nouvelle Vec de poids.
- Vérification des limites, du type, du buffer, de l'alignement et des dimensions avant vue typée. Le buffer reste vivant sous le prêt de &self pendant la projection synchrone.
- Aucun pointeur ni slice emprunté ne survit à l'appel. Les dtypes non pris en charge conservent le repli historique.
- Gate, up et down empruntent les poids Q2K/Q3K. Le chemin CUDA et la politique de placement ne sont pas modifiés. Aucun cache persistant ajouté.

## Tests et preuves

- Candle : 6/6 tests PASS, comprenant la parité Q2K et Q3K contre des tranches matérialisées.
- mistralrs-core : le test CPU MoE à contributions répétées et Q2K+Q3K passe.
- Deux tentatives de build RED conservées : décalage de symboles pendant l'évolution du prototype ; puis Result<Tensor> non propagé, corrigé.
- Patches incrémentaux Candle et mistralrs avec identités SHA256 et applicabilité vérifiée sur les sources originales.
- Profil dynamique précis des allocations par route encore absent. Ne pas présenter les copies évitées comme un gain de mémoire physique déjà mesuré.

## Protocole CUDA préfigé

Même GGUF SSD Qwen3-30B-A3B Q2_K, contexte 1024, profil expert et réglages F32, six démarrages alternés : trois Strata originale et trois candidate. Deux réponses naturellement complètes, comptage moteur, RSS/processus, pic VRAM carte, préfill et TTFT chaud issu d'une requête distincte.

Critères exploratoires avant lecture des résultats : parité des sorties, libération GPU sans dérive, pas de hausse du pic GPU supérieure à 128 Mio ni RSS supérieure à 512 Mio, et au moins 10 % de gain médian de décodage. N=3 reste descriptif.

**Aucune revendication de performance avant une mesure release CUDA réussie.** Preuves durables : /mnt/hdd/lab/sessions/gnostral-q010-cpu-moe-hotpath-20261010/. Aucune mutation modeld, fusion, push ou publication.

## Qualification CUDA release — A/B répétée (10 octobre 2026)

**Verdict : PASS expérimental pour cette intervention Q2_K/Q3_K, mais aucune revendication de supériorité face à llama.cpp.**

### Historique des deux tentatives

- Première tentative : une paire de lancements a démontré une accélération et une sortie identique, mais le candidat s'est arrêté au gate de restitution GPU (+196 Mio après arrêt pour un plafond de 128 Mio). Résultat brut conservé : NOT_QUALIFIED, sans attribution causale certaine de la dérive au moteur.
- Deuxième tentative : session lab indépendante, quatre points de surveillance ambiante GPU stables avant le lancement ; **seul le chemin de session du contrôleur a changé**, aucune relaxation des gates ni modification du candidat.
- Six processus éphémères (trois baseline, trois candidat), ordre B-C-C-B-B-C, avec un warmup et deux tâches complètes par processus. Le protocole a demandé 128 puis 512 tokens maximum, mais les réponses se sont arrêtées naturellement avant ces plafonds.
- Six paires baseline/candidat ont produit des textes **byte-identiques**, par répétition et budget. À la répétition trois, la réponse de la tâche longue a une longueur différente des deux premières : différence commune aux deux moteurs, non attribuable au patch.

### Débits de décodage mesurés (médianes de 3 exécutions)

| Mesure | Strata original | Candidat Q2_K/Q3_K sans copie | Ratio des médianes |
|---|---:|---:|---:|
| Deux phrases, 52 tokens | 8.90 tok/s | **21.93 tok/s** | **2.47×** |
| Six contrôles, 192–209 tokens | 9.51 tok/s | **20.18 tok/s** | **2.12×** |

Le gain dépasse le seuil ratifié de +10 % sur le débit médian. Il correspond à un code patché exécuté en CUDA release, par rapport au binaire d'origine, sur Qwen3-30B-A3B Q2_K et une RTX 3070 8 Gio ; il ne doit pas être étendu à d'autres modèles, kernels ou plateformes sans qualification.

### Ressources et préfill

| Médiane, trois démarrages par moteur | Original | Candidat | Delta candidat − original |
|---|---:|---:|---:|
| Pic VRAM **carte entière** | 2344 Mio | 2351 Mio | +7 Mio |
| Pic RSS **arbre de processus** | 22094 Mio | 22172 Mio | +79 Mio |
| Préfill de la tâche courte | 3636 ms | 1442 ms | — |
| Premier texte streamé sur requête distincte chaude | 3818 ms | 1422 ms | — |

- Critères de non-régression observés : augmentation des pics VRAM ≤128 Mio ; augmentation des pics RSS ≤512 Mio ; restitution GPU de chaque processus dans ±128 Mio, sur la deuxième série.
- Le pic VRAM concerne **le GPU entier** partagé avec le bureau et reste un relevé échantillonné, non une allocation propre au modèle.
- Le RSS inclut les pages partagées et celles mappées depuis le GGUF ; **PSS non mesuré**. Aucun effet d'économie RAM réelle n'est démontré.
- Le TTFT est mesuré par une autre requête après le prompt initial ; il est susceptible de bénéficier du cache et n'est ni un TTFT froid ni celui de la requête de débit.

### Tests, audits et frontières

- Parité préalable : 6/6 tests Candle Q2_K et Q3_K et 1 test de routage mistralrs-core PASS. Le nouveau chemin emprunte temporairement les blocs quantifiés et laisse les autres dtypes sur le chemin de repli.
- Source de vérité du patch : commit local 67040aa et deux patches incrémentaux Candle/mistralrs archivés avec le reçu de parité.
- Audit indépendant post-run : 6 lancements, 12 réponses, 6 paires byte-identiques ; 29 fichiers de preuve vérifiés, SHA256 modèle et deux binaires recalculés.
- Aucun événement NVRM/Xid détecté dans le journal noyau hôte pendant la fenêtre qualifiée ; ce n'est pas une attestation du pilote par processus.
- **Non réalisé** : profil dynamique par route du volume de copies, mesures PCIe, PSS/RSS privé, revue exhaustive de sûreté du bloc unsafe et long-term soak.
- Comparatif externe antérieur : llama.cpp CPU-MoE upstream atteignait 34,54 tok/s sur une tâche similaire avec VRAM appariée. Notre candidat à 20,18 tok/s ne démontre toujours pas une compétitivité supérieure à upstream ; cette confrontation n'a pas été reréalisée dans ce nouvel A/B.

### Preuves et reproductibilité

- Première tentative : /mnt/hdd/lab/sessions/gnostral-q010-cpu-moe-hotpath-20261010/ (summary.json = NOT_QUALIFIED, retest n'efface rien).
- Tentative qualifiée : /mnt/hdd/lab/sessions/gnostral-q010-cpu-moe-hotpath-retest-20261010/ (frozen-protocol.json, summary.json, 6 logs serveurs, 6 JSON de lancements et 12 fichiers de réponse).
- Audit indépendant : /mnt/hdd/lab/sessions/gnostral-q010-cpu-moe-hotpath-retest-20261010/independent-audit.json.
- Copies Git : evidence/runs/q010-hotpath-ssd-ab-audit-20261010.json, evidence/runs/q010-hotpath-ssd-ab-protocol-20261010.json, evidence/runs/q010-hotpath-first-failed-ab-20261010.json et scripts de reproduction.
- Aucune fusion ou push, aucune mutation modeld, aucun service installé, aucun changement d'autorité stockage/identité/réseau.

**Clôture bornée :** l'optimisation P1 supprime un chemin de copie par route Q2_K/Q3_K et améliore le débit du candidat Q-010 sur cet A/B. P0 (profilage détaillé des coûts), P2 (kernel Q2_K vectorisé) et qualification longue demeurent hors périmètre, sans ouverture automatique.
