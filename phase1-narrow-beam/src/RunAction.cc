#include "RunAction.hh"
#include "G4RunManager.hh"
#include "G4Run.hh"
#include "G4AccumulableManager.hh"
#include "G4SystemOfUnits.hh"

RunAction::RunAction() : G4UserRunAction(), fTransmissionCount(0) {
    G4AccumulableManager* accumulableManager = G4AccumulableManager::Instance();
    // v11 Syntax Fix
    accumulableManager->Register(fTransmissionCount);
}

RunAction::~RunAction() {}

void RunAction::BeginOfRunAction(const G4Run*) {
    G4AccumulableManager* accumulableManager = G4AccumulableManager::Instance();
    accumulableManager->Reset();
}

void RunAction::EndOfRunAction(const G4Run* run) {
    G4AccumulableManager* accumulableManager = G4AccumulableManager::Instance();
    accumulableManager->Merge();

    G4int nofEvents = run->GetNumberOfEvent();
    if (nofEvents == 0) return;

    if (IsMaster()) {
        G4int counts = fTransmissionCount.GetValue();
        G4double transmissionRatio = (G4double)counts / nofEvents;

        // THIS MUST MATCH THE PYTHON SCRIPT REGULAR EXPRESSION EXACTLY
        G4cout << "\n==========================================" << G4endl;
        G4cout << "Primary Photons Fired (I_0): " << nofEvents << G4endl;
        G4cout << "Surviving Photons (I): " << counts << G4endl;
        G4cout << "Transmission Ratio (I/I_0): " << transmissionRatio << G4endl;
        G4cout << "==========================================\n" << G4endl;
    }
}
