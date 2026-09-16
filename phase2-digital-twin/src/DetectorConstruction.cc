#include "DetectorConstruction.hh"

#include "G4RunManager.hh"
#include "G4NistManager.hh"
#include "G4Box.hh"
#include "G4Tubs.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"
#include "G4GenericMessenger.hh"
#include "G4Material.hh"
#include "G4Element.hh"

// ═══════════════════════════════════════════════════════════════════════════
//  LAB-CONFIGURABLE GEOMETRY PARAMETERS
//  All dimensions marked [LAB] must be confirmed against the real lab setup
//  before the final 996-run campaign. Only these constants need changing —
//  all derived positions update automatically.
// ═══════════════════════════════════════════════════════════════════════════
static constexpr G4double SSD_CM           = 10.0;  // cm  source-to-sample dist  [LAB]
static constexpr G4double SRC_COLL_HALF_XY = 5.0;   // cm  source collimator XY   [LAB]
static constexpr G4double SRC_COLL_HALF_Z  = 2.5;   // cm  source collimator Z/2  [LAB]
static constexpr G4double SRC_BORE_R       = 1.5;   // mm  bore radius (3 mm diam)[LAB]
static constexpr G4double SAMPLE_R         = 2.5;   // cm  sample disc radius      [LAB]
static constexpr G4double MID_COLL_Z_CENTER= 2.5;   // cm  mid-coll centre         [LAB]
static constexpr G4double MID_COLL_HALF_XY = 5.0;   // cm                          [LAB]
static constexpr G4double MID_COLL_HALF_Z  = 1.5;   // cm                          [LAB]
static constexpr G4double MID_BORE_R       = 2.5;   // mm                          [LAB]
static constexpr G4double DET_FACE_Z       = 5.0;   // cm  sample-to-det face dist [LAB]
static constexpr G4double CRYSTAL_R        = 3.81;  // cm  NaI crystal radius      [LAB]
static constexpr G4double CRYSTAL_HALF_L   = 3.81;  // cm  NaI crystal half-length [LAB]
static constexpr G4double CASTLE_PB_WALL   = 5.0;   // cm  Pb castle wall thick.   [LAB]


DetectorConstruction::DetectorConstruction()
: G4VUserDetectorConstruction(),
  fTargetLogical(nullptr), fTargetPhysical(nullptr),
  fCurrentSolid(nullptr),
  fMaterialName("PPS_0Wt"),
  fTargetThickness(2.0*mm)
{
    fMessenger = new G4GenericMessenger(this, "/shielding/", "Target control");
    fMessenger->DeclareMethod("setMaterial",  &DetectorConstruction::SetTargetMaterial,
                              "Set target material (G4_AIR for baseline)");
    fMessenger->DeclareMethodWithUnit("setThickness", "mm",
                              &DetectorConstruction::SetTargetThickness,
                              "Set target thickness in mm");
}

DetectorConstruction::~DetectorConstruction() { delete fMessenger; }

G4VPhysicalVolume* DetectorConstruction::Construct() {
    DefineMaterials();
    return ConstructVolumes();
}

