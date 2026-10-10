use gnostral_engine_provider_contract::{
    q013::{select_probe, ProbeIntent, ProbeKind, ProbeQualification},
    QualificationStatus, ServingMode,
};
use gnostral_q013b_local_adapter::{
    guarded_scope, run_fixture, AdapterError, FixtureScenario, Outcome, PINNED_TEST_FIXTURE_SHA256,
};
use sha2::{Digest, Sha256};
use std::{
    path::Path,
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc,
    },
    thread,
    time::Duration,
};

const ENGINE: &str = "64eec222ccefff4cd4c0067bd83348f1d22eebda27d0d857e352ee090cf19723";
const MOE: &str = "db3ce897ccc9e7d9dbf17fe083cae7880a2092aa473b45eba8b77715aa9ca170";
const EMB: &str = "0437e45c94563b09e13cb7a64478fc406947a93cb34a7e05870fc8dcd48e23fd";
const DENSE: &str = "c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8";
const EVIDENCE: &str = "sha256:48241e35df171941e5d80a8f3832a55642de43d96abad04c0a000208e1cd3164";

fn fixture() -> &'static Path {
    Path::new(env!("CARGO_BIN_EXE_q013b-fixture"))
}
fn plan(model: &str, probe: ProbeKind) -> gnostral_engine_provider_contract::q013::ProbePlan {
    select_probe(
        &[ProbeQualification {
            engine_sha256: ENGINE.into(),
            model_sha256: model.into(),
            probe,
            evidence_ref: EVIDENCE.into(),
            profile: "Q012_SEQUENTIAL_FUNCTIONAL".into(),
            status: QualificationStatus::Qualified,
            observed_card_gpu_peak_mib: 2427,
        }],
        &ProbeIntent {
            engine_sha256: ENGINE.into(),
            model_sha256: model.into(),
            probe,
            evidence_ref: EVIDENCE.into(),
            serving_mode: ServingMode::OneShot,
        },
    )
    .expect("Q012 receipt")
}
fn run(
    model: &str,
    probe: ProbeKind,
    scenario: FixtureScenario,
    timeout: u64,
) -> gnostral_q013b_local_adapter::FixtureReceipt {
    run_fixture(
        &plan(model, probe),
        fixture(),
        PINNED_TEST_FIXTURE_SHA256,
        scenario,
        Duration::from_millis(timeout),
        &AtomicBool::new(false),
    )
    .expect("fixture run must produce receipt")
}

fn record(name: &str, r: &gnostral_q013b_local_adapter::FixtureReceipt) {
    println!(
        "Q013B_SAMPLE name={name} outcome={:?} ms={} before_mem={} after_mem={} before_swap={} after_swap={} oom_unchanged={} returned={} gpu_reclaim={} group_killed={}",
        r.outcome, r.duration_ms,
        r.host_before.memory_current_bytes, r.host_after.memory_current_bytes,
        r.host_before.swap_current_bytes, r.host_after.swap_current_bytes,
        r.oom_events_unchanged, r.memory_returned_within_tolerance,
        r.gpu_reclaim_qualified, r.killed_process_group
    );
}

