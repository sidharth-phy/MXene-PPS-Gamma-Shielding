#include "EventAction.hh"
#include "RunAction.hh"

#include "G4Event.hh"
#include "G4SystemOfUnits.hh"
#include "Randomize.hh"

#include <cmath>

EventAction::EventAction()
: G4UserEventAction(), fEdepNaI(0.) {}

EventAction::~EventAction() {}

void EventAction::BeginOfEventAction(const G4Event*)
{
    fEdepNaI = 0.;
}

void EventAction::EndOfEventAction(const G4Event*)
{
    // Nothing to record if no energy was deposited in the crystal
    if (fEdepNaI <= 0.) return;

    // ── NaI(Tl) Gaussian Energy Broadening ────────────────────────────────
    // In a real scintillator detector, the energy resolution results from
    // statistical fluctuations in photon yield and PMT gain.
    //
    // Empirical NaI(Tl) resolution (Saint-Gobain 3"×3"):
    //   FWHM(E) = a × √E   where a = 2.06 keV^0.5
    //   This gives  R = FWHM/E = 8.0% at 662 keV  (validated value)
    //               R = 27%  at  59.5 keV           (realistic for NaI)
    //               R = 6.0% at 1173 keV
    //
    // sigma = FWHM / 2.355

    G4double E_keV    = fEdepNaI / keV;
    if (E_keV < 0.5) return;                   // Below minimum recordable energy

    G4double fwhm_keV  = 2.06 * std::sqrt(E_keV);
    G4double sigma_keV = fwhm_keV / 2.355;

    // Gaussian smear — this is what the MCA records
    G4double blurred_keV = G4RandGauss::shoot(E_keV, sigma_keV);

    // Convert to integer bin (1 keV per bin)
    G4int bin = static_cast<G4int>(blurred_keV);

    // Thread-safe fill into the spectrum histogram
    RunAction::FillSpectrum(bin);
}