// ─────────────────────────────────────────────────────────────────────────────
void DetectorConstruction::DefineMaterials()
{
    G4NistManager* nist = G4NistManager::Instance();

    // ── Elements ──────────────────────────────────────────────────────────
    G4Element* elC  = nist->FindOrBuildElement("C");
    G4Element* elH  = nist->FindOrBuildElement("H");
    G4Element* elS  = nist->FindOrBuildElement("S");
    G4Element* elPb = nist->FindOrBuildElement("Pb");
    G4Element* elW  = nist->FindOrBuildElement("W");
    G4Element* elTi = nist->FindOrBuildElement("Ti");
    G4Element* elO  = nist->FindOrBuildElement("O");
    G4Element* elBa = nist->FindOrBuildElement("Ba");  // for BaSO4 composites
    G4Element* elBi = nist->FindOrBuildElement("Bi");  // for Bi2O3 composites

    // ══════════════════════════════════════════════════════════
    // PURE PPS — (C6H4S)n, density 1.35 g/cm³
    // ══════════════════════════════════════════════════════════
    G4Material* PPS_0Wt = new G4Material("PPS_0Wt", 1.3500*g/cm3, 3);
    PPS_0Wt->AddElement(elC, 0.6663);
    PPS_0Wt->AddElement(elH, 0.0373);
    PPS_0Wt->AddElement(elS, 0.2964);

    // ══════════════════════════════════════════════════════════
    // Pb / PPS COMPOSITES
    // Density: 1/ρ = wPb/11.35 + wPPS/1.35
    // ══════════════════════════════════════════════════════════
    G4Material* Pb_5Wt  = new G4Material("Pb_5Wt",  1.4122*g/cm3, 4);
    Pb_5Wt->AddElement(elC,0.6330); Pb_5Wt->AddElement(elH,0.0354);
    Pb_5Wt->AddElement(elS,0.2816); Pb_5Wt->AddElement(elPb,0.0500);

    G4Material* Pb_10Wt = new G4Material("Pb_10Wt", 1.4804*g/cm3, 4);
    Pb_10Wt->AddElement(elC,0.5997); Pb_10Wt->AddElement(elH,0.0336);
    Pb_10Wt->AddElement(elS,0.2668); Pb_10Wt->AddElement(elPb,0.1000);

    G4Material* Pb_15Wt = new G4Material("Pb_15Wt", 1.5556*g/cm3, 4);
    Pb_15Wt->AddElement(elC,0.5664); Pb_15Wt->AddElement(elH,0.0317);
    Pb_15Wt->AddElement(elS,0.2519); Pb_15Wt->AddElement(elPb,0.1500);

    G4Material* Pb_20Wt = new G4Material("Pb_20Wt", 1.6387*g/cm3, 4);
    Pb_20Wt->AddElement(elC,0.5330); Pb_20Wt->AddElement(elH,0.0298);
    Pb_20Wt->AddElement(elS,0.2371); Pb_20Wt->AddElement(elPb,0.2000);

    G4Material* Pb_25Wt = new G4Material("Pb_25Wt", 1.7313*g/cm3, 4);
    Pb_25Wt->AddElement(elC,0.4997); Pb_25Wt->AddElement(elH,0.0280);
    Pb_25Wt->AddElement(elS,0.2223); Pb_25Wt->AddElement(elPb,0.2500);

    G4Material* Pb_30Wt = new G4Material("Pb_30Wt", 1.8350*g/cm3, 4);
    Pb_30Wt->AddElement(elC,0.4664); Pb_30Wt->AddElement(elH,0.0261);
    Pb_30Wt->AddElement(elS,0.2075); Pb_30Wt->AddElement(elPb,0.3000);

    // ══════════════════════════════════════════════════════════
    // W / PPS COMPOSITES
    // Density: 1/ρ = wW/19.25 + wPPS/1.35
    // ══════════════════════════════════════════════════════════
    G4Material* W_5Wt  = new G4Material("W_5Wt",  1.4158*g/cm3, 4);
    W_5Wt->AddElement(elC,0.6330); W_5Wt->AddElement(elH,0.0354);
    W_5Wt->AddElement(elS,0.2816); W_5Wt->AddElement(elW,0.0500);

    G4Material* W_10Wt = new G4Material("W_10Wt", 1.4884*g/cm3, 4);
    W_10Wt->AddElement(elC,0.5997); W_10Wt->AddElement(elH,0.0336);
    W_10Wt->AddElement(elS,0.2668); W_10Wt->AddElement(elW,0.1000);

    G4Material* W_15Wt = new G4Material("W_15Wt", 1.5688*g/cm3, 4);
    W_15Wt->AddElement(elC,0.5664); W_15Wt->AddElement(elH,0.0317);
    W_15Wt->AddElement(elS,0.2519); W_15Wt->AddElement(elW,0.1500);

    G4Material* W_20Wt = new G4Material("W_20Wt", 1.6584*g/cm3, 4);
    W_20Wt->AddElement(elC,0.5330); W_20Wt->AddElement(elH,0.0298);
    W_20Wt->AddElement(elS,0.2371); W_20Wt->AddElement(elW,0.2000);

    G4Material* W_25Wt = new G4Material("W_25Wt", 1.7589*g/cm3, 4);
    W_25Wt->AddElement(elC,0.4997); W_25Wt->AddElement(elH,0.0280);
    W_25Wt->AddElement(elS,0.2223); W_25Wt->AddElement(elW,0.2500);

    G4Material* W_30Wt = new G4Material("W_30Wt", 1.8723*g/cm3, 4);
    W_30Wt->AddElement(elC,0.4664); W_30Wt->AddElement(elH,0.0261);
    W_30Wt->AddElement(elS,0.2075); W_30Wt->AddElement(elW,0.3000);

    // ══════════════════════════════════════════════════════════
    // Ti3C2O2 (MXene) / PPS COMPOSITES
    // MXene MW = 3×47.867 + 2×12.011 + 2×15.999 = 199.621 g/mol
    // ══════════════════════════════════════════════════════════
    G4Material* Ti_5Wt  = new G4Material("Ti3C2O2_5Wt",  1.4027*g/cm3, 5);
    Ti_5Wt->AddElement(elC,0.6390); Ti_5Wt->AddElement(elH,0.0354);
    Ti_5Wt->AddElement(elS,0.2816); Ti_5Wt->AddElement(elTi,0.0360);
    Ti_5Wt->AddElement(elO,0.0080);

    G4Material* Ti_10Wt = new G4Material("Ti3C2O2_10Wt", 1.4597*g/cm3, 5);
    Ti_10Wt->AddElement(elC,0.6117); Ti_10Wt->AddElement(elH,0.0336);
    Ti_10Wt->AddElement(elS,0.2668); Ti_10Wt->AddElement(elTi,0.0719);
    Ti_10Wt->AddElement(elO,0.0160);

    G4Material* Ti_15Wt = new G4Material("Ti3C2O2_15Wt", 1.5216*g/cm3, 5);
    Ti_15Wt->AddElement(elC,0.5844); Ti_15Wt->AddElement(elH,0.0317);
    Ti_15Wt->AddElement(elS,0.2519); Ti_15Wt->AddElement(elTi,0.1079);
    Ti_15Wt->AddElement(elO,0.0240);

    G4Material* Ti_20Wt = new G4Material("Ti3C2O2_20Wt", 1.5889*g/cm3, 5);
    Ti_20Wt->AddElement(elC,0.5571); Ti_20Wt->AddElement(elH,0.0298);
    Ti_20Wt->AddElement(elS,0.2371); Ti_20Wt->AddElement(elTi,0.1439);
    Ti_20Wt->AddElement(elO,0.0321);

    G4Material* Ti_25Wt = new G4Material("Ti3C2O2_25Wt", 1.6625*g/cm3, 5);
    Ti_25Wt->AddElement(elC,0.5298); Ti_25Wt->AddElement(elH,0.0280);
    Ti_25Wt->AddElement(elS,0.2223); Ti_25Wt->AddElement(elTi,0.1799);
    Ti_25Wt->AddElement(elO,0.0401);

    G4Material* Ti_30Wt = new G4Material("Ti3C2O2_30Wt", 1.7432*g/cm3, 5);
    Ti_30Wt->AddElement(elC,0.5025); Ti_30Wt->AddElement(elH,0.0261);
    Ti_30Wt->AddElement(elS,0.2075); Ti_30Wt->AddElement(elTi,0.2158);
    Ti_30Wt->AddElement(elO,0.0481);

    // ══════════════════════════════════════════════════════════
    // BaSO4 / PPS COMPOSITES  (5–30 wt% BaSO4 in PPS matrix)
    //
    // BaSO4: Ba(137.327) + S(32.065) + 4×O(16.000) = 233.392 g/mol
    // ρ(BaSO4) = 4.50 g/cm³ (literature, barite)
    //
    // Elemental fractions in BaSO4:
    //   Ba = 0.5884,  S = 0.1374,  O = 0.2742
    //
    // Composite density: 1/ρ = w/4.50 + (1-w)/1.35
    //
    // NOTE: Total S = S from PPS + S from BaSO4 (combined as one element).
    //       O in composites comes entirely from BaSO4 (PPS has no O).
    //       Fractions are quoted to four decimals and a few sets sum to
    //       1.0000 +/- 0.0001, which Geant4 renormalises with a warning.
    // ══════════════════════════════════════════════════════════

    G4Material* BaSO4_5Wt  = new G4Material("BaSO4_5Wt",  1.3990*g/cm3, 5);
    BaSO4_5Wt->AddElement(elC,  0.6330);
    BaSO4_5Wt->AddElement(elH,  0.0354);
    BaSO4_5Wt->AddElement(elS,  0.2885);   // 0.95×0.2964 + 0.05×0.1374
    BaSO4_5Wt->AddElement(elBa, 0.0294);   // 0.05×0.5884
    BaSO4_5Wt->AddElement(elO,  0.0137);   // 0.05×0.2742

    G4Material* BaSO4_10Wt = new G4Material("BaSO4_10Wt", 1.4516*g/cm3, 5);
    BaSO4_10Wt->AddElement(elC,  0.5997);
    BaSO4_10Wt->AddElement(elH,  0.0336);
    BaSO4_10Wt->AddElement(elS,  0.2805);
    BaSO4_10Wt->AddElement(elBa, 0.0588);
    BaSO4_10Wt->AddElement(elO,  0.0274);

    G4Material* BaSO4_15Wt = new G4Material("BaSO4_15Wt", 1.5084*g/cm3, 5);
    BaSO4_15Wt->AddElement(elC,  0.5664);
    BaSO4_15Wt->AddElement(elH,  0.0317);
    BaSO4_15Wt->AddElement(elS,  0.2725);
    BaSO4_15Wt->AddElement(elBa, 0.0883);
    BaSO4_15Wt->AddElement(elO,  0.0411);

    G4Material* BaSO4_20Wt = new G4Material("BaSO4_20Wt", 1.5698*g/cm3, 5);
    BaSO4_20Wt->AddElement(elC,  0.5331);
    BaSO4_20Wt->AddElement(elH,  0.0298);
    BaSO4_20Wt->AddElement(elS,  0.2646);
    BaSO4_20Wt->AddElement(elBa, 0.1177);
    BaSO4_20Wt->AddElement(elO,  0.0548);

    G4Material* BaSO4_25Wt = new G4Material("BaSO4_25Wt", 1.6364*g/cm3, 5);
    BaSO4_25Wt->AddElement(elC,  0.4997);
    BaSO4_25Wt->AddElement(elH,  0.0280);
    BaSO4_25Wt->AddElement(elS,  0.2566);
    BaSO4_25Wt->AddElement(elBa, 0.1471);
    BaSO4_25Wt->AddElement(elO,  0.0686);

    G4Material* BaSO4_30Wt = new G4Material("BaSO4_30Wt", 1.7089*g/cm3, 5);
    BaSO4_30Wt->AddElement(elC,  0.4664);
    BaSO4_30Wt->AddElement(elH,  0.0261);
    BaSO4_30Wt->AddElement(elS,  0.2487);
    BaSO4_30Wt->AddElement(elBa, 0.1765);
    BaSO4_30Wt->AddElement(elO,  0.0823);

    // ══════════════════════════════════════════════════════════
    // Bi2O3 / PPS COMPOSITES  (5–30 wt% Bi2O3 in PPS matrix)
    //
    // Bi2O3: 2×Bi(208.980) + 3×O(16.000) = 465.960 g/mol
    // ρ(Bi2O3) = 8.90 g/cm³ (literature, monoclinic α-phase)
    //
    // Elemental fractions in Bi2O3:
    //   Bi = 0.8970,  O = 0.1030
    //
    // Composite density: 1/ρ = w/8.90 + (1-w)/1.35
    //
    // NOTE: O in composites comes entirely from Bi2O3 (PPS has no O).
    //       Bi is unique to this composite family — no cross-contamination.
    //       Fractions are quoted to four decimals and a few sets sum to
    //       1.0000 +/- 0.0001, which Geant4 renormalises with a warning.
    // ══════════════════════════════════════════════════════════

    G4Material* Bi2O3_5Wt  = new G4Material("Bi2O3_5Wt",  1.4098*g/cm3, 5);
    Bi2O3_5Wt->AddElement(elC,  0.6329);
    Bi2O3_5Wt->AddElement(elH,  0.0354);
    Bi2O3_5Wt->AddElement(elS,  0.2816);
    Bi2O3_5Wt->AddElement(elBi, 0.0449);   // 0.05×0.8970
    Bi2O3_5Wt->AddElement(elO,  0.0052);   // 0.05×0.1030

    G4Material* Bi2O3_10Wt = new G4Material("Bi2O3_10Wt", 1.4751*g/cm3, 5);
    Bi2O3_10Wt->AddElement(elC,  0.5996);
    Bi2O3_10Wt->AddElement(elH,  0.0336);
    Bi2O3_10Wt->AddElement(elS,  0.2668);
    Bi2O3_10Wt->AddElement(elBi, 0.0897);
    Bi2O3_10Wt->AddElement(elO,  0.0103);

    G4Material* Bi2O3_15Wt = new G4Material("Bi2O3_15Wt", 1.5468*g/cm3, 5);
    Bi2O3_15Wt->AddElement(elC,  0.5664);
    Bi2O3_15Wt->AddElement(elH,  0.0317);
    Bi2O3_15Wt->AddElement(elS,  0.2519);
    Bi2O3_15Wt->AddElement(elBi, 0.1345);
    Bi2O3_15Wt->AddElement(elO,  0.0155);

    G4Material* Bi2O3_20Wt = new G4Material("Bi2O3_20Wt", 1.6258*g/cm3, 5);
    Bi2O3_20Wt->AddElement(elC,  0.5331);
    Bi2O3_20Wt->AddElement(elH,  0.0298);
    Bi2O3_20Wt->AddElement(elS,  0.2371);
    Bi2O3_20Wt->AddElement(elBi, 0.1794);
    Bi2O3_20Wt->AddElement(elO,  0.0206);

    G4Material* Bi2O3_25Wt = new G4Material("Bi2O3_25Wt", 1.7134*g/cm3, 5);
    Bi2O3_25Wt->AddElement(elC,  0.4997);
    Bi2O3_25Wt->AddElement(elH,  0.0280);
    Bi2O3_25Wt->AddElement(elS,  0.2223);
    Bi2O3_25Wt->AddElement(elBi, 0.2242);
    Bi2O3_25Wt->AddElement(elO,  0.0258);

    G4Material* Bi2O3_30Wt = new G4Material("Bi2O3_30Wt", 1.8109*g/cm3, 5);
    Bi2O3_30Wt->AddElement(elC,  0.4664);
    Bi2O3_30Wt->AddElement(elH,  0.0261);
    Bi2O3_30Wt->AddElement(elS,  0.2075);
    Bi2O3_30Wt->AddElement(elBi, 0.2691);
    Bi2O3_30Wt->AddElement(elO,  0.0309);

    // ── NIST pure materials ────────────────────────────────────────────────
    nist->FindOrBuildMaterial("G4_Pb");           // pure lead reference, ρ=11.35 g/cm³
    nist->FindOrBuildMaterial("G4_W");            // pure tungsten reference, ρ=19.30 g/cm³
    nist->FindOrBuildMaterial("G4_AIR");          // baseline (transparent disc)
    nist->FindOrBuildMaterial("G4_Al");           // detector housing
    nist->FindOrBuildMaterial("G4_Cu");           // graded-Z Cu lining
    nist->FindOrBuildMaterial("G4_Sn");           // graded-Z Sn lining
    nist->FindOrBuildMaterial("G4_SODIUM_IODIDE");// NaI crystal
}

