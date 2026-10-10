//! Minimal host-side scope gate probe. Exit 73 when not inside GNU6 bounded scope.
fn main() {
    match gnostral_q013b_local_adapter::guarded_scope() {
        Ok(sample) => {
            println!("Q013B_BOUNDARY_PASS {}", sample.cgroup_path);
        }
        Err(reason) => {
            eprintln!("Q013B_BOUNDARY_DENIED {reason:?}");
            std::process::exit(73);
        }
    }
}
