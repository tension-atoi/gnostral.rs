use crate::{ExpertKey, Lease, ResidencyError, ResidencyTable};
use std::collections::BTreeSet;

#[derive(Debug, Clone, PartialEq)]
pub struct Route {
    pub token: usize,
    pub ordinal: usize,
    pub key: ExpertKey,
    pub weight: f32,
}
#[derive(Debug)]
pub struct RoutePartition {
    pub gpu: Vec<(Route, Lease)>,
    pub cpu: Vec<Route>,
}

/// Preserves route order within each destination, including repeated experts.
/// Caller must release all GPU leases after computation (also on errors).
pub fn partition_routes(
    table: &mut ResidencyTable,
    routes: &[Route],
) -> Result<RoutePartition, ResidencyError> {
    let mut positions = BTreeSet::new();
    for route in routes {
        table.validate_key(route.key)?;
        if !route.weight.is_finite() || !positions.insert((route.token, route.ordinal)) {
            return Err(ResidencyError::InvalidProfile);
        }
    }
    let mut partition = RoutePartition {
        gpu: Vec::new(),
        cpu: Vec::new(),
    };
    for route in routes {
        match table.acquire(route.key) {
            Ok(Some(lease)) => partition.gpu.push((route.clone(), lease)),
            Ok(None) => partition.cpu.push(route.clone()),
            Err(error) => {
                for (_, lease) in partition.gpu {
                    table.release(lease)?;
                }
                return Err(error);
            }
        }
    }
    Ok(partition)
}
