# GNOSTRAL-Q012 — Native inference capabilities / RTX 3070

**Statut final (2026-10-10) : `THREE_FAMILIES_SAME_BINARY_PASS` — qualification fonctionnelle locale de trois familles, sous un même exécutable Rust/CUDA, en processus successifs.** L'essai intermédiaire `PARTIAL_Q012_QUALIFICATION` et sa régression MoE sont conservés ci-dessous comme preuve négative. Ce document distingue systématiquement les capacités upstream, les résultats observés et les fonctionnalités non qualifiées.

## Question expérimentale

Un **même exécutable Rust/CUDA**, dérivé du Q-010 qualifié, peut-il lancer trois familles de modèles dans trois processus locaux successifs : génération dense, génération MoE quantifiée et embeddings ? Il ne s'agit ni d'un moteur multi-modèle résident, ni d'un ordonnanceur, ni d'une API de production.

## Matériel et provenance

- NVIDIA RTX 3070 (8 Gio), 32 Gio de RAM hôte, poste graphique actif.
- Base Git publique : tension-atoi/gnostral.rs, commit f272c2c, worktree Q-012 isolé.
- Binaire Q-010 de contrôle SHA-256 : dc11a9ad45574fea0565768bb877cd828b4ec7ee9eb1177537119959c42984c3.
- Dense : Qwen2.5-Coder-1.5B-Instruct, modèle safetensors déjà en cache.
- MoE : Qwen3-30B-A3B Q2_K, GGUF local en lecture seule, 11 258 610 240 octets.
- Embeddings : Qwen3-Embedding-0.6B officiel, révision 97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3 ; poids de 1 191 586 416 octets, SHA-256 0437e45c94563b09e13cb7a64478fc406947a93cb34a7e05870fc8dcd48e23fd.
- Les fichiers de Qwen3 Embedding restent dans le SSD temporaire du laboratoire ; pas de modèle global ni de service permanent.

## Contrôles historiques Q-010

- Dense : réponse exacte GNOSTRAL via le point d'entrée chat ; pic GPU carte entière 4 959 Mio ; delta GPU après arrêt 0 Mio.
- MoE : réponse via completions ; pic GPU carte entière 2 292 Mio ; delta GPU après arrêt -30 Mio.
- Ces deux essais utilisent exactement le même binaire Q-010. Un seul lancement par famille : test fonctionnel, pas benchmark statistique.

## Chronologie des échecs conservés

1. Les options --host et --port ont d'abord été placées après les sous-commandes ; le parseur CLI les a rejetées.
2. Le chargeur safetensors refuse --max-model-len, pourtant accepté sur la voie GGUF.
3. BGE-small-en-v1.5 en cache est un BertModel, architecture non prise en charge par le chargeur embeddings de cette version.
4. Le premier essai Qwen3 Embedding omettait modules.json et la configuration SentenceTransformers du pooling ; assertion sur les modules.
5. Avec le paquet officiel complet, le modèle d'embeddings est chargé par CUDA, mais l'engine appelle EmbeddingPipeline::cache() alors que son contrat est no_kv_cache=true ; panic à unreachable!().

## Correctif source borné

La modification Q-012 garde seulement les **deux lectures de pipeline.cache().is_hybrid() pendant l'initialisation** par un test préalable de pipeline_metadata.no_kv_cache. Aucun cache fictif, aucune nouvelle autorité, aucun kernel ni algorithme de placement modifié.

Le code de base Q-010 et le candidat Q-012 ne diffèrent que dans mistralrs-core/src/engine/mod.rs au sein des sources du core. Patch : patches/q012/mistralrs-engine-embedding-no-kv-startup.patch. Deux tests structurels indépendants valident sa portée mais ne suffisent pas à qualifier le runtime.

## Critères de sortie établis avant l'exécution (satisfaits dans le run final)

- Recompiler et hacher le candidat CUDA, puis exécuter les **trois familles avec le même nouveau SHA de binaire**.
- Vérifier la réponse dense, une réponse MoE et trois vecteurs finis d'embeddings de dimension attendue, avec contrôle de similarité élémentaire.
- Enregistrer chaque pic VRAM, RSS, l'état du serveur et le delta GPU après arrêt, tolérance ±128 Mio.
- Faire relire les reçus et les sorties par un script distinct du lanceur, sans remplacer les échecs initiaux.
- Interdire l'affirmation de disponibilité à chaud, de co-résidence, de PagedAttention, de qualité générale ou de statut production.

