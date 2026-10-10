# Gnostral — Observabilité du placement CPU/GPU au chargement (RTX 3070)

Statut : Q-011 / EVIDENCE_PASS_RESOURCE_AWARE_STARTUP_ONLY. Expérience hors ligne non déployée, sans nouveau plan d autorité.

## Question et résultat

Notre mistral.rs/Candle adapté réagit aux variations de VRAM disponible au CHARGEMENT du modèle. Une réservation CUDA externe de 2048 Mio fait passer les couches GPU de 21–22 (contrôle) à 12–13 (pression), avec réponses structurellement complètes. Cet outil transforme les logs et les reçus en observations structurées avec contrôles d intégrité, sans gérer le GPU.

## Provenance

- Carte NVIDIA RTX 3070 8 Gio ; bureau Hyprland et Chrome actifs ; pression CUDA synthétique sans calcul concurrent.
- GGUF SSD Qwen3-30B-A3B Q2_K : SHA-256 db3ce897ccc9e7d9dbf17fe083cae7880a2092aa473b45eba8b77715aa9ca170.
- Binaire CUDA Q-010 : SHA-256 dc11a9ad45574fea0565768bb877cd828b4ec7ee9eb1177537119959c42984c3.
- Session brute : /mnt/hdd/lab/sessions/gnostral-rtx3070-vram-coexist-20261010.
- Reçu généré : evidence/runs/q011-rtx3070-placement-observation-20261010.json.
- Second audit indépendant : evidence/runs/q011-placement-secondary-audit-20261010.json.
- Six démarrages, trois par condition, douze sorties complètes, 37 fichiers originaux reliés par SHA-256.

## Placement observé (48 couches)

| Condition | Essai 1 | Essai 2 | Essai 3 |
|---|---|---|---|
| Contrôle | 22 GPU / 26 CPU | 21 GPU / 27 CPU | 21 GPU / 27 CPU |
| Réservation 2 Gio | 13 GPU / 35 CPU | 12 GPU / 36 CPU | 13 GPU / 35 CPU |

Les ranges de couches sont validés contigus et cohérents avec les compteurs de résidence native. PagedAttention a été désactivé dans les six sessions CPU/GPU mixtes.

## Performances descriptives (médiane sur trois lancements)

| Mesure | Contrôle | Sous pression |
|---|---:|---:|
| Tâche technique, tok/s | 20.88 | 20.15 |
| Réponse courte, tok/s | 22.40 | 21.50 |
| Pic VRAM totale GPU, Mio | 2346 | 4420 |
| RSS arbre du moteur, Mio | 22155 | 22307 |

Le pic de VRAM sous pression INCLUT la réservation externe de 2048 Mio, et non seulement le moteur.

## Point d attention sur le contexte

Les logs montrent un paramètre d estimation du placement text[max_seq_len: 4096, max_batch_size: 1], alors que le contexte demandé dans les requêtes qualifiées était 1024. Ces deux champs doivent rester distincts : le placement initial ne peut pas être attribué exclusivement au contexte 1024.

## Invariants contrôlés

- Segments du device map sans trou, comptage CPU/GPU cohérent et modèle chargé.
- Témoin de résidence native cohérent avec les plages de couches.
- Réservation GPU présente et mesurée avant chaque lancement sous pression ; processus externe vivant après arrêt du moteur.
- Réserves hôte/VRAM initiales, restitution GPU dans la limite expérimentale, statut du serveur reaped.
- Deux sorties par processus vérifiées par hash ; checklist de six éléments terminée.
- Huit tests unitaires et négatifs, incluant couches discontinues, mismatch de résidence, échec de reclaim et absence de réservation.
- Contre-audit indépendant : six cartes de placement recalculées et 37 fichiers de preuve re-hachés.

## FRONTIÈRE : ce qui n est PAS qualifié

- Aucun rebalancing à chaud sur un modèle chargé et aucune orchestration multi-modèles.
- Aucun KV paginé fonctionnel dans ce chemin CPU/GPU mixte.
- La pression synthétique occupe de la VRAM mais n exécute pas de kernels concurrents ; ne représente pas un jeu ou un éditeur graphique lourd.
- Les sorties varient entre essais ; complétude structurelle ne vaut pas équivalence textuelle ou qualité générale.
- VRAM totale inclut le bureau ; RSS inclut les pages de fichiers partagées ; PSS et transferts PCIe non instrumentés.
- Cet outil produit une preuve APRÈS exécution : il ne décide ni du placement, ni des budgets du bureau, ni des droits des processus.

## Reproduction

Exécuter depuis le dépôt :

    python3 harness/placement/evidence.py --session /mnt/hdd/lab/sessions/gnostral-rtx3070-vram-coexist-20261010 --output /tmp/gnostral-placement-evidence-new.json
    python3 -m unittest discover -s harness/placement -p test_*.py -v

Optionnel : fournir --model et --binary pour recalculer leurs SHA-256 au moment du contrôle. Les sorties existantes ne sont jamais écrasées.

## Statut et coût technique

Résultat conservé en branche isolée ; observabilité hors ligne ajoutée, pas de mutation du runtime. Le passage à des événements structurés émis EN DIRECT dans mistral.rs nécessiterait du code et une compilation CUDA de qualification supplémentaires. Une politique de ressources ou un superviseur exigeraient une décision d autorité distincte.

Aucun merge/push ni publication sur docs.gnu6.live ; aucune mutation de modeld, DB, identité, edge ou secrets.
