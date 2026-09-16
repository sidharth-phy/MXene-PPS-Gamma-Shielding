#include "DetectorConstruction.hh"
#include "G4RunManager.hh"
#include "G4NistManager.hh"
#include "G4Box.hh"
#include "G4Tubs.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"
#include "G4GenericMessenger.hh"

DetectorConstruction::DetectorConstruction()
: G4VUserDetectorConstruction(),
  fTargetLogical(nullptr), fDetectorLogical(nullptr), fTargetPhysical(nullptr),
  fCurrentMaterial(nullptr), fTargetThickness(2.0*mm)
{
    // Materials are built at construction, before any geometry is placed
    DefineMaterials();

    fMessenger = new G4GenericMessenger(this, "/shielding/", "Target control commands");
    fMessenger->DeclareMethod("setMaterial", &DetectorConstruction::SetTargetMaterial, "Set the material of the target disc.");
    fMessenger->DeclareMethodWithUnit("setThickness", "mm", &DetectorConstruction::SetTargetThickness, "Set the thickness of the target disc.");
}

DetectorConstruction::~DetectorConstruction()
{
    delete fMessenger;
}

G4VPhysicalVolume* DetectorConstruction::Construct()
{
    // DefineMaterials() was removed from here.
    return ConstructVolumes();
}

