#include "RunAction.hh"

#include "G4Run.hh"
#include "G4RunManager.hh"
#include "G4SystemOfUnits.hh"
#include "G4AutoLock.hh"

#include <fstream>

// ── Static member definitions ──────────────────────────────────────────────
G4Mutex                  RunAction::fMutex    = G4MUTEX_INITIALIZER;
std::array<G4long, 1500> RunAction::fSpectrum = {};

// ──────────────────────────────────────────────────────────────────────────
RunAction::RunAction()
: G4UserRunAction(), fOutputFile("spectrum_output.csv")
{
    fMessenger = new G4GenericMessenger(this, "/output/",
                                        "Output file control");
    fMessenger->DeclareMethod("setFile", &RunAction::SetOutputFile,
                              "Set spectrum output filename (e.g. spectrum_PPS_2mm_662.csv)");
}

RunAction::~RunAction() {
    delete fMessenger;
}

// ──────────────────────────────────────────────────────────────────────────
void RunAction::BeginOfRunAction(const G4Run*)
{
    // Reset spectrum on the master thread before any events fire.
    // Worker threads start AFTER master's BeginOfRunAction, so this is safe.
    if (IsMaster()) {
        G4AutoLock lock(&fMutex);
        fSpectrum.fill(0);
    }
}

// ──────────────────────────────────────────────────────────────────────────
// Called from EventAction::EndOfEventAction on a worker thread.
// G4AutoLock ensures thread safety with minimal overhead.
void RunAction::FillSpectrum(G4int bin)
{
    if (bin < 0 || bin >= 1500) return;
    G4AutoLock lock(&fMutex);
    fSpectrum[bin]++;
}

// ──────────────────────────────────────────────────────────────────────────
void RunAction::EndOfRunAction(const G4Run* run)
{
    if (!IsMaster()) return;   // Only the master thread writes output

    G4int nEvents = run->GetNumberOfEvent();
    if (nEvents == 0) return;

    // Lock not strictly needed here (all workers are done) but kept for safety
    G4AutoLock lock(&fMutex);

    // ── Write spectrum to CSV ──────────────────────────────────────────────
    std::ofstream file(fOutputFile);
    if (!file.is_open()) {
        G4cerr << "ERROR: Cannot open output file: " << fOutputFile << G4endl;
        return;
    }

    file << "# Phase 2 NaI(Tl) energy spectrum\n";
    file << "# Total histories: " << nEvents << "\n";
    file << "# Format: bin_lower_edge_keV, counts\n";
    file << "# Bin width: 1 keV/bin  |  Range: 0-1499 keV\n";

    G4long totalCounts = 0;
    for (G4int i = 0; i < 1500; i++) {
        file << i << "," << fSpectrum[i] << "\n";
        totalCounts += fSpectrum[i];
    }
    file.close();

    G4cout << "\n==========================================\n"
           << " Spectrum written to: " << fOutputFile    << "\n"
           << " Total histories:     " << nEvents        << "\n"
           << " Total NaI hits:      " << totalCounts    << "\n"
           << " Detection efficiency: "
           << G4double(totalCounts)/nEvents * 100. << " %\n"
           << "==========================================\n" << G4endl;
}
