#ifndef RunAction_h
#define RunAction_h 1

#include "G4UserRunAction.hh"
#include "globals.hh"
#include "G4Threading.hh"
#include "G4GenericMessenger.hh"
#include <array>
#include <string>

class G4Run;

class RunAction : public G4UserRunAction {
public:
    RunAction();
    virtual ~RunAction();

    virtual void BeginOfRunAction(const G4Run*);
    virtual void EndOfRunAction(const G4Run*);

    // Thread-safe spectrum fill — called from EventAction
    static void FillSpectrum(G4int bin_keV);

    void SetOutputFile(G4String fn) { fOutputFile = fn; }

private:
    G4GenericMessenger* fMessenger;
    G4String            fOutputFile;

    // Static: shared across all worker threads, protected by fMutex
    static G4Mutex                    fMutex;
    static std::array<G4long, 1500>   fSpectrum; // 1 keV/bin, 0-1499 keV
};

#endif
