#include "SteppingAction.hh"
#include "EventAction.hh"

#include "G4Step.hh"
#include "G4Track.hh"
#include "G4SystemOfUnits.hh"
#include "G4VPhysicalVolume.hh"
#include "G4TouchableHandle.hh"

SteppingAction::SteppingAction(EventAction* evtAction)
: G4UserSteppingAction(), fEventAction(evtAction) {}

SteppingAction::~SteppingAction() {}

void SteppingAction::UserSteppingAction(const G4Step* step)
{
    // ── Get the volume this step is in ───────────────────────────────────
    G4VPhysicalVolume* preVol =
        step->GetPreStepPoint()->GetTouchableHandle()->GetVolume();
    if (!preVol) return;

    G4String volName = preVol->GetName();

    // ── Score energy deposition inside the NaI crystal ───────────────────
    // In Phase 2 we measure the FULL energy deposition from ALL particles:
    // primary photon, Compton electrons, secondary photons, photoelectrons.
    // This is what a real NaI(Tl)+PMT detector integrates over its shaping time.
    if (volName == "NaICrystal") {
        G4double edep = step->GetTotalEnergyDeposit();
        if (edep > 0.) {
            fEventAction->AddEdepNaI(edep);
        }
        return;  // No need to do anything else for NaI steps
    }

    // ── Secondary suppression in the lead volumes ──
    // Every secondary created inside the lead collimators and the castle is
    // terminated, charged and neutral alike. Charged secondaries there have a
    // range well under 1 mm and could not reach the crystal in any case. Lead
    // fluorescence photons could, so suppressing them also removes the
    // fluorescence background, which is why the graded-Z shells make no
    // measurable contribution in these runs. This is stated in the manuscript.
    if (volName == "SourceColl" || volName == "MidColl" || volName == "PbCastle") {
        G4Track* track = step->GetTrack();
        if (track->GetTrackID() != 1) {         // Not the primary photon
            track->SetTrackStatus(fStopAndKill);
        }
    }
}
