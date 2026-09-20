#include "G4RunManagerFactory.hh"
#include "G4UImanager.hh"
#include "G4UIExecutive.hh"
#include "G4VisExecutive.hh"

// User Defined Classes
#include "DetectorConstruction.hh"
#include "PrimaryGeneratorAction.hh"
#include "RunAction.hh"
#include "SteppingAction.hh"

// Physics List headers
#include "FTFP_BERT.hh"
#include "G4EmLivermorePhysics.hh" 

// Action initialisation wrapper, required for multithreaded builds
#include "G4VUserActionInitialization.hh"

class ActionInitialization : public G4VUserActionInitialization {
  public:
    ActionInitialization() = default;
    ~ActionInitialization() override = default;

    // For the Master Thread (Just merges the data together at the end)
    void BuildForMaster() const override {
        SetUserAction(new RunAction());
    }

    // For the Worker Threads (Copies the Gun and Filter to each CPU core)
    void Build() const override {
        RunAction* runAction = new RunAction();
        SetUserAction(runAction);
        SetUserAction(new PrimaryGeneratorAction());
        SetUserAction(new SteppingAction(runAction));
    }
};

int main(int argc, char** argv) {
    G4UIExecutive* ui = nullptr;
    if (argc == 1) {
        ui = new G4UIExecutive(argc, argv);
    }

    auto* runManager = G4RunManagerFactory::CreateRunManager();
    runManager->SetUserInitialization(new DetectorConstruction());

    // Physics Base
    G4VModularPhysicsList* physicsList = new FTFP_BERT();
    physicsList->ReplacePhysics(new G4EmLivermorePhysics());
    runManager->SetUserInitialization(physicsList);

    // Register the wrapper rather than the actions directly
    runManager->SetUserInitialization(new ActionInitialization());

    G4UImanager* UImanager = G4UImanager::GetUIpointer();

    if (!ui) {
        // Batch Mode: No visualization overhead
        G4String command = "/control/execute ";
        G4String fileName = argv[1];
        UImanager->ApplyCommand(command + fileName);
    } else {
        // UI Mode: Visualization enabled
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
