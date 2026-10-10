use crate::ResidencyError;
use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct ExpertKey {
    pub layer: u32,
    pub expert: u32,
}
#[derive(Debug, Clone, Copy)]
pub struct ExpertSize {
    pub key: ExpertKey,
    pub bytes: u64,
}
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct SlotSpec {
    pub key: ExpertKey,
    pub offset: u64,
    pub bytes: u64,
}

/// Validated immutable plan. Bytes are a budget, not measured residency.
#[derive(Debug, Clone)]
pub struct CachePlan {
    slots: Vec<SlotSpec>,
    planned_bytes: u64,
    layers: u32,
    experts: u32,
}
impl CachePlan {
    pub fn build(
        layers: u32,
        experts: u32,
        sizes: &[ExpertSize],
        ranking: &[ExpertKey],
        budget_bytes: u64,
    ) -> Result<Self, ResidencyError> {
        if layers == 0 || experts == 0 {
            return Err(ResidencyError::InvalidGeometry);
        }
        let valid = |key: ExpertKey| key.layer < layers && key.expert < experts;
        let mut by_key = BTreeMap::new();
        let mut total = 0u64;
        for size in sizes {
            if !valid(size.key) || size.bytes == 0 || by_key.insert(size.key, size.bytes).is_some()
            {
                return Err(ResidencyError::InvalidProfile);
            }
            total = total
                .checked_add(size.bytes)
                .ok_or(ResidencyError::Overflow)?;
        }
        let mut seen = BTreeSet::new();
        for &key in ranking {
            if !valid(key) || !seen.insert(key) || !by_key.contains_key(&key) {
                return Err(ResidencyError::InvalidProfile);
            }
        }
        let mut plan = Self {
            slots: Vec::new(),
            planned_bytes: 0,
            layers,
            experts,
        };
        for &key in ranking {
            let bytes = by_key[&key];
            if bytes > budget_bytes - plan.planned_bytes {
                continue;
            }
            plan.slots.push(SlotSpec {
                key,
                offset: plan.planned_bytes,
                bytes,
            });
            plan.planned_bytes = plan
                .planned_bytes
                .checked_add(bytes)
                .ok_or(ResidencyError::Overflow)?;
        }
        Ok(plan)
    }
    pub fn slots(&self) -> &[SlotSpec] {
        &self.slots
    }
    pub fn planned_bytes(&self) -> u64 {
        self.planned_bytes
    }
    pub fn contains_key(&self, key: ExpertKey) -> bool {
        key.layer < self.layers && key.expert < self.experts
    }
}
