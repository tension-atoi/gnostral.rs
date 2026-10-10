//! Q013-B disposable subprocess qualification. This crate is NOT an inference adapter.
//! It accepts only the compiled q013b-fixture and fixed protocol arguments.
use gnostral_engine_provider_contract::q013::{ProbeKind, ProbePlan};
use sha2::{Digest, Sha256};
use std::{
    fs::{self, File, OpenOptions},
    io::{self, Read},
    os::unix::{
        fs::{DirBuilderExt, OpenOptionsExt, PermissionsExt},
        process::CommandExt,
    },
    path::{Path, PathBuf},
    process::{Command, Stdio},
    sync::atomic::{AtomicBool, Ordering},
    thread,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

const GIB: u64 = 1024 * 1024 * 1024;
/// Local test binary attested once; recompile requires a deliberate repin.
pub const PINNED_TEST_FIXTURE_SHA256: &str =
    "60dee3e056d442ac779edb6f799f2d2926c6916e636752de4183b2bf12955c40";
const MAX_OUTPUT: u64 = 64 * 1024;
const RETURN_TOLERANCE: u64 = 32 * 1024 * 1024;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FixtureScenario {
    Normal,
    InvalidOutput,
    Hang,
    Descendant,
    Crash,
}
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Outcome {
    ProbePass,
    SemanticReject,
    TimedOut,
    Cancelled,
    ProcessFailed,
}
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum AdapterError {
    Unisolated,
    InsufficientHeadroom,
    InvalidBudget,
    InvalidBinaryIdentity,
    BinaryDigestMismatch,
    UnsupportedExecutable,
    IoError(String),
}
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HostSample {
    pub cgroup_path: String,
    pub memory_current_bytes: u64,
    pub swap_current_bytes: u64,
    pub oom_kill_events: u64,
}
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FixtureReceipt {
    pub outcome: Outcome,
    pub snapshot_sha256: String,
    pub expected_semantic_output: String,
    pub observed_semantic_output: String,
    pub stdout_bytes: u64,
    pub duration_ms: u128,
    pub child_exit_code: Option<i32>,
    pub killed_process_group: bool,
    pub host_before: HostSample,
    pub host_after: HostSample,
    pub memory_returned_within_tolerance: bool,
    pub oom_events_unchanged: bool,
    /// This cannot prove NVIDIA VRAM reclaim or genuine inference readiness.
    pub gpu_reclaim_qualified: bool,
}
fn digest(path: &Path) -> Result<String, AdapterError> {
    let mut h = Sha256::new();
    let mut f = File::open(path).map_err(|e| AdapterError::IoError(e.to_string()))?;
    let mut buf = [0_u8; 64 * 1024];
    loop {
        let n = f
            .read(&mut buf)
            .map_err(|e| AdapterError::IoError(e.to_string()))?;
        if n == 0 {
            break;
        }
        h.update(&buf[..n]);
    }
    Ok(format!("{:x}", h.finalize()))
}
fn read_number(path: &Path) -> Result<u64, AdapterError> {
    fs::read_to_string(path)
        .map_err(|_| AdapterError::Unisolated)?
        .trim()
        .parse::<u64>()
        .map_err(|_| AdapterError::InvalidBudget)
}
fn event_count(path: &Path) -> Result<u64, AdapterError> {
    let text = fs::read_to_string(path).map_err(|_| AdapterError::Unisolated)?;
    text.lines()
        .find_map(|line| {
            let mut x = line.split_whitespace();
            if x.next() == Some("oom_kill") {
                x.next()?.parse::<u64>().ok()
            } else {
                None
            }
        })
        .ok_or(AdapterError::Unisolated)
}
fn available_kib(name: &str) -> Result<u64, AdapterError> {
    let text = fs::read_to_string("/proc/meminfo").map_err(|_| AdapterError::Unisolated)?;
    text.lines()
        .find_map(|line| {
            let (key, value) = line.split_once(':')?;
            if key == name {
                value.split_whitespace().next()?.parse::<u64>().ok()
            } else {
                None
            }
        })
        .ok_or(AdapterError::Unisolated)
}
fn sample(path: &Path, logical: &str) -> Result<HostSample, AdapterError> {
    Ok(HostSample {
        cgroup_path: logical.to_string(),
        memory_current_bytes: read_number(&path.join("memory.current"))?,
        swap_current_bytes: read_number(&path.join("memory.swap.current"))?,
        oom_kill_events: event_count(&path.join("memory.events"))?,
    })
}
/// Verifies the actual Linux cgroup controls, not merely a claimed environment variable.
pub fn guarded_scope() -> Result<HostSample, AdapterError> {
    let data = fs::read_to_string("/proc/self/cgroup").map_err(|_| AdapterError::Unisolated)?;
    let logical = data
        .lines()
        .find_map(|line| line.strip_prefix("0::"))
        .ok_or(AdapterError::Unisolated)?;
    if !logical.contains("/gnu6-lab.slice/") || !logical.ends_with(".scope") {
        return Err(AdapterError::Unisolated);
    }
    let root = Path::new("/sys/fs/cgroup");
    let scope = root.join(logical.trim_start_matches('/'));
    let parent = scope.parent().ok_or(AdapterError::Unisolated)?;
    if parent.file_name().and_then(|x| x.to_str()) != Some("gnu6-lab.slice") {
        return Err(AdapterError::Unisolated);
    }
    if read_number(&scope.join("memory.max"))? > 21 * GIB
        || read_number(&scope.join("memory.swap.max"))? > 2 * GIB
        || read_number(&scope.join("memory.oom.group"))? != 1
        || read_number(&parent.join("memory.high"))? > 18 * GIB
        || read_number(&parent.join("memory.max"))? > 22 * GIB
        || read_number(&parent.join("memory.swap.max"))? > 2 * GIB
    {
        return Err(AdapterError::InvalidBudget);
    }
    if available_kib("MemAvailable")? < 1024 * 1024 || available_kib("SwapFree")? < 1024 * 1024 {
        return Err(AdapterError::InsufficientHeadroom);
    }
    sample(&scope, logical)
}
struct PrivateSnapshot {
    dir: PathBuf,
    executable: PathBuf,
}
impl Drop for PrivateSnapshot {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.dir);
    }
}
fn snapshot(source: &Path, expected_sha: &str) -> Result<PrivateSnapshot, AdapterError> {
    if expected_sha != PINNED_TEST_FIXTURE_SHA256 {
        return Err(AdapterError::InvalidBinaryIdentity);
    }
    if source.file_name().and_then(|x| x.to_str()) != Some("q013b-fixture") {
        return Err(AdapterError::UnsupportedExecutable);
    }
    let base = std::env::temp_dir();
    let mut output = None;
    for seq in 0..32 {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map_err(|e| AdapterError::IoError(e.to_string()))?
            .as_nanos();
        let dir = base.join(format!(
            "gnostral-q013b-{}-{}-{seq}",
            std::process::id(),
            now
        ));
        if fs::DirBuilder::new().mode(0o700).create(&dir).is_ok() {
            output = Some(dir);
            break;
        }
    }
    let dir = output
        .ok_or_else(|| AdapterError::IoError("private snapshot directory unavailable".into()))?;
    let state = PrivateSnapshot {
        executable: dir.join("q013b-fixture"),
        dir,
    };
    let result = (|| -> Result<(), AdapterError> {
        let mut src = File::open(source).map_err(|e| AdapterError::IoError(e.to_string()))?;
        let mut dst = OpenOptions::new()
            .create_new(true)
            .write(true)
            .mode(0o600)
            .open(&state.executable)
            .map_err(|e| AdapterError::IoError(e.to_string()))?;
        io::copy(&mut src, &mut dst).map_err(|e| AdapterError::IoError(e.to_string()))?;
        dst.sync_all()
            .map_err(|e| AdapterError::IoError(e.to_string()))?;
        fs::set_permissions(&state.executable, fs::Permissions::from_mode(0o500))
            .map_err(|e| AdapterError::IoError(e.to_string()))?;
        if digest(&state.executable)? != expected_sha {
            return Err(AdapterError::BinaryDigestMismatch);
        }
        Ok(())
    })();
    result.map(|()| state)
}
fn expected_for(probe: ProbeKind) -> (&'static str, &'static str) {
    match probe {
        ProbeKind::DenseSentinel => ("--dense", "Q013B_DENSE=GNOSTRAL"),
        ProbeKind::EmbeddingTriple1024 => ("--embedding", "Q013B_EMBEDDING=3x1024_FINITE"),
        ProbeKind::MoeExpertSentence => ("--moe", "Q013B_MOE=CPU_EXPERTS"),
    }
}
fn group_kill(pid: u32) -> Result<(), AdapterError> {
    // Negative PID sends SIGKILL only to this dedicated process group.
    let rc = unsafe { libc::kill(-(pid as i32), libc::SIGKILL) };
    if rc == 0 {
        return Ok(());
    }
    let e = io::Error::last_os_error();
    if e.raw_os_error() == Some(libc::ESRCH) {
        return Ok(());
    }
    Err(AdapterError::IoError(format!(
        "process group kill failed: {e}"
    )))
}