void DetectorConstruction::DefineMaterials()
{
    G4NistManager* nist = G4NistManager::Instance();

    // 1. Load All Elements
    G4Element* elC  = nist->FindOrBuildElement("C");
    G4Element* elH  = nist->FindOrBuildElement("H");
    G4Element* elS  = nist->FindOrBuildElement("S");
    G4Element* elW  = nist->FindOrBuildElement("W");
    G4Element* elTi = nist->FindOrBuildElement("Ti");
    G4Element* elO  = nist->FindOrBuildElement("O");
    G4Element* elPb = nist->FindOrBuildElement("Pb");
    G4Element* elBa = nist->FindOrBuildElement("Ba");
    G4Element* elBi = nist->FindOrBuildElement("Bi");

    // 2. Pure PPS Baseline
    G4Material* PPS_0Wt = new G4Material("PPS_0Wt", 1.3500*g/cm3, 3);
    PPS_0Wt->AddElement(elC, 0.6663); PPS_0Wt->AddElement(elH, 0.0373); PPS_0Wt->AddElement(elS, 0.2964);

    // 3. Lead (Pb) Composites
    G4Material* Pb_5Wt = new G4Material("Pb_5Wt", 1.4122*g/cm3, 4);
    Pb_5Wt->AddElement(elC, 0.6330); Pb_5Wt->AddElement(elH, 0.0354); Pb_5Wt->AddElement(elS, 0.2816); Pb_5Wt->AddElement(elPb, 0.0500);
    G4Material* Pb_10Wt = new G4Material("Pb_10Wt", 1.4804*g/cm3, 4);
    Pb_10Wt->AddElement(elC, 0.5997); Pb_10Wt->AddElement(elH, 0.0336); Pb_10Wt->AddElement(elS, 0.2668); Pb_10Wt->AddElement(elPb, 0.1000);
    G4Material* Pb_15Wt = new G4Material("Pb_15Wt", 1.5556*g/cm3, 4);
    Pb_15Wt->AddElement(elC, 0.5664); Pb_15Wt->AddElement(elH, 0.0317); Pb_15Wt->AddElement(elS, 0.2519); Pb_15Wt->AddElement(elPb, 0.1500);
    G4Material* Pb_20Wt = new G4Material("Pb_20Wt", 1.6387*g/cm3, 4);
    Pb_20Wt->AddElement(elC, 0.5330); Pb_20Wt->AddElement(elH, 0.0298); Pb_20Wt->AddElement(elS, 0.2371); Pb_20Wt->AddElement(elPb, 0.2000);
    G4Material* Pb_25Wt = new G4Material("Pb_25Wt", 1.7313*g/cm3, 4);
    Pb_25Wt->AddElement(elC, 0.4997); Pb_25Wt->AddElement(elH, 0.0280); Pb_25Wt->AddElement(elS, 0.2223); Pb_25Wt->AddElement(elPb, 0.2500);
    G4Material* Pb_30Wt = new G4Material("Pb_30Wt", 1.8350*g/cm3, 4);
    Pb_30Wt->AddElement(elC, 0.4664); Pb_30Wt->AddElement(elH, 0.0261); Pb_30Wt->AddElement(elS, 0.2075); Pb_30Wt->AddElement(elPb, 0.3000);

    // 4. Barium Sulfate (BaSO4) Composites
    G4Material* BaSO4_5Wt = new G4Material("BaSO4_5Wt", 1.3990*g/cm3, 5);
    BaSO4_5Wt->AddElement(elC, 0.6330); BaSO4_5Wt->AddElement(elH, 0.0354); BaSO4_5Wt->AddElement(elS, 0.2884); BaSO4_5Wt->AddElement(elBa, 0.0294); BaSO4_5Wt->AddElement(elO, 0.0137);
    G4Material* BaSO4_10Wt = new G4Material("BaSO4_10Wt", 1.4516*g/cm3, 5);
    BaSO4_10Wt->AddElement(elC, 0.5997); BaSO4_10Wt->AddElement(elH, 0.0336); BaSO4_10Wt->AddElement(elS, 0.2805); BaSO4_10Wt->AddElement(elBa, 0.0588); BaSO4_10Wt->AddElement(elO, 0.0274);
    G4Material* BaSO4_15Wt = new G4Material("BaSO4_15Wt", 1.5084*g/cm3, 5);
    BaSO4_15Wt->AddElement(elC, 0.5664); BaSO4_15Wt->AddElement(elH, 0.0317); BaSO4_15Wt->AddElement(elS, 0.2726); BaSO4_15Wt->AddElement(elBa, 0.0883); BaSO4_15Wt->AddElement(elO, 0.0411);
    G4Material* BaSO4_20Wt = new G4Material("BaSO4_20Wt", 1.5698*g/cm3, 5);
    BaSO4_20Wt->AddElement(elC, 0.5330); BaSO4_20Wt->AddElement(elH, 0.0298); BaSO4_20Wt->AddElement(elS, 0.2646); BaSO4_20Wt->AddElement(elBa, 0.1177); BaSO4_20Wt->AddElement(elO, 0.0548);
    G4Material* BaSO4_25Wt = new G4Material("BaSO4_25Wt", 1.6364*g/cm3, 5);
    BaSO4_25Wt->AddElement(elC, 0.4997); BaSO4_25Wt->AddElement(elH, 0.0280); BaSO4_25Wt->AddElement(elS, 0.2566); BaSO4_25Wt->AddElement(elBa, 0.1471); BaSO4_25Wt->AddElement(elO, 0.0685);
    G4Material* BaSO4_30Wt = new G4Material("BaSO4_30Wt", 1.7089*g/cm3, 5);
    BaSO4_30Wt->AddElement(elC, 0.4664); BaSO4_30Wt->AddElement(elH, 0.0261); BaSO4_30Wt->AddElement(elS, 0.2487); BaSO4_30Wt->AddElement(elBa, 0.1765); BaSO4_30Wt->AddElement(elO, 0.0823);

    // 5. Tungsten (W) Composites
    G4Material* W_5Wt = new G4Material("W_5Wt", 1.4158*g/cm3, 4);
    W_5Wt->AddElement(elC, 0.6330); W_5Wt->AddElement(elH, 0.0354); W_5Wt->AddElement(elS, 0.2816); W_5Wt->AddElement(elW, 0.0500);
    G4Material* W_10Wt = new G4Material("W_10Wt", 1.4884*g/cm3, 4);
    W_10Wt->AddElement(elC, 0.5997); W_10Wt->AddElement(elH, 0.0336); W_10Wt->AddElement(elS, 0.2668); W_10Wt->AddElement(elW, 0.1000);
    G4Material* W_15Wt = new G4Material("W_15Wt", 1.5688*g/cm3, 4);
    W_15Wt->AddElement(elC, 0.5664); W_15Wt->AddElement(elH, 0.0317); W_15Wt->AddElement(elS, 0.2519); W_15Wt->AddElement(elW, 0.1500);
    G4Material* W_20Wt = new G4Material("W_20Wt", 1.6584*g/cm3, 4);
    W_20Wt->AddElement(elC, 0.5330); W_20Wt->AddElement(elH, 0.0298); W_20Wt->AddElement(elS, 0.2371); W_20Wt->AddElement(elW, 0.2000);
    G4Material* W_25Wt = new G4Material("W_25Wt", 1.7589*g/cm3, 4);
    W_25Wt->AddElement(elC, 0.4997); W_25Wt->AddElement(elH, 0.0280); W_25Wt->AddElement(elS, 0.2223); W_25Wt->AddElement(elW, 0.2500);
    G4Material* W_30Wt = new G4Material("W_30Wt", 1.8723*g/cm3, 4);
    W_30Wt->AddElement(elC, 0.4664); W_30Wt->AddElement(elH, 0.0261); W_30Wt->AddElement(elS, 0.2075); W_30Wt->AddElement(elW, 0.3000);

    // 6. Bismuth Oxide (Bi2O3) Composites
    G4Material* Bi2O3_5Wt = new G4Material("Bi2O3_5Wt", 1.4098*g/cm3, 5);
    Bi2O3_5Wt->AddElement(elC, 0.6330); Bi2O3_5Wt->AddElement(elH, 0.0354); Bi2O3_5Wt->AddElement(elS, 0.2816); Bi2O3_5Wt->AddElement(elBi, 0.0449); Bi2O3_5Wt->AddElement(elO, 0.0052);
    G4Material* Bi2O3_10Wt = new G4Material("Bi2O3_10Wt", 1.4751*g/cm3, 5);
    Bi2O3_10Wt->AddElement(elC, 0.5997); Bi2O3_10Wt->AddElement(elH, 0.0336); Bi2O3_10Wt->AddElement(elS, 0.2668); Bi2O3_10Wt->AddElement(elBi, 0.0897); Bi2O3_10Wt->AddElement(elO, 0.0103);
    G4Material* Bi2O3_15Wt = new G4Material("Bi2O3_15Wt", 1.5468*g/cm3, 5);
    Bi2O3_15Wt->AddElement(elC, 0.5664); Bi2O3_15Wt->AddElement(elH, 0.0317); Bi2O3_15Wt->AddElement(elS, 0.2519); Bi2O3_15Wt->AddElement(elBi, 0.1346); Bi2O3_15Wt->AddElement(elO, 0.0154);
    G4Material* Bi2O3_20Wt = new G4Material("Bi2O3_20Wt", 1.6258*g/cm3, 5);
    Bi2O3_20Wt->AddElement(elC, 0.5330); Bi2O3_20Wt->AddElement(elH, 0.0298); Bi2O3_20Wt->AddElement(elS, 0.2371); Bi2O3_20Wt->AddElement(elBi, 0.1794); Bi2O3_20Wt->AddElement(elO, 0.0206);
    G4Material* Bi2O3_25Wt = new G4Material("Bi2O3_25Wt", 1.7134*g/cm3, 5);
    Bi2O3_25Wt->AddElement(elC, 0.4997); Bi2O3_25Wt->AddElement(elH, 0.0280); Bi2O3_25Wt->AddElement(elS, 0.2223); Bi2O3_25Wt->AddElement(elBi, 0.2243); Bi2O3_25Wt->AddElement(elO, 0.0257);
    G4Material* Bi2O3_30Wt = new G4Material("Bi2O3_30Wt", 1.8109*g/cm3, 5);
    Bi2O3_30Wt->AddElement(elC, 0.4664); Bi2O3_30Wt->AddElement(elH, 0.0261); Bi2O3_30Wt->AddElement(elS, 0.2075); Bi2O3_30Wt->AddElement(elBi, 0.2691); Bi2O3_30Wt->AddElement(elO, 0.0309);

    // 7. MXene (Ti3C2O2) Composites
    G4Material* Ti3C2O2_5Wt = new G4Material("Ti3C2O2_5Wt", 1.4027*g/cm3, 5);
    Ti3C2O2_5Wt->AddElement(elC, 0.6390); Ti3C2O2_5Wt->AddElement(elH, 0.0354); Ti3C2O2_5Wt->AddElement(elS, 0.2816); Ti3C2O2_5Wt->AddElement(elTi, 0.0360); Ti3C2O2_5Wt->AddElement(elO, 0.0080);
    G4Material* Ti3C2O2_10Wt = new G4Material("Ti3C2O2_10Wt", 1.4597*g/cm3, 5);
    Ti3C2O2_10Wt->AddElement(elC, 0.6117); Ti3C2O2_10Wt->AddElement(elH, 0.0336); Ti3C2O2_10Wt->AddElement(elS, 0.2668); Ti3C2O2_10Wt->AddElement(elTi, 0.0719); Ti3C2O2_10Wt->AddElement(elO, 0.0160);
    G4Material* Ti3C2O2_15Wt = new G4Material("Ti3C2O2_15Wt", 1.5216*g/cm3, 5);
    Ti3C2O2_15Wt->AddElement(elC, 0.5844); Ti3C2O2_15Wt->AddElement(elH, 0.0317); Ti3C2O2_15Wt->AddElement(elS, 0.2519); Ti3C2O2_15Wt->AddElement(elTi, 0.1079); Ti3C2O2_15Wt->AddElement(elO, 0.0240);
    G4Material* Ti3C2O2_20Wt = new G4Material("Ti3C2O2_20Wt", 1.5889*g/cm3, 5);
    Ti3C2O2_20Wt->AddElement(elC, 0.5571); Ti3C2O2_20Wt->AddElement(elH, 0.0298); Ti3C2O2_20Wt->AddElement(elS, 0.2371); Ti3C2O2_20Wt->AddElement(elTi, 0.1439); Ti3C2O2_20Wt->AddElement(elO, 0.0321);
    G4Material* Ti3C2O2_25Wt = new G4Material("Ti3C2O2_25Wt", 1.6625*g/cm3, 5);
    Ti3C2O2_25Wt->AddElement(elC, 0.5298); Ti3C2O2_25Wt->AddElement(elH, 0.0280); Ti3C2O2_25Wt->AddElement(elS, 0.2223); Ti3C2O2_25Wt->AddElement(elTi, 0.1799); Ti3C2O2_25Wt->AddElement(elO, 0.0401);
    G4Material* Ti3C2O2_30Wt = new G4Material("Ti3C2O2_30Wt", 1.7432*g/cm3, 5);
    Ti3C2O2_30Wt->AddElement(elC, 0.5025); Ti3C2O2_30Wt->AddElement(elH, 0.0261); Ti3C2O2_30Wt->AddElement(elS, 0.2075); Ti3C2O2_30Wt->AddElement(elTi, 0.2158); Ti3C2O2_30Wt->AddElement(elO, 0.0481);

    // 8. Pure NIST Calibration Materials
    nist->FindOrBuildMaterial("G4_Pb");
    nist->FindOrBuildMaterial("G4_W");

    fCurrentMaterial = PPS_0Wt;
}

