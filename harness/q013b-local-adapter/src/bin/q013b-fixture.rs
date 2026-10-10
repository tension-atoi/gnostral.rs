//! Disposable bounded subprocess; *never* loads weights or contacts a model server.
use std::{process::Command, thread, time::Duration};
fn main() {
    let arg = std::env::args().nth(1).unwrap_or_default();
    match arg.as_str() {
        "--dense" => println!("Q013B_DENSE=GNOSTRAL"),
        "--embedding" => println!("Q013B_EMBEDDING=3x1024_FINITE"),
        "--moe" => println!("Q013B_MOE=CPU_EXPERTS"),
        "--invalid" => println!("Q013B_INVALID=FORGED"),
        "--hang" => loop {
            thread::sleep(Duration::from_secs(1));
        },
        "--descendant" => {
            let exe = std::env::current_exe().expect("fixture executable");
            let mut child = Command::new(exe)
                .arg("--hang")
                .spawn()
                .expect("spawn descendant");
            println!("DESCENDANT_PID={}", child.id());
            let _ = child.wait(); // parent blocks; adapter must kill the entire group
        }
        "--crash" => std::process::exit(23),
        _ => std::process::exit(64),
    }
}
