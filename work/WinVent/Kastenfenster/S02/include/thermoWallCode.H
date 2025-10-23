#ifndef thermoWallCode_H
#define thermoWallCode_H

#include "fvPatchField.H"
#include "volFields.H"
#include "dictionary.H"
#include <cmath>





/*void updateThermoWall(Foam::fvPatchScalarField& patchField)
{
    using namespace Foam;

    // Namespace für scalarField ist Foam::scalarField
    scalarField& field = patchField;

    forAll(field, i)
    {
        field[i] = 500.0;
    }
}*/


//void updateThermoWall(Foam::fvPatchScalarField& patchField)

void updateThermoWall(Foam::fvPatchScalarField& patchField, const Foam::scalar rho, const Foam::scalar cp, const Foam::scalar d)
{
    using namespace Foam;
    scalar dt = patchField.db().time().deltaTValue(); // timestep
    scalarField& field = patchField;
    const scalarField& internalT = patchField.internalField();
    const labelUList& faceCells = patchField.patch().faceCells(); 
    const scalarField& faceAreas = patchField.patch().magSf();
    const vectorField& faceNormals = patchField.patch().Sf(); 
    const volVectorField& Ufield = patchField.db().lookupObject<volVectorField>("U");

    //static const scalar rho     = 20; //2000.0;     // [kg/m³] concrete density
    //static const scalar cp      = 100; //1000.0;     // [J/kgK]  specific heat
    //static const scalar d       = 0.2;       // [m]      wall thickness

    static const scalar k_air   = 0.025;      // [W/mK]   air thermal conductivity
    static const scalar p_air   = 1.225;      // [kg/m³]  air density
    static const scalar cp_air  = 1003.5;     // [J/kgK]  air cp
    static const scalar mu_air  = 1.48e-5;    // [m2/s]   dynamic viscosity

    static const scalar a_air   = k_air / (p_air * cp_air);  // thermal diffusivity
    static const scalar Pr_air  = mu_air / a_air;            // Prandtl number

    forAll(faceCells, i)
    {
        label cellI = faceCells[i];
        scalar Tcell  = internalT[cellI];
        scalar Tpatch = field[i];
        scalar deltaTemp = Tpatch - Tcell;

        vector Ucell = Ufield[cellI]; // u from cell
        scalar Un = (Ucell & faceNormals[i]) / faceAreas[i]; //dot product
        scalar U = mag(Un); //flow speed (m/s)

        scalar Lc = faceAreas[i]; // convection Characteristic length is area
        scalar Re = (p_air * U * Lc) / mu_air; //Reynolds number
        scalar Nu = 0.332 * std::pow(Re, 0.5) * std::pow(Pr_air, 1.0 / 3.0);
        scalar hc_air = Nu * k_air / Lc;

        scalar Qdot_dt = hc_air * faceAreas[i] * deltaTemp * dt; // heat exchange
        scalar m = rho * d * faceAreas[i];                       // wall mass
        scalar Q = m * cp * Tpatch;                              // wall heat content

        field[i] = (Q - Qdot_dt) / (m * cp);                     // updated temperature
    }
}

#endif