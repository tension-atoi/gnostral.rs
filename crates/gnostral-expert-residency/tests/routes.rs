use gnostral_expert_residency::{
    partition_routes, CachePlan, ExpertKey, ExpertSize, ResidencyError, ResidencyTable, Route,
};
fn key(e: u32) -> ExpertKey {
    ExpertKey {
        layer: 0,
        expert: e,
    }
}
fn table() -> ResidencyTable {
    let mut t = ResidencyTable::new(
        CachePlan::build(
            1,
            3,
            &[ExpertSize {
                key: key(0),
                bytes: 16,
            }],
            &[key(0)],
            16,
        )
        .unwrap(),
    );
    let u = t.begin_upload(key(0)).unwrap();
    t.complete_upload(u, true).unwrap();
    t
}
fn route(e: u32, ordinal: usize, weight: f32) -> Route {
    Route {
        token: 0,
        ordinal,
        key: key(e),
        weight,
    }
}
#[test]
fn partition_preserves_repeated_contributions_and_route_order() {
    let mut t = table();
    let input = vec![route(0, 0, 0.25), route(2, 1, 0.5), route(0, 2, 0.125)];
    let split = partition_routes(&mut t, &input).unwrap();
    assert_eq!(
        split.gpu.iter().map(|(r, _)| r.clone()).collect::<Vec<_>>(),
        vec![input[0].clone(), input[2].clone()]
    );
    assert_eq!(split.cpu, vec![input[1].clone()]);
    assert_eq!(t.active_leases(), 2);
    for (_, lease) in split.gpu {
        t.release(lease).unwrap();
    }
    t.close().unwrap();
}
#[test]
fn invalid_later_route_does_not_leak_pins() {
    for input in [
        vec![route(0, 0, 1.0), route(9, 1, 1.0)],
        vec![route(0, 0, 1.0), route(2, 1, f32::NAN)],
        vec![route(0, 0, 1.0), route(2, 1, f32::INFINITY)],
        vec![route(0, 0, 1.0), route(2, 0, 1.0)],
    ] {
        let mut t = table();
        assert_eq!(
            partition_routes(&mut t, &input).unwrap_err(),
            ResidencyError::InvalidProfile
        );
        assert_eq!(t.active_leases(), 0);
        t.close().unwrap();
    }
}
