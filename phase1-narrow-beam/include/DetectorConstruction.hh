#ifndef DetectorConstruction_h
#define DetectorConstruction_h 1

#include "G4VUserDetectorConstruction.hh"
#include "globals.hh"

class G4VPhysicalVolume;
class G4LogicalVolume;
class G4Material;
class G4GenericMessenger;

class DetectorConstruction : public G4VUserDetectorConstruction {
  public:
    DetectorConstruction();
    virtual ~DetectorConstruction();

    virtual G4VPhysicalVolume* Construct();
    
    // Custom UI Commands
    void SetTargetMaterial(G4String materialName);
    void SetTargetThickness(G4double thickness);

  private:
    void DefineMaterials();
    G4VPhysicalVolume* ConstructVolumes();

    G4LogicalVolume* fTargetLogical;
    G4LogicalVolume* fDetectorLogical;
    G4VPhysicalVolume* fTargetPhysical;
    
    G4Material* fCurrentMaterial;
    G4double fTargetThickness;
    
    G4GenericMessenger* fMessenger;
};

#endif