G4VPhysicalVolume* DetectorConstruction::ConstructVolumes()
{
    G4NistManager* nist = G4NistManager::Instance();
    G4Material* galactic = nist->FindOrBuildMaterial("G4_Galactic"); 

    // Phase I: Perfect Vacuum World
    G4Box* solidWorld = new G4Box("World", 25.*cm, 25.*cm, 25.*cm);
    G4LogicalVolume* logicWorld = new G4LogicalVolume(solidWorld, galactic, "World");
    G4VPhysicalVolume* physWorld = new G4PVPlacement(0, G4ThreeVector(), logicWorld, "World", 0, false, 0, true);

    // The Target Disc
    G4Tubs* solidTarget = new G4Tubs("Target", 0., 2.5*cm, fTargetThickness/2.0, 0., 360.*deg);
    fTargetLogical = new G4LogicalVolume(solidTarget, fCurrentMaterial, "Target");
    fTargetPhysical = new G4PVPlacement(0, G4ThreeVector(0,0,0), fTargetLogical, "Target", logicWorld, false, 0, true);

    // Phase I: Perfect Virtual Detector Plane
    G4Box* solidDetector = new G4Box("Detector", 5.*cm, 5.*cm, 0.1*mm);
    fDetectorLogical = new G4LogicalVolume(solidDetector, galactic, "Detector");
    new G4PVPlacement(0, G4ThreeVector(0, 0, 5.0*cm), fDetectorLogical, "Detector", logicWorld, false, 0, true);

    return physWorld;
}

void DetectorConstruction::SetTargetMaterial(G4String materialName)
{
    G4Material* pttoMaterial = G4Material::GetMaterial(materialName);
    if (pttoMaterial) {
        fCurrentMaterial = pttoMaterial;
        if (fTargetLogical) {
            fTargetLogical->SetMaterial(fCurrentMaterial);
            G4RunManager::GetRunManager()->GeometryHasBeenModified();
            G4cout << "Target material swapped to: " << materialName << G4endl;
        }
    } else {
        G4cerr << "WARNING: Material " << materialName << " not found!" << G4endl;
    }
}

void DetectorConstruction::SetTargetThickness(G4double thickness)
{
    fTargetThickness = thickness;
    if (fTargetLogical) {
        G4Tubs* newSolid = new G4Tubs("Target", 0., 2.5*cm, fTargetThickness/2.0, 0., 360.*deg);
        fTargetLogical->SetSolid(newSolid);
        G4RunManager::GetRunManager()->GeometryHasBeenModified();
        G4cout << "Target thickness changed to: " << thickness/mm << " mm" << G4endl;
    }
}
