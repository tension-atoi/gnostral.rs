use gnostral_expert_residency::{CachePlan, ExpertKey, ExpertSize, ResidencyError};

fn key(layer: u32, expert: u32) -> ExpertKey {
    ExpertKey { layer, expert }
}
fn sizes() -> Vec<ExpertSize> {
    vec![
        ExpertSize {
            key: key(0, 0),
            bytes: 16,
        },
        ExpertSize {
            key: key(0, 1),
            bytes: 64,
        },
        ExpertSize {
            key: key(1, 0),
            bytes: 32,
        },
        ExpertSize {
            key: key(1, 1),
            bytes: 16,
        },
    ]
}
#[test]
fn ranked_admission_charges_sizes_and_reaches_later_layers() {
    let plan = CachePlan::build(
        2,
        2,
        &sizes(),
        &[key(0, 0), key(1, 0), key(0, 1), key(1, 1)],
        48,
    )
    .unwrap();
    assert_eq!(plan.planned_bytes(), 48);
    assert_eq!(
        plan.slots()
            .iter()
            .map(|s| (s.key, s.offset, s.bytes))
            .collect::<Vec<_>>(),
        vec![(key(0, 0), 0, 16), (key(1, 0), 16, 32)]
    );
}
#[test]
fn oversized_entry_does_not_block_a_smaller_ranked_expert() {
    let plan = CachePlan::build(2, 2, &sizes(), &[key(0, 1), key(1, 1)], 16).unwrap();
    assert_eq!(plan.slots()[0].key, key(1, 1));
    assert_eq!(plan.planned_bytes(), 16);
}
#[test]
fn zero_budget_is_empty_but_still_validates_profile() {
    assert!(CachePlan::build(2, 2, &sizes(), &[key(0, 0)], 0)
        .unwrap()
        .slots()
        .is_empty());
    assert_eq!(
        CachePlan::build(2, 2, &sizes(), &[key(3, 0)], 0).unwrap_err(),
        ResidencyError::InvalidProfile
    );
}
#[test]
fn malformed_profiles_and_sizes_fail_before_admission() {
    for profile in [vec![key(0, 0), key(0, 0)], vec![key(2, 0)], vec![key(0, 2)]] {
        assert_eq!(
            CachePlan::build(2, 2, &sizes(), &profile, 48).unwrap_err(),
            ResidencyError::InvalidProfile
        );
    }
    assert_eq!(
        CachePlan::build(2, 2, &sizes()[..1], &[key(1, 0)], 48).unwrap_err(),
        ResidencyError::InvalidProfile
    );
    let mut bad = sizes();
    bad.push(bad[0]);
    assert_eq!(
        CachePlan::build(2, 2, &bad, &[], 48).unwrap_err(),
        ResidencyError::InvalidProfile
    );
    bad = sizes();
    bad[0].bytes = 0;
    assert_eq!(
        CachePlan::build(2, 2, &bad, &[], 48).unwrap_err(),
        ResidencyError::InvalidProfile
    );
    assert_eq!(
        CachePlan::build(0, 2, &[], &[], 48).unwrap_err(),
        ResidencyError::InvalidGeometry
    );
}
#[test]
fn total_storage_overflow_is_rejected() {
    let huge = [
        ExpertSize {
            key: key(0, 0),
            bytes: u64::MAX,
        },
        ExpertSize {
            key: key(0, 1),
            bytes: 1,
        },
    ];
    assert_eq!(
        CachePlan::build(1, 2, &huge, &[key(0, 0), key(0, 1)], u64::MAX).unwrap_err(),
        ResidencyError::Overflow
    );
}
