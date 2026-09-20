#include "PrimaryGeneratorAction.hh"

#include "G4ParticleGun.hh"
#include "G4ParticleTable.hh"
#include "G4ParticleDefinition.hh"
#include "G4SystemOfUnits.hh"

PrimaryGeneratorAction::PrimaryGeneratorAction()
: G4VUserPrimaryGeneratorAction(), fParticleGun(nullptr)
{
    fParticleGun = new G4ParticleGun(1);

    G4ParticleDefinition* gamma =
        G4ParticleTable::GetParticleTable()->FindParticle("gamma");

    fParticleGun->SetParticleDefinition(gamma);

    // Source position: on Z-axis, 10 cm behind the sample disc
    // The source collimator block spans z = -7.5 cm to -2.5 cm, so the gun sits
  // 2.5 cm of air upstream of its rear face.
    fParticleGun->SetParticlePosition(G4ThreeVector(0., 0., -10.*cm));

    // Pencil beam along +Z axis.
    // In good-geometry experiments the collimator bore defines the beam;
    // the pencil-beam approximation is valid because the bore (3 mm) is
    // centred on-axis and the source sits at its entrance.
    fParticleGun->SetParticleMomentumDirection(G4ThreeVector(0., 0., 1.));

    // Default energy — overridden by /gun/energy in the macro each run
    fParticleGun->SetParticleEnergy(662.*keV);
}

PrimaryGeneratorAction::~PrimaryGeneratorAction() {
    delete fParticleGun;
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* anEvent) {
    fParticleGun->GeneratePrimaryVertex(anEvent);
}
