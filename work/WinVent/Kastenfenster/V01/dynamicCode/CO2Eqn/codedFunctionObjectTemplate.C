/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Copyright (C) YEAR OpenFOAM Foundation
     \\/     M anipulation  |
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

\*---------------------------------------------------------------------------*/

#include "codedFunctionObjectTemplate.H"
#include "volFields.H"
#include "read.H"
#include "addToRunTimeSelectionTable.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

defineTypeNameAndDebug(CO2EqnFunctionObject, 0);

addRemovableToRunTimeSelectionTable
(
    functionObject,
    CO2EqnFunctionObject,
    dictionary
);


// * * * * * * * * * * * * * * * Global Functions  * * * * * * * * * * * * * //

extern "C"
{
    // dynamicCode:
    // SHA1 = a6e86895a3cb37bb582c8eaef3a8dae46d995f90
    //
    // unique function name that can be checked if the correct library version
    // has been loaded
    void CO2Eqn_a6e86895a3cb37bb582c8eaef3a8dae46d995f90(bool load)
    {
        if (load)
        {
            // code that can be explicitly executed after loading
        }
        else
        {
            // code that can be explicitly executed before unloading
        }
    }
}


// * * * * * * * * * * * * * * * Local Functions * * * * * * * * * * * * * * //

//{{{ begin localCode

//}}} end localCode


// * * * * * * * * * * * * * Private Member Functions  * * * * * * * * * * * //

const fvMesh& CO2EqnFunctionObject::mesh() const
{
    return refCast<const fvMesh>(obr_);
}


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

CO2EqnFunctionObject::CO2EqnFunctionObject
(
    const word& name,
    const Time& runTime,
    const dictionary& dict
)
:
    functionObjects::regionFunctionObject(name, runTime, dict)
{
    read(dict);
}


// * * * * * * * * * * * * * * * * Destructor  * * * * * * * * * * * * * * * //

CO2EqnFunctionObject::~CO2EqnFunctionObject()
{}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

bool CO2EqnFunctionObject::read(const dictionary& dict)
{
    if (false)
    {
        Info<<"read CO2Eqn sha1: a6e86895a3cb37bb582c8eaef3a8dae46d995f90\n";
    }

//{{{ begin code
    
//}}} end code

    return true;
}


Foam::wordList CO2EqnFunctionObject::fields() const
{
    if (false)
    {
        Info<<"fields CO2Eqn sha1: a6e86895a3cb37bb582c8eaef3a8dae46d995f90\n";
    }

    wordList fields;
//{{{ begin code
    
//}}} end code

    return fields;
}