**Le gate de sortie était bloqué avant le run final.** Le binaire corrigé et son audit indépendant ont depuis levé cette interdiction pour la seule qualification fonctionnelle séquentielle.

## English synopsis — historical pre-fix state

**Question:** Can one exact local Rust/CUDA executable handle dense text, quantized MoE and semantic embeddings as three sequential, independently loaded model families on an 8 GiB RTX 3070?

**Already demonstrated on the Q-010 binary:** a Qwen2.5-Coder-1.5B dense text chat response and a Qwen3-30B-A3B Q2_K MoE completion, both with owned-process cleanup and observed GPU memory recovery.

**Negative finding:** the cached BERT-family embedding model is unsupported by this build. A complete Qwen3-Embedding-0.6B checkpoint loads in CUDA but panics at startup because the engine dereferences a cacheless embedding pipeline's deliberately unavailable KV-cache accessor.

**Narrow patch candidate:** short-circuit two hybrid-cache checks when the pipeline metadata already says no KV cache. No artificial cache, placement intervention or new process authority.

**Required red-to-green evidence:** a newly compiled and SHA-256-pinned binary; all three successful fresh-start probes under that same binary; bounded GPU reclaim; independently rehashed model and response receipts; numeric vector similarity recomputed from raw lab-only embeddings.

No claims of concurrent model hosting, production readiness, attention paging or generalized inference quality are authorized by this study.


## Essai intermédiaire conservé — feature de résidence manquante (2026-10-10)

- Build : cargo build --release -p mistralrs-cli --features cuda --locked --offline -j 4 ; FINAL_EXIT=0 après 3 min 51 s, sous MISTRALRS_LAB_FAST_CUDA_BUILD=1. Cette configuration sélectionne un sous-ensemble de kernels CUDA et -O0 pour les kernels paged-attn retenus : **ce n'est pas une qualification CUDA optimisée**.
- Nouveau binaire (262 156 832 octets) : SHA-256 0b08e65267786df03f3469e4ff65ae36c9c06eafba47580689704984fa7a8b12. Les deux gardes no_kv_cache restent présents. Build log : /mnt/hdd/lab/sessions/gnostral-q012-native-inference-capabilities-20261010/q012-fast-cuda-rebuild.log.
- Essai frais sur le même SHA, trois serveurs locaux successifs : /mnt/hdd/lab/sessions/gnostral-q012-native-all-profiles-20261010/.
- Dense PASS_FUNCTIONAL : réponse exacte GNOSTRAL, pic GPU carte entière 4 837 Mio, récupération -19 Mio.
- Embeddings PASS_FUNCTIONAL : trois vecteurs finis de 1 024 dimensions, cosinus apparenté 0,784622 / non apparenté 0,170419, pic GPU 2 552 Mio, récupération +23 Mio. Vecteurs complets réservés à embedding-vectors-private.json.
- MoE Qwen3-30B-A3B Q2_K : poids chargés et API locale démarrée, mais NOT_QUALIFIED (timeout HTTP 240 s). Le moteur rapporte ~0,20 token/s en décodage. Pic GPU 6 772 Mio, RSS du processus ~15 699 Mio, récupération GPU -41 Mio. Aucun PASS MoE sous le nouveau binaire.
- Témoin Q-010 : réponse MoE en 3,096 s dans son scénario historique. Les paramètres de build et l'état machine ne sont pas contrôlés identiques ; la causalité de la régression n'est pas encore établie.
- L'audit indépendant q012_capability_audit.py confirme PARTIAL_Q012_QUALIFICATION ; reçu q012-independent-audit.json dans le dossier de session.
- Les fichiers de source correspondant au fast path CPU compute_host et cpu_expert_matmul_k présentent les mêmes empreintes dans les worktrees Q-010 et Q-012 examinés : aucune preuve de disparition de ce patch.

**Verdict de cet essai intermédiaire uniquement :** `PARTIAL_Q012_QUALIFICATION`. La fermeture définitive figure dans la section suivante. Aucune revendication de co-résidence, qualité généralisée ou production n'en découle.

## Fermeture définitive — trois familles sur le même exécutable

