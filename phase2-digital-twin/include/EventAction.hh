#ifndef EventAction_h
#define EventAction_h 1

#include "G4UserEventAction.hh"
#include "globals.hh"

class RunAction;

class EventAction : public G4UserEventAction {
public:
    EventAction();
    virtual ~EventAction();

    virtual void BeginOfEventAction(const G4Event*);
    virtual void EndOfEventAction(const G4Event*);

    // Called by SteppingAction for every step inside the NaI crystal
    void AddEdepNaI(G4double edep) { fEdepNaI += edep; }

private:
    G4double fEdepNaI;  // Total energy deposited in NaI this event
};

#endif
