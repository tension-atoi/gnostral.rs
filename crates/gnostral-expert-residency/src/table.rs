use crate::{CachePlan, ExpertKey, ResidencyError};
use std::collections::BTreeMap;
use std::sync::atomic::{AtomicU64, Ordering};

static TABLE_ID: AtomicU64 = AtomicU64::new(1);
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct SlotId(usize);
impl SlotId {
    pub fn index(self) -> usize {
        self.0
    }
}
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UploadTicket {
    table: u64,
    slot: SlotId,
    nonce: u64,
}
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Lease {
    table: u64,
    slot: SlotId,
    nonce: u64,
    key: ExpertKey,
}
impl Lease {
    pub fn key(&self) -> ExpertKey {
        self.key
    }
    pub fn slot(&self) -> SlotId {
        self.slot
    }
}
#[derive(Debug, Clone, Copy)]
enum State {
    Vacant,
    Pending(u64),
    Resident,
}

/// Owns metadata only; callers own allocations and prove upload completion.
#[derive(Debug)]
pub struct ResidencyTable {
    plan: CachePlan,
    id: u64,
    nonce: u64,
    slots: BTreeMap<ExpertKey, SlotId>,
    states: Vec<State>,
    leases: BTreeMap<u64, SlotId>,
    closed: bool,
}
impl ResidencyTable {
    pub fn new(plan: CachePlan) -> Self {
        let id = TABLE_ID
            .fetch_update(Ordering::Relaxed, Ordering::Relaxed, |n| n.checked_add(1))
            .expect("expert residency table identity space exhausted");
        let slots = plan
            .slots()
            .iter()
            .enumerate()
            .map(|(n, s)| (s.key, SlotId(n)))
            .collect();
        let states = vec![State::Vacant; plan.slots().len()];
        Self {
            plan,
            id,
            nonce: 0,
            slots,
            states,
            leases: BTreeMap::new(),
            closed: false,
        }
    }
    fn next_nonce(&mut self) -> Result<u64, ResidencyError> {
        self.nonce = self.nonce.checked_add(1).ok_or(ResidencyError::Overflow)?;
        Ok(self.nonce)
    }
    pub fn validate_key(&self, key: ExpertKey) -> Result<(), ResidencyError> {
        if self.closed {
            return Err(ResidencyError::Closed);
        }
        if !self.plan.contains_key(key) {
            return Err(ResidencyError::InvalidProfile);
        }
        Ok(())
    }
    pub fn begin_upload(&mut self, key: ExpertKey) -> Result<UploadTicket, ResidencyError> {
        self.validate_key(key)?;
        let slot = *self.slots.get(&key).ok_or(ResidencyError::InvalidProfile)?;
        if !matches!(self.states[slot.0], State::Vacant) {
            return Err(ResidencyError::Busy);
        }
        let nonce = self.next_nonce()?;
        self.states[slot.0] = State::Pending(nonce);
        Ok(UploadTicket {
            table: self.id,
            slot,
            nonce,
        })
    }
    pub fn complete_upload(
        &mut self,
        ticket: UploadTicket,
        succeeded: bool,
    ) -> Result<(), ResidencyError> {
        if self.closed {
            return Err(ResidencyError::Closed);
        }
        if ticket.table != self.id
            || !matches!(self.states.get(ticket.slot.0),Some(State::Pending(n)) if *n==ticket.nonce)
        {
            return Err(ResidencyError::InvalidTicket);
        }
        self.states[ticket.slot.0] = if succeeded {
            State::Resident
        } else {
            State::Vacant
        };
        if succeeded {
            Ok(())
        } else {
            Err(ResidencyError::UploadFailed)
        }
    }
    pub fn acquire(&mut self, key: ExpertKey) -> Result<Option<Lease>, ResidencyError> {
        self.validate_key(key)?;
        let Some(&slot) = self.slots.get(&key) else {
            return Ok(None);
        };
        if !matches!(self.states[slot.0], State::Resident) {
            return Ok(None);
        }
        let nonce = self.next_nonce()?;
        self.leases.insert(nonce, slot);
        Ok(Some(Lease {
            table: self.id,
            slot,
            nonce,
            key,
        }))
    }
    pub fn release(&mut self, lease: Lease) -> Result<(), ResidencyError> {
        if lease.table != self.id || self.leases.get(&lease.nonce) != Some(&lease.slot) {
            return Err(ResidencyError::InvalidTicket);
        }
        self.leases.remove(&lease.nonce);
        Ok(())
    }
    pub fn active_leases(&self) -> usize {
        self.leases.len()
    }
    pub fn close(&mut self) -> Result<(), ResidencyError> {
        if !self.leases.is_empty() || self.states.iter().any(|s| matches!(s, State::Pending(_))) {
            return Err(ResidencyError::Busy);
        }
        self.closed = true;
        self.states.fill(State::Vacant);
        Ok(())
    }
}
