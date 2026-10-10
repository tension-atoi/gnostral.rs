use gnostral_expert_residency::{CachePlan, ExpertKey, ExpertSize, ResidencyError, ResidencyTable};
fn key() -> ExpertKey {
    ExpertKey {
        layer: 0,
        expert: 0,
    }
}
fn table() -> ResidencyTable {
    ResidencyTable::new(
        CachePlan::build(
            1,
            2,
            &[ExpertSize {
                key: key(),
                bytes: 16,
            }],
            &[key()],
            16,
        )
        .unwrap(),
    )
}
#[test]
fn upload_publication_waits_for_success_and_rejects_stale_completion() {
    let mut t = table();
    let old = t.begin_upload(key()).unwrap();
    assert!(t.acquire(key()).unwrap().is_none());
    assert_eq!(t.begin_upload(key()).unwrap_err(), ResidencyError::Busy);
    assert_eq!(
        t.complete_upload(old.clone(), false),
        Err(ResidencyError::UploadFailed)
    );
    assert!(t.acquire(key()).unwrap().is_none());
    let retry = t.begin_upload(key()).unwrap();
    assert_eq!(
        t.complete_upload(old, true),
        Err(ResidencyError::InvalidTicket)
    );
    assert!(t.acquire(key()).unwrap().is_none());
    t.complete_upload(retry, true).unwrap();
    let lease = t.acquire(key()).unwrap().unwrap();
    assert_eq!(lease.key(), key());
    assert_eq!(t.close(), Err(ResidencyError::Busy));
    t.release(lease.clone()).unwrap();
    assert_eq!(t.release(lease), Err(ResidencyError::InvalidTicket));
    t.close().unwrap();
    t.close().unwrap();
    assert_eq!(t.acquire(key()), Err(ResidencyError::Closed));
}
#[test]
fn pending_upload_blocks_close_and_foreign_tokens_cannot_publish_or_unpin() {
    let mut a = table();
    let mut b = table();
    let at = a.begin_upload(key()).unwrap();
    let bt = b.begin_upload(key()).unwrap();
    assert_eq!(a.close(), Err(ResidencyError::Busy));
    assert_eq!(
        a.complete_upload(bt.clone(), true),
        Err(ResidencyError::InvalidTicket)
    );
    a.complete_upload(at, true).unwrap();
    b.complete_upload(bt, true).unwrap();
    let al = a.acquire(key()).unwrap().unwrap();
    let bl = b.acquire(key()).unwrap().unwrap();
    assert_eq!(a.release(bl.clone()), Err(ResidencyError::InvalidTicket));
    assert_eq!(a.active_leases(), 1);
    a.release(al).unwrap();
    b.release(bl).unwrap();
    a.close().unwrap();
    b.close().unwrap();
}
#[test]
fn uncached_key_misses_but_invalid_geometry_is_rejected() {
    let mut t = table();
    assert!(t
        .acquire(ExpertKey {
            layer: 0,
            expert: 1
        })
        .unwrap()
        .is_none());
    assert_eq!(
        t.acquire(ExpertKey {
            layer: 1,
            expert: 0
        }),
        Err(ResidencyError::InvalidProfile)
    );
}