// ─────────────────────────────────────────────────────────────────────────────
G4VPhysicalVolume* DetectorConstruction::ConstructVolumes()
{
    G4NistManager* nist = G4NistManager::Instance();
    G4Material* air    = nist->FindOrBuildMaterial("G4_AIR");
    G4Material* lead   = nist->FindOrBuildMaterial("G4_Pb");
    G4Material* alum   = nist->FindOrBuildMaterial("G4_Al");
    G4Material* copper = nist->FindOrBuildMaterial("G4_Cu");
    G4Material* tin    = nist->FindOrBuildMaterial("G4_Sn");
    G4Material* NaI    = nist->FindOrBuildMaterial("G4_SODIUM_IODIDE");

    // ── Resolve target material from stored name ───────────────────────────
    G4Material* targetMat = G4Material::GetMaterial(fMaterialName);
    if (!targetMat) {
        G4cerr << "\n[FATAL] Material '" << fMaterialName << "' not found.\n"
               << "  Valid names: PPS_0Wt | G4_Pb | G4_W | G4_AIR\n"
               << "  | Pb_5Wt..Pb_30Wt | W_5Wt..W_30Wt\n"
               << "  | Ti3C2O2_5Wt..Ti3C2O2_30Wt\n"
               << "  | BaSO4_5Wt..BaSO4_30Wt\n"
               << "  | Bi2O3_5Wt..Bi2O3_30Wt\n";
        targetMat = air;  // safe fallback — not silently wrong
    }
    G4cout << "  [DetectorConstruction] Target → " << targetMat->GetName()
           << "  ρ=" << targetMat->GetDensity()/(g/cm3) << " g/cm³"
           << "  t=" << fTargetThickness/mm << " mm" << G4endl;

    // ── Derived positions ──────────────────────────────────────────────────
    const G4double SRC_COLL_Z    = -(SSD_CM/2.0)*cm;                        // -5.0 cm
    const G4double WIN_CENTER_Z  = (DET_FACE_Z + 0.025)*cm;                 //  5.025 cm
    const G4double CRYS_CENTER_Z = (DET_FACE_Z + 0.05 + CRYSTAL_HALF_L)*cm;// 8.86 cm
    const G4double CASTLE_CENTER_Z = CRYS_CENTER_Z;
    const G4double CASTLE_HALF_Z   = CRYSTAL_HALF_L*cm;
    const G4double CASTLE_INNER_R  = (CRYSTAL_R + 0.10 + 0.05 + 0.10)*cm;  // 4.06 cm
    const G4double CASTLE_OUTER_R  = CASTLE_INNER_R + CASTLE_PB_WALL*cm;   // 9.06 cm

    // ── World ──────────────────────────────────────────────────────────────
    G4Box* solidWorld = new G4Box("World", 15.*cm, 15.*cm, 15.*cm);
    G4LogicalVolume* logicWorld = new G4LogicalVolume(solidWorld, air, "World");
    G4VPhysicalVolume* physWorld = new G4PVPlacement(
        0, G4ThreeVector(), logicWorld, "World", nullptr, false, 0, true);

    // ── Source collimator ──────────────────────────────────────────────────
    G4Box* solidPbBlock = new G4Box("SourceColl",
                                    SRC_COLL_HALF_XY*cm,
                                    SRC_COLL_HALF_XY*cm,
                                    SRC_COLL_HALF_Z*cm);
    G4LogicalVolume* logicPbBlock = new G4LogicalVolume(solidPbBlock, lead, "SourceColl");
    new G4PVPlacement(0, G4ThreeVector(0, 0, SRC_COLL_Z),
                      logicPbBlock, "SourceColl", logicWorld, false, 0, true);

    // Air bore — placed at LOCAL origin of Pb block
    G4Tubs* solidBore = new G4Tubs("SourceBore", 0., SRC_BORE_R*mm,
                                   SRC_COLL_HALF_Z*cm, 0., 360.*deg);
    G4LogicalVolume* logicBore = new G4LogicalVolume(solidBore, air, "SourceBore");
    new G4PVPlacement(0, G4ThreeVector(0, 0, 0),
                      logicBore, "SourceBore", logicPbBlock, false, 0, true);

    // ── Target disc ────────────────────────────────────────────────────────
    fCurrentSolid = new G4Tubs("Target", 0., SAMPLE_R*cm,
                                fTargetThickness/2., 0., 360.*deg);
    fTargetLogical  = new G4LogicalVolume(fCurrentSolid, targetMat, "Target");
    fTargetPhysical = new G4PVPlacement(0, G4ThreeVector(0, 0, 0),
                      fTargetLogical, "Target", logicWorld, false, 0, true);

    // Al sample holder (annular ring around disc — beam doesn't touch it)
    G4Tubs* solidHolder = new G4Tubs("SampleHolder",
                                     SAMPLE_R*cm, (SAMPLE_R+1.0)*cm,
                                     1.0*mm, 0., 360.*deg);
    G4LogicalVolume* logicHolder = new G4LogicalVolume(solidHolder, alum, "SampleHolder");
    new G4PVPlacement(0, G4ThreeVector(0, 0, 0),
                      logicHolder, "SampleHolder", logicWorld, false, 0, true);

    // ── Intermediate collimator ────────────────────────────────────────────
    G4Box* solidMidBlock = new G4Box("MidColl",
                                     MID_COLL_HALF_XY*cm,
                                     MID_COLL_HALF_XY*cm,
                                     MID_COLL_HALF_Z*cm);
    G4LogicalVolume* logicMidBlock = new G4LogicalVolume(solidMidBlock, lead, "MidColl");
    new G4PVPlacement(0, G4ThreeVector(0, 0, MID_COLL_Z_CENTER*cm),
                      logicMidBlock, "MidColl", logicWorld, false, 0, true);

    G4Tubs* solidMidBore = new G4Tubs("MidBore", 0., MID_BORE_R*mm,
                                      MID_COLL_HALF_Z*cm, 0., 360.*deg);
    G4LogicalVolume* logicMidBore = new G4LogicalVolume(solidMidBore, air, "MidBore");
    new G4PVPlacement(0, G4ThreeVector(0, 0, 0),
                      logicMidBore, "MidBore", logicMidBlock, false, 0, true);

    // ── Detector assembly ──────────────────────────────────────────────────
    // Graded-Z order from detector outward: Al → Cu → Sn → Pb
    // X-rays from Pb travel INWARD, hitting Sn first (correct order):
    //   Pb K X-rays(~75 keV) → Sn absorbs → Sn K X-rays(~25 keV) → Cu absorbs
    //   Cu K X-rays(~8 keV) → too soft to reach crystal, absorbed in Al/NaI

    // Al entrance window
    G4Tubs* solidWindow = new G4Tubs("DetWindow", 0., CRYSTAL_R*cm,
                                     0.25*mm, 0., 360.*deg);
    G4LogicalVolume* logicWindow = new G4LogicalVolume(solidWindow, alum, "DetWindow");
    new G4PVPlacement(0, G4ThreeVector(0, 0, WIN_CENTER_Z),
                      logicWindow, "DetWindow", logicWorld, false, 0, true);

    // NaI crystal — active scoring volume (energy deposited here → spectrum)
    G4Tubs* solidCrystal = new G4Tubs("NaICrystal", 0., CRYSTAL_R*cm,
                                      CRYSTAL_HALF_L*cm, 0., 360.*deg);
    G4LogicalVolume* logicCrystal = new G4LogicalVolume(solidCrystal, NaI, "NaICrystal");
    new G4PVPlacement(0, G4ThreeVector(0, 0, CRYS_CENTER_Z),
                      logicCrystal, "NaICrystal", logicWorld, false, 0, true);

    // Al lateral housing — 1 mm wall
    G4Tubs* solidAlHousing = new G4Tubs("AlHousing",
                                        CRYSTAL_R*cm, (CRYSTAL_R+0.10)*cm,
                                        CRYSTAL_HALF_L*cm, 0., 360.*deg);
    G4LogicalVolume* logicAlHousing = new G4LogicalVolume(solidAlHousing, alum, "AlHousing");
    new G4PVPlacement(0, G4ThreeVector(0, 0, CRYS_CENTER_Z),
                      logicAlHousing, "AlHousing", logicWorld, false, 0, true);

    // Cu graded-Z lining — 0.5 mm
    G4Tubs* solidCu = new G4Tubs("CuLining",
                                  (CRYSTAL_R+0.10)*cm, (CRYSTAL_R+0.15)*cm,
                                  CRYSTAL_HALF_L*cm, 0., 360.*deg);
    G4LogicalVolume* logicCu = new G4LogicalVolume(solidCu, copper, "CuLining");
    new G4PVPlacement(0, G4ThreeVector(0, 0, CRYS_CENTER_Z),
                      logicCu, "CuLining", logicWorld, false, 0, true);

    // Sn graded-Z lining — 1.0 mm
    G4Tubs* solidSn = new G4Tubs("SnLining",
                                  (CRYSTAL_R+0.15)*cm, (CRYSTAL_R+0.25)*cm,
                                  CRYSTAL_HALF_L*cm, 0., 360.*deg);
    G4LogicalVolume* logicSn = new G4LogicalVolume(solidSn, tin, "SnLining");
    new G4PVPlacement(0, G4ThreeVector(0, 0, CRYS_CENTER_Z),
                      logicSn, "SnLining", logicWorld, false, 0, true);

    // Pb castle — 50 mm lateral wall
    G4Tubs* solidCastle = new G4Tubs("PbCastle",
                                     CASTLE_INNER_R, CASTLE_OUTER_R,
                                     CASTLE_HALF_Z, 0., 360.*deg);
    G4LogicalVolume* logicCastle = new G4LogicalVolume(solidCastle, lead, "PbCastle");
    new G4PVPlacement(0, G4ThreeVector(0, 0, CASTLE_CENTER_Z),
                      logicCastle, "PbCastle", logicWorld, false, 0, true);

    return physWorld;
}

// ─────────────────────────────────────────────────────────────────────────────
void DetectorConstruction::SetTargetMaterial(G4String name)
{
    fMaterialName = name;
    G4cout << "  [setMaterial] Stored: '" << name << "'" << G4endl;
    if (fTargetLogical) {
        G4Material* mat = G4Material::GetMaterial(name);
        if (mat) {
            fTargetLogical->SetMaterial(mat);
            G4RunManager::GetRunManager()->GeometryHasBeenModified();
        }
    }
}

void DetectorConstruction::SetTargetThickness(G4double thickness)
{
    fTargetThickness = thickness;
    if (fTargetLogical) {
        G4Tubs* newSolid = new G4Tubs("Target", 0., SAMPLE_R*cm,
                                      fTargetThickness/2., 0., 360.*deg);
        fCurrentSolid = newSolid;
        fTargetLogical->SetSolid(fCurrentSolid);
        G4RunManager::GetRunManager()->GeometryHasBeenModified();
        G4cout << "  [setThickness] " << thickness/mm << " mm" << G4endl;
    }
}