/// This accepts a Q013-A probe plan only as a test shape. The child is a tiny fixture
/// with a DIFFERENT binary SHA than the real Q-012 engine. Never treat its output
/// as a new Q-012 semantic readiness receipt.
pub fn run_fixture(
    plan: &ProbePlan,
    executable: &Path,
    fixture_sha256: &str,
    scenario: FixtureScenario,
    timeout: Duration,
    cancel: &AtomicBool,
) -> Result<FixtureReceipt, AdapterError> {
    let baseline = guarded_scope()?;
    if timeout < Duration::from_millis(30) || timeout > Duration::from_secs(3) {
        return Err(AdapterError::InvalidBudget);
    }
    if cancel.load(Ordering::Acquire) {
        return Err(AdapterError::IoError("cancelled before spawn".into()));
    }
    let private = snapshot(executable, fixture_sha256)?;
    let (normal_arg, expected) = expected_for(plan.binding().probe);
    let arg = match scenario {
        FixtureScenario::Normal => normal_arg,
        FixtureScenario::InvalidOutput => "--invalid",
        FixtureScenario::Hang => "--hang",
        FixtureScenario::Descendant => "--descendant",
        FixtureScenario::Crash => "--crash",
    };
    let out = OpenOptions::new()
        .create_new(true)
        .write(true)
        .mode(0o600)
        .open(private.dir.join("stdout"))
        .map_err(|e| AdapterError::IoError(e.to_string()))?;
    let err = OpenOptions::new()
        .create_new(true)
        .write(true)
        .mode(0o600)
        .open(private.dir.join("stderr"))
        .map_err(|e| AdapterError::IoError(e.to_string()))?;
    let mut command = Command::new(&private.executable);
    command
        .arg(arg)
        .stdin(Stdio::null())
        .stdout(Stdio::from(out))
        .stderr(Stdio::from(err));
    command.process_group(0);
    unsafe {
        command.pre_exec(|| {
            let limit = libc::rlimit {
                rlim_cur: MAX_OUTPUT,
                rlim_max: MAX_OUTPUT,
            };
            if libc::setrlimit(libc::RLIMIT_FSIZE, &limit) != 0 {
                return Err(io::Error::last_os_error());
            }
            let no_core = libc::rlimit {
                rlim_cur: 0,
                rlim_max: 0,
            };
            if libc::setrlimit(libc::RLIMIT_CORE, &no_core) != 0 {
                return Err(io::Error::last_os_error());
            }
            Ok(())
        });
    }
    let mut child = command
        .spawn()
        .map_err(|e| AdapterError::IoError(e.to_string()))?;
    let started = Instant::now();
    let mut stopped = None;
    let mut killed = false;
    let code;
    loop {
        match child.try_wait() {
            Err(e) => {
                let _ = group_kill(child.id());
                let _ = child.kill();
                let _ = child.wait();
                return Err(AdapterError::IoError(format!("child wait failed: {e}")));
            }
            Ok(Some(status)) => {
                code = status.code();
                break;
            }
            Ok(None) if cancel.load(Ordering::Acquire) => {
                stopped = Some(Outcome::Cancelled);
                let kill = group_kill(child.id());
                if kill.is_err() {
                    let _ = child.kill();
                }
                code = child
                    .wait()
                    .map_err(|e| AdapterError::IoError(e.to_string()))?
                    .code();
                kill?;
                killed = true;
                break;
            }
            Ok(None) if started.elapsed() >= timeout => {
                stopped = Some(Outcome::TimedOut);
                let kill = group_kill(child.id());
                if kill.is_err() {
                    let _ = child.kill();
                }
                code = child
                    .wait()
                    .map_err(|e| AdapterError::IoError(e.to_string()))?
                    .code();
                kill?;
                killed = true;
                break;
            }
            Ok(None) => thread::sleep(Duration::from_millis(10)),
        }
    }
    thread::sleep(Duration::from_millis(40));
    let bytes =
        fs::read(private.dir.join("stdout")).map_err(|e| AdapterError::IoError(e.to_string()))?;
    let output = String::from_utf8_lossy(&bytes).trim().to_string();
    let after = guarded_scope()?;
    let memory_returned = after.memory_current_bytes
        <= baseline
            .memory_current_bytes
            .saturating_add(RETURN_TOLERANCE)
        && after.swap_current_bytes <= baseline.swap_current_bytes.saturating_add(RETURN_TOLERANCE);
    let oom_unchanged = after.oom_kill_events == baseline.oom_kill_events;
    let outcome = stopped.unwrap_or_else(|| {
        if code != Some(0) {
            Outcome::ProcessFailed
        } else if output == expected {
            Outcome::ProbePass
        } else {
            Outcome::SemanticReject
        }
    });
    Ok(FixtureReceipt {
        outcome,
        snapshot_sha256: fixture_sha256.into(),
        expected_semantic_output: expected.into(),
        observed_semantic_output: output,
        stdout_bytes: bytes.len() as u64,
        duration_ms: started.elapsed().as_millis(),
        child_exit_code: code,
        killed_process_group: killed,
        host_before: baseline,
        host_after: after,
        memory_returned_within_tolerance: memory_returned,
        oom_events_unchanged: oom_unchanged,
        gpu_reclaim_qualified: false,
    })
}
