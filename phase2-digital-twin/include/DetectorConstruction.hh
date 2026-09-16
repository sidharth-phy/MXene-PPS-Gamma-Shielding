#ifndef DetectorConstruction_h
#define DetectorConstruction_h 1

#include "G4VUserDetectorConstruction.hh"
#include "globals.hh"

class G4VPhysicalVolume;
class G4LogicalVolume;
class G4Material;
class G4GenericMessenger;
class G4Tubs;

class DetectorConstruction : public G4VUserDetectorConstruction {
public:
    DetectorConstruction();
    virtual ~DetectorConstruction();
    virtual G4VPhysicalVolume* Construct();

    // These are called from macro commands BEFORE /run/initialize.
    // They store the requested values only; geometry is built in
    // ConstructVolumes() after DefineMaterials() has populated the table.
    void SetTargetMaterial(G4String name);
    void SetTargetThickness(G4double thickness);

private:
    void DefineMaterials();
    G4VPhysicalVolume* ConstructVolumes();

    G4LogicalVolume*    fTargetLogical;
    G4VPhysicalVolume*  fTargetPhysical;
    G4Tubs*             fCurrentSolid;

    // The material is stored by name, not as a pointer, so the geometry can be
    // rebuilt when /shielding/setMaterial is issued before /run/initialize.
    // Pointer lookup (G4Material::GetMaterial) happens in ConstructVolumes()
    // AFTER DefineMaterials() has run — not in SetTargetMaterial().
    G4String  fMaterialName;
    G4double  fTargetThickness;

    G4GenericMessenger* fMessenger;
};

#endif
