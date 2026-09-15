#include "G4RunManagerFactory.hh"
#include "G4UImanager.hh"
#include "G4UIExecutive.hh"
#include "G4VisExecutive.hh"

#include "DetectorConstruction.hh"
#include "PrimaryGeneratorAction.hh"
#include "RunAction.hh"
#include "EventAction.hh"
#include "SteppingAction.hh"

#include "FTFP_BERT.hh"
#include "G4EmLivermorePhysics.hh"
#include "G4VUserActionInitialization.hh"

// ── Action Initialisation ─────────────────────────────────────────────────
// Phase 2 adds EventAction to the worker thread.
// Master thread only runs RunAction (for merging + file writing).
class ActionInitialization : public G4VUserActionInitialization {
public:
    ActionInitialization()  = default;
    ~ActionInitialization() override = default;

    void BuildForMaster() const override {
        SetUserAction(new RunAction());
    }

    void Build() const override {
        RunAction*   runAction = new RunAction();
        EventAction* evtAction = new EventAction();
        SetUserAction(runAction);
        SetUserAction(evtAction);
        SetUserAction(new PrimaryGeneratorAction());
        SetUserAction(new SteppingAction(evtAction));   // <-- evtAction passed here
    }
};

// ── main ──────────────────────────────────────────────────────────────────
int main(int argc, char** argv)
{
    G4UIExecutive* ui = nullptr;
    if (argc == 1) {
        ui = new G4UIExecutive(argc, argv);
    }

    auto* runManager = G4RunManagerFactory::CreateRunManager();
    runManager->SetUserInitialization(new DetectorConstruction());

    // FTFP_BERT provides validated transportation + hadronic physics base.
    // G4EmLivermorePhysics replaces the EM component with Livermore data sets:
    // validated down to 250 eV — essential for accurate 59.5 keV simulation.
    G4VModularPhysicsList* physicsList = new FTFP_BERT();
    physicsList->ReplacePhysics(new G4EmLivermorePhysics());
    runManager->SetUserInitialization(physicsList);

    runManager->SetUserInitialization(new ActionInitialization());

    G4UImanager* UImanager = G4UImanager::GetUIpointer();

    if (!ui) {
        // Batch mode: run the macro supplied as argv[1]
        UImanager->ApplyCommand("/control/execute " + G4String(argv[1]));
    } else {
        // Interactive mode: load visualisation
        G4VisManager* visManager = new G4VisExecutive;
        visManager->Initialize();
        UImanager->ApplyCommand("/control/execute init_vis.mac");
        ui->SessionStart();
        delete ui;
        delete visManager;
    }

    delete runManager;
    return 0;
}