**Binaire final épinglé :** `64eec222ccefff4cd4c0067bd83348f1d22eebda27d0d857e352ee090cf19723` (262 133 264 octets). Build offline Rust/CUDA de laboratoire terminé avec `BUILD_FEATURE_EXIT=0`. Les features réelles de `mistralrs-core` sont `cuda`, `gnostral-expert-residency`, `code-execution` et `utoipa`. Les deux gardes `no_kv_cache` restent présents. La configuration `MISTRALRS_LAB_FAST_CUDA_BUILD=1` ne vaut **pas** qualification d'une distribution optimisée.

| Famille / modèle | Résultat | Pic VRAM carte entière | RSS maximum arbre du serveur | Delta GPU après arrêt |
| --- | --- | ---: | ---: | ---: |
| Dense — Qwen2.5-Coder-1.5B-Instruct | `PASS_FUNCTIONAL` ; `GNOSTRAL` | 5 025 Mio | 3 556 Mio | −42 Mio |
| Embeddings — Qwen3-Embedding-0.6B | `PASS_FUNCTIONAL` ; 3 × 1 024 dimensions | 2 783 Mio | 1 533 Mio | −2 Mio |
| MoE — Qwen3-30B-A3B Q2_K | `PASS_FUNCTIONAL` ; réponse en 2,774 s | 2 427 Mio | 19 282 Mio | 0 Mio |

**Embeddings :** normes finies, cosinus lié = 0,784622 ; sans lien = 0,170419. Ces trois vecteurs sont conservés uniquement dans le dossier privé de test ; seuls les agrégats et les condensats peuvent être publiés. Les serveurs ont été lancés *successivement*, chacun dans son propre processus, puis arrêtés et vérifiés.

**Régression résolue :** le premier Q-012 (`0b08e652…`) avait été compilé sans la feature optionnelle `gnostral-expert-residency` ; les experts MoE n'empruntaient donc pas la voie native, pic GPU = 6 772 Mio, décodage observé ≈ 0,20 token/s, timeout à 240 s. Après la recompilation avec la feature, le journal atteste l'admission de la résidence native et l'initialisation des compteurs ; le MoE répond et sa VRAM retombe à 2 427 Mio. La corrélation avec la feature est établie sur cet A/B ; ce n'est pas un benchmark statistique.

**Audit indépendant final :** `THREE_FAMILIES_SAME_BINARY_PASS`, avec rehash des poids des trois modèles, comparaison des reçus de lancement, vérification du SHA exact, oracles numériques embeddings et contrôles de récupération GPU à ±128 Mio. Cinq échecs de préparation restent dans le dossier historique. Le nouveau garde `harness/experiments/q012_feature_gate.py` requiert à la fois la feature Cargo, le marqueur ELF, deux gardes source et (au gate runtime) les événements de résidence native. **13/13 tests Python** (correctif, gate et reçu public) et **10/10 tests Rust** du crate MIT `crates/gnostral-expert-residency` passent ; l'ancien binaire sans la feature est rejeté (code 2).

**Traçabilité :** dossier privé `/mnt/hdd/lab/sessions/gnostral-q012-feature-recovery-20261010/` ; reçus `build-attestation.json`, `feature-causal-delta.json`, `q012-feature-runtime-witness.json`, `independent-three-family-audit.json`. Résumé public épuré : `evidence/runs/gnostral-q012-native-three-families-20261010.json`.

**Limites de la clôture :** aucune preuve de co-résidence, hot-swap, modèle résident, PagedAttention CPU, qualité large des embeddings, stabilité longue durée, indépendance GPU AMD/Intel ou performance statistique. Le crash Hyprland du 10 octobre est attribué à une action `systemd-oomd` ; son déclencheur processus précis reste indéterminé. Les expériences suivantes doivent utiliser `gnu6-lab-run --exclusive` afin de séparer les charges lourdes de la session graphique.

### Final English synopsis

**Q-012 CLOSED for sequential functional capability:** one exact SHA-256-pinned Rust/CUDA executable started dense, Qwen3 embeddings and quantized MoE as three distinct short-lived servers on the RTX 3070. The initial MoE regression was caused by an omitted compile-time feature; the corrected build passed independent evidence verification. No simultaneous hosting, broad performance or production claim is implied.
