#include "SteppingAction.hh"
#include "RunAction.hh"
#include "G4Step.hh"
#include "G4Track.hh"
#include "G4SystemOfUnits.hh"

SteppingAction::SteppingAction(RunAction* runAction)
: G4UserSteppingAction(), fRunAction(runAction) {}

SteppingAction::~SteppingAction() {}

void SteppingAction::UserSteppingAction(const G4Step* step) {
    G4Track* track = step->GetTrack();
    
    // 1. PERFECT VACUUM FILTER: Kill all secondary particles immediately
    if (track->GetTrackID() != 1) {
        track->SetTrackStatus(fStopAndKill);
        return;
    }

    // 2. SAFETY NET: Check if the photon flew out of the world!
    G4VPhysicalVolume* preVolume = step->GetPreStepPoint()->GetTouchableHandle()->GetVolume();
    if (!preVolume) return; 

    // 3. DETECTOR HIT (NARROW BEAM LOGIC)
    G4String volumeName = preVolume->GetName();
    
    if (volumeName == "Detector") {
        
        G4double initialEnergy = track->GetVertexKineticEnergy();
        G4ThreeVector momentum = track->GetMomentumDirection();
        
        // SCIENTIFIC CHECK 1: Did it lose any energy? (Compton/Photoelectric filter)
        G4bool energyKept = (track->GetKineticEnergy() > initialEnergy - 0.1 * keV);
        
        // SCIENTIFIC CHECK 2: Is it still flying perfectly straight? (Rayleigh scattering filter)
        G4bool straightLine = (momentum.z() > 0.999999);
        
        if (energyKept && straightLine) {
            fRunAction->CountTransmission();
        }
        
        track->SetTrackStatus(fStopAndKill);
    }
}