bool CO2EqnFunctionObject::execute()
{
    if (false)
    {
        Info<<"execute CO2Eqn sha1: a6e86895a3cb37bb582c8eaef3a8dae46d995f90\n";
    }

//{{{ begin code
    #line 38 "/home/ubuntu/mnt/work/validation/V03/system/functions/CO2Eqn"
auto ensureFieldExists = [&](const word& name, const dimensionSet& dims)
        {
            if (!mesh().objectRegistry::foundObject<volScalarField>(name))
            {
                Info << "Creating " << name << " field" << endl;
                auto* ptr = new volScalarField(
                    IOobject(name, mesh().time().name(), mesh(), IOobject::READ_IF_PRESENT, IOobject::AUTO_WRITE),
                    mesh(),
                    dimensionedScalar(name, dims, 0.0)
                );
                mesh().objectRegistry::store(ptr);
            }
        };

        IOdictionary physicalProperties
        (
            IOobject
            (
                "physicalProperties",
                mesh().time().constant(),
                mesh(),
                IOobject::MUST_READ,
                IOobject::NO_WRITE
            )
        );

        ensureFieldExists("CO2", dimensionSet(0,0,0,0,0,0,0));
        ensureFieldExists("Y_CO2", dimensionSet(0,0,0,0,0,0,0));
        //ensureFieldExists("CO2relativdensity", dimensionSet(1,-3,0,0,0,0,0));
        //volScalarField& CO2relativdensity = mesh().lookupObjectRef<volScalarField>("CO2relativdensity");
        volScalarField& CO2 = mesh().lookupObjectRef<volScalarField>("CO2");
        volScalarField& Y_CO2 = mesh().lookupObjectRef<volScalarField>("Y_CO2");
        const volScalarField& T = mesh().lookupObject<volScalarField>("T");
        const volVectorField& U = mesh().lookupObject<volVectorField>("U");
        //const volScalarField& rho = mesh().lookupObject<volScalarField>("rho");
        //const surfaceScalarField& phi = mesh().lookupObject<surfaceScalarField>("phi");
        const Foam::fvModels& fvModels(Foam::fvModels::New(this->mesh()));
        const Foam::fvConstraints& fvConstraints(Foam::fvConstraints::New(this->mesh()));
        const dimensionedScalar D_CO2(physicalProperties.lookup("D_CO2"));

        const dimensionedScalar P("P", dimensionSet(1, -1, -2, 0, 0, 0, 0), 101325);// Pa standard atmosphere pressure
        const dimensionedScalar Rm("Rm", dimensionSet(1, 2, -2, -1 , -1, 0, 0), 8.314);// J/(mol*K) universal gas constant
        const dimensionedScalar M_C("M_C", dimensionSet(1, 0, 0, 0, -1, 0, 0), 12.0107e-3); // kg/mol
        const dimensionedScalar M_N("M_N", dimensionSet(1, 0, 0, 0, -1, 0, 0), 14.0067e-3); // kg/mol
        const dimensionedScalar M_O("M_O", dimensionSet(1, 0, 0, 0, -1, 0, 0), 15.9994e-3); // kg/mol
        const dimensionedScalar M_Ar("M_Ar", dimensionSet(1, 0, 0, 0, -1, 0, 0), 39.948e-3); // kg/mol 
        
        

        dimensionedScalar M_CO2 = M_C + 2 * M_O; // kg/mol
        volScalarField M_Air = 2 * M_N * 0.78 + 2 * M_O * (0.21 - CO2/1e6) + M_Ar * 0.01 + M_CO2 * (CO2/1e6); // kg/mol
        //volScalarField M_Air = M_N * 0.78 + M_O * (0.21 - CO2/1e6) + M_Ar * 0.01 + M_CO2 * (CO2/1e6); // kg/mol
        volScalarField Mol_co2_part =  M_CO2 * (CO2 / 1e6); // kg/mol Part from M_Air
        tmp<volScalarField> rho_mix = (M_Air * P) / (Rm * T); // kg/m³ mixture

        //Y_CO2 = ((CO2/1e6)*M_CO2)/((CO2/1e6)*M_CO2 + (1-CO2/1e6)*M_Air); // mass fraction of CO2 in the mixture
        //tmp<volScalarField> rho_co2 = (M_CO2 * P) / (Rm * T); // kg/m³ CO2
        //CO2relativdensity = (P * Mol_co2_part) / (Rm * T); // kg/m³ CO2 mass from mixture 

        volScalarField rho_co2
        (
            IOobject
            (
                "rho_co2",
                mesh().time().constant(),
                mesh(),
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            (M_CO2 * P) / (Rm * T)
        );

        surfaceScalarField phi_co2 = fvc::interpolate(rho_co2) * fvc::interpolate(U) & mesh().Sf(); // phi = rho_humair * U
        // phi_co2 problematic bec. mass flux is not mass constant

        //surfaceScalarField phi_diff("phi_diff", phi_co2 - phi);
        //scalar diffNorm = gSum(phi_diff);
        //Info << "Flux magnitude difference between phi_co2 and phi = " << diffNorm << endl;
        //Info << "Total flux magnitude difference between phi_co2 and phi = " << diffNorm << endl;

        fvScalarMatrix CO2Eqn =
            fvm::ddt(rho_co2, Y_CO2)
            + fvm::div(phi_co2, Y_CO2,"div(phi,CO2)")
            - fvm::laplacian(rho_co2*D_CO2, Y_CO2)
            == fvModels.source(rho_co2, Y_CO2);
            
        fvConstraints.constrain(CO2Eqn);
        CO2Eqn.relax();
        CO2Eqn.solve();
        fvConstraints.constrain(Y_CO2);
        //scalar totalMassCO2 = gSum(Y_CO2 * rho_co2 * mesh().V());
        //Info << "Total CO2 mass = " << totalMassCO2 << endl;


        //Y_CO2 = ((CO2/1e6)*M_CO2)/((CO2/1e6)*M_CO2 + (1-CO2/1e6)*M_Air);
        CO2 = (Y_CO2*M_Air) / (M_CO2*(1-Y_CO2) + Y_CO2*M_Air) * 1e6; // molar fraction of CO2 in the mixture * 1e6 to get ppm
        CO2.correctBoundaryConditions();


        const label nCells = returnReduce(CO2.internalField().size(), sumOp<label>());

        if (mesh().time().writeTime())
        {
            Info << "D_CO2: " << D_CO2.value() << endl;
            Info << "Cell count: " << nCells << endl;
            Info << "CO2 avg: " << gSum(CO2) / nCells << endl;
            Info << "Y_CO2 avg: " << gSum(Y_CO2) / nCells << endl;
        }
//}}} end code

    return true;
}


bool CO2EqnFunctionObject::write()
{
    if (false)
    {
        Info<<"write CO2Eqn sha1: a6e86895a3cb37bb582c8eaef3a8dae46d995f90\n";
    }

//{{{ begin code
    
//}}} end code

    return true;
}


bool CO2EqnFunctionObject::end()
{
    if (false)
    {
        Info<<"end CO2Eqn sha1: a6e86895a3cb37bb582c8eaef3a8dae46d995f90\n";
    }

//{{{ begin code
    
//}}} end code

    return true;
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// ************************************************************************* //

