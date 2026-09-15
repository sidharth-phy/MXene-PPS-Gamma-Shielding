#include "PrimaryGeneratorAction.hh"
#include "G4ParticleGun.hh"
#include "G4ParticleTable.hh"
#include "G4ParticleDefinition.hh"
#include "G4SystemOfUnits.hh"

PrimaryGeneratorAction::PrimaryGeneratorAction() : G4VUserPrimaryGeneratorAction(), fParticleGun(0) {
    fParticleGun = new G4ParticleGun(1);
    
    G4ParticleTable* particleTable = G4ParticleTable::GetParticleTable();
    G4ParticleDefinition* particle = particleTable->FindParticle("gamma");
    
    fParticleGun->SetParticleDefinition(particle);
    // Fire from 10 cm away, perfectly straight down the Z-axis (Pencil Beam)
    fParticleGun->SetParticlePosition(G4ThreeVector(0., 0., -10.*cm));
    fParticleGun->SetParticleMomentumDirection(G4ThreeVector(0., 0., 1.));
    
    // Default energy (Will be safely overridden by Python macro)
    fParticleGun->SetParticleEnergy(59.5*keV); 
}

PrimaryGeneratorAction::~PrimaryGeneratorAction() {
    delete fParticleGun;
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* anEvent) {
    fParticleGun->GeneratePrimaryVertex(anEvent);
}