#[test]
fn actual_user_scope_is_bounded_before_any_execution() {
    let sample = guarded_scope().expect("must be in gnu6-lab child scope");
    assert!(sample.cgroup_path.contains("/gnu6-lab.slice/"));
    assert!(sample.cgroup_path.ends_with(".scope"));
}
#[test]
fn fixture_digest_is_pinned_not_supplied_by_caller_authority() {
    let data = std::fs::read(fixture()).unwrap();
    let actual = format!("{:x}", Sha256::digest(data));
    assert_eq!(actual, PINNED_TEST_FIXTURE_SHA256);
    let r = run_fixture(
        &plan(MOE, ProbeKind::MoeExpertSentence),
        fixture(),
        &"0".repeat(64),
        FixtureScenario::Normal,
        Duration::from_millis(500),
        &AtomicBool::new(false),
    );
    assert_eq!(r, Err(AdapterError::InvalidBinaryIdentity));
}
#[test]
fn all_q012_shapes_can_run_their_exact_cpu_only_fixture_probe() {
    for (model, probe, expected) in [
        (DENSE, ProbeKind::DenseSentinel, "Q013B_DENSE=GNOSTRAL"),
        (
            EMB,
            ProbeKind::EmbeddingTriple1024,
            "Q013B_EMBEDDING=3x1024_FINITE",
        ),
        (MOE, ProbeKind::MoeExpertSentence, "Q013B_MOE=CPU_EXPERTS"),
    ] {
        let receipt = run(model, probe, FixtureScenario::Normal, 800);
        record(expected, &receipt);
        assert_eq!(receipt.outcome, Outcome::ProbePass);
        assert_eq!(receipt.observed_semantic_output, expected);
        assert_eq!(receipt.snapshot_sha256, PINNED_TEST_FIXTURE_SHA256);
        assert_eq!(receipt.child_exit_code, Some(0));
        assert!(receipt.oom_events_unchanged);
        assert!(
            receipt.memory_returned_within_tolerance,
            "CPU cgroup memory did not reclaim within observation bound"
        );
        assert!(!receipt.gpu_reclaim_qualified);
    }
}
#[test]
fn plausible_but_incorrect_semantic_output_is_rejected() {
    let receipt = run(
        MOE,
        ProbeKind::MoeExpertSentence,
        FixtureScenario::InvalidOutput,
        800,
    );
    record("invalid_output", &receipt);
    assert_eq!(receipt.outcome, Outcome::SemanticReject);
    assert_eq!(receipt.child_exit_code, Some(0));
    assert!(receipt.oom_events_unchanged);
}
#[test]
fn nonzero_exit_never_becomes_a_semantic_pass() {
    let receipt = run(DENSE, ProbeKind::DenseSentinel, FixtureScenario::Crash, 800);
    record("process_exit_23", &receipt);
    assert_eq!(receipt.outcome, Outcome::ProcessFailed);
    assert_eq!(receipt.child_exit_code, Some(23));
}
#[test]
fn bounded_timeout_terminates_the_specific_group() {
    let receipt = run(
        MOE,
        ProbeKind::MoeExpertSentence,
        FixtureScenario::Hang,
        110,
    );
    record("timeout", &receipt);
    assert_eq!(receipt.outcome, Outcome::TimedOut);
    assert!(receipt.killed_process_group);
    assert!(receipt.duration_ms < 1800);
    assert!(receipt.oom_events_unchanged);
    assert!(receipt.memory_returned_within_tolerance);
}
#[test]
fn cancellation_terminates_the_specific_group() {
    let cancellation = Arc::new(AtomicBool::new(false));
    let switch = Arc::clone(&cancellation);
    let waiter = thread::spawn(move || {
        thread::sleep(Duration::from_millis(80));
        switch.store(true, Ordering::Release);
    });
    let receipt = run_fixture(
        &plan(EMB, ProbeKind::EmbeddingTriple1024),
        fixture(),
        PINNED_TEST_FIXTURE_SHA256,
        FixtureScenario::Hang,
        Duration::from_secs(2),
        &cancellation,
    )
    .unwrap();
    waiter.join().unwrap();
    record("cancel", &receipt);
    assert_eq!(receipt.outcome, Outcome::Cancelled);
    assert!(receipt.killed_process_group);
    assert!(receipt.duration_ms < 1800);
}
#[test]
fn invalid_budgets_rejected_without_spawning() {
    let result = run_fixture(
        &plan(MOE, ProbeKind::MoeExpertSentence),
        fixture(),
        PINNED_TEST_FIXTURE_SHA256,
        FixtureScenario::Normal,
        Duration::from_secs(60),
        &AtomicBool::new(false),
    );
    assert_eq!(result, Err(AdapterError::InvalidBudget));
}
#[test]
fn already_cancelled_run_refuses_to_spawn() {
    let result = run_fixture(
        &plan(MOE, ProbeKind::MoeExpertSentence),
        fixture(),
        PINNED_TEST_FIXTURE_SHA256,
        FixtureScenario::Normal,
        Duration::from_secs(1),
        &AtomicBool::new(true),
    );
    assert!(
        matches!(result, Err(AdapterError::IoError(ref message)) if message.contains("before spawn"))
    );
}
#[test]
fn child_descendant_is_also_killed_by_timeout_group_cleanup() {
    let receipt = run(
        MOE,
        ProbeKind::MoeExpertSentence,
        FixtureScenario::Descendant,
        180,
    );
    record("timeout_descendant", &receipt);
    assert_eq!(receipt.outcome, Outcome::TimedOut);
    assert!(receipt.killed_process_group);
    let pid = receipt
        .observed_semantic_output
        .strip_prefix("DESCENDANT_PID=")
        .expect("descendant receipt")
        .parse::<u32>()
        .unwrap();
    // A reparented zombie may remain briefly: it has already ceased execution.
    let proc = std::path::PathBuf::from(format!("/proc/{pid}/stat"));
    for _ in 0..30 {
        if !proc.exists() {
            break;
        }
        let stat = std::fs::read_to_string(&proc).unwrap_or_default();
        if stat
            .split(')')
            .nth(1)
            .is_some_and(|rest| rest.trim().starts_with('Z'))
        {
            break;
        }
        thread::sleep(Duration::from_millis(10));
    }
    if proc.exists() {
        let stat = std::fs::read_to_string(proc).unwrap_or_default();
        assert!(
            stat.split(')')
                .nth(1)
                .is_some_and(|rest| rest.trim().starts_with('Z')),
            "descendant still running"
        );
    }
}

#[test]
fn forged_executable_named_like_fixture_cannot_reuse_the_pinned_digest() {
    let dir = std::env::temp_dir().join(format!("gnostral-q013b-forged-{}", std::process::id()));
    std::fs::create_dir(&dir).unwrap();
    let forged = dir.join("q013b-fixture");
    std::fs::write(&forged, b"#!/bin/sh\necho Q013B_MOE=CPU_EXPERTS\n").unwrap();
    let result = run_fixture(
        &plan(MOE, ProbeKind::MoeExpertSentence),
        &forged,
        PINNED_TEST_FIXTURE_SHA256,
        FixtureScenario::Normal,
        Duration::from_millis(800),
        &AtomicBool::new(false),
    );
    std::fs::remove_dir_all(dir).unwrap();
    assert_eq!(result, Err(AdapterError::BinaryDigestMismatch));
}
