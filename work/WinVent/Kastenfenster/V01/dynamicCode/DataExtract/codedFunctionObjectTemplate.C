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

defineTypeNameAndDebug(DataExtractFunctionObject, 0);

addRemovableToRunTimeSelectionTable
(
    functionObject,
    DataExtractFunctionObject,
    dictionary
);


// * * * * * * * * * * * * * * * Global Functions  * * * * * * * * * * * * * //

extern "C"
{
    // dynamicCode:
    // SHA1 = 0ae777a90e9ee978561550b3de303efe164d6b28
    //
    // unique function name that can be checked if the correct library version
    // has been loaded
    void DataExtract_0ae777a90e9ee978561550b3de303efe164d6b28(bool load)
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

const fvMesh& DataExtractFunctionObject::mesh() const
{
    return refCast<const fvMesh>(obr_);
}


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

DataExtractFunctionObject::DataExtractFunctionObject
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

DataExtractFunctionObject::~DataExtractFunctionObject()
{}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

bool DataExtractFunctionObject::read(const dictionary& dict)
{
    if (false)
    {
        Info<<"read DataExtract sha1: 0ae777a90e9ee978561550b3de303efe164d6b28\n";
    }

//{{{ begin code
    
//}}} end code

    return true;
}


Foam::wordList DataExtractFunctionObject::fields() const
{
    if (false)
    {
        Info<<"fields DataExtract sha1: 0ae777a90e9ee978561550b3de303efe164d6b28\n";
    }

    wordList fields;
//{{{ begin code
    
//}}} end code

    return fields;
}


bool DataExtractFunctionObject::execute()
{
    if (false)
    {
        Info<<"execute DataExtract sha1: 0ae777a90e9ee978561550b3de303efe164d6b28\n";
    }

//{{{ begin code
    #line 193 "/home/ubuntu/mnt/work/validation/V03/system/functions/DataExtract"
auto extractFieldData = [&](const word& fieldName, const vector& lower, const vector& upper, const scalar& roundedTime)
        {
            const fvMesh& mesh = this->mesh();
            const pointField& centres = mesh.C();
            bool isParallel = (Pstream::parRun() && Pstream::nProcs() > 1);

            fileName mergedDir = mesh.time().globalPath() / "postProcess" / fieldName;
            mkDir(mergedDir);
            fileName mergedOutputPath = mergedDir / "Data";
            if (roundedTime == 0 && isFile(mergedOutputPath))
            {
                std::remove(mergedOutputPath.c_str());
            }

            fileName procOutputPath;
            if (isParallel)
            {
                procOutputPath = mesh.time().path() / (fieldName + "_" + Foam::name(roundedTime) + "_proc" + Foam::name(Pstream::myProcNo()));
            }
            else
            {
                procOutputPath = mergedDir / Foam::name(roundedTime);
            }

            if (isFile(procOutputPath))
            {
                std::remove(procOutputPath.c_str());
            }

            std::ostringstream buffer;

            if (mesh.foundObject<volScalarField>(fieldName))
            {
                const volScalarField& field = mesh.lookupObject<volScalarField>(fieldName);
                buffer << "x,y,z," << fieldName << "\n";

                forAll(field, cellI)
                {
                    const point& p = centres[cellI];
                    if ((p.x() >= lower.x() && p.x() <= upper.x()) &&
                        (p.y() >= lower.y() && p.y() <= upper.y()) &&
                        (p.z() >= lower.z() && p.z() <= upper.z()))
                    {
                        scalar val = field[cellI];
                        buffer << p.x() << "," << p.y() << "," << p.z() << "," << val << "\n";
                    }
                }
            }
            else if (mesh.foundObject<volVectorField>(fieldName))
            {
                const volVectorField& field = mesh.lookupObject<volVectorField>(fieldName);
                buffer << "x,y,z," << fieldName << "_x," << fieldName << "_y," << fieldName << "_z," << fieldName << "_mag\n";

                forAll(field, cellI)
                {
                    const point& p = centres[cellI];
                    if ((p.x() >= lower.x() && p.x() <= upper.x()) &&
                        (p.y() >= lower.y() && p.y() <= upper.y()) &&
                        (p.z() >= lower.z() && p.z() <= upper.z()))
                    {
                        const vector& val = field[cellI];
                        buffer << p.x() << "," << p.y() << "," << p.z() << ","
                               << val.x() << "," << val.y() << "," << val.z() << ","
                               << mag(val) << "\n";
                    }
                }
            }
            else
            {
                Info << "Field " << fieldName << " not found or unsupported type." << endl;
                return true;
            }

            std::ofstream output(procOutputPath.c_str());
            output << buffer.str();
            output.close();

            Info << fieldName << " values written to " << procOutputPath << endl;

            if (isParallel)
            {
                scalar dummy = 0;
                Pstream::scatter(dummy);

                if (Pstream::myProcNo() == 0)
                {
                    std::ofstream merged(mergedOutputPath.c_str(), std::ios::app);
                    merged << "Timestep" << Foam::name(roundedTime) << "\n";

                    for (int procNo = 0; procNo < Pstream::nProcs(); ++procNo)
                    {
                        fileName procDir = mesh.time().globalPath() / ("processor" + Foam::name(procNo));
                        fileName filePath = procDir / (fieldName + "_" + Foam::name(roundedTime) + "_proc" + Foam::name(procNo));
                        const int maxWaitMs = 1000;
                        bool fileAvailable = false;
                        for (int waitMs = 0; waitMs < maxWaitMs; ++waitMs)
                        {
                            if (isFile(filePath))
                            {
                                fileAvailable = true;
                                break;
                            }
                            std::this_thread::sleep_for(std::chrono::milliseconds(1));
                        }

                        if (fileAvailable)
                        {
                            std::ifstream fin(filePath.c_str());
                            std::string line;
                            bool firstLine = true;
                            while (std::getline(fin, line))
                            {
                                if (firstLine) { firstLine = false; continue; }
                                merged << "\"" << line << "\"\n";
                            }
                            fin.close();
                            std::remove(filePath.c_str());
                        }
                        else
                        {
                            Info << "Missing file from processor" << procNo << ": " << filePath << endl;
                        }
                    }

                    merged.close();
                    Info << "Appended data block for time " << roundedTime << " to " << mergedOutputPath << endl;
                }
            }
            else
            {
                std::ifstream fin(procOutputPath.c_str());
                std::ofstream merged(mergedOutputPath.c_str(), std::ios::app);
                std::string line;
                bool firstLine = true;

                merged << Foam::name(roundedTime) << "\n";

                while (std::getline(fin, line))
                {
                    if (firstLine) { firstLine = false; continue; }
                    merged << "\"" << line << "\"\n";
                }

                fin.close();
                merged.close();
                std::remove(procOutputPath.c_str());
                Info << "Appended data block for time " << roundedTime << " to " << mergedOutputPath << " (serial mode)" << endl;
            }

            return true;
        };

        //--------------------------------------------------------

        struct SliceIntersection
        {
            label cellId;                    // ID der geschnittenen Zelle
            vector centroid;                 // Zentroid der Schnittfläche
            scalar area;                     // Fläche der Schnittfläche
            vector normal;                   // Normale der Schnittfläche
            label neighborCellId;            // ID der Nachbarzelle auf der anderen Seite
            scalar distance;                 // Abstand vom Zellzentrum zur Slice
            scalar ownerWeight;              // Gewichtung für Owner-Zelle
            scalar neighborWeight;           // Gewichtung für Neighbor-Zelle
        };

        auto calculateSliceIntersections = [&](const vector& slicePoint, const vector& sliceNormal) -> std::vector<SliceIntersection>
        {
            std::vector<SliceIntersection> intersections;
            const fvMesh& mesh = this->mesh();
            const scalar tolerance = 1e-10;
            
            Info << "Calculating slice intersections (one-time calculation)" << endl;
            Info << "Slice point: " << slicePoint << ", Normal: " << sliceNormal << endl;
            
            forAll(mesh.C(), cellI)
            {
                const cell& cellFaces = mesh.cells()[cellI];
                
                // Prüfe ob Zelle die Slice-Ebene schneidet
                scalar minDistance = GREAT;
                scalar maxDistance = -GREAT;
                
                // Berechne Distanzen aller Zellpunkte zur Slice-Ebene
                forAll(cellFaces, fI)
                {
                    label faceI = cellFaces[fI];
                    const face& f = mesh.faces()[faceI];
                    forAll(f, pointI)
                    {
                        const point& p = mesh.points()[f[pointI]];
                        scalar dist = (p - slicePoint) & sliceNormal;
                        minDistance = min(minDistance, dist);
                        maxDistance = max(maxDistance, dist);
                    }
                }
                
                // Zelle schneidet Slice wenn min und max unterschiedliche Vorzeichen haben
                bool cellIntersectsSlice = (minDistance <= tolerance && maxDistance >= -tolerance);
                
                if (cellIntersectsSlice)
                {
                    // Sammle eindeutige Schnittpunkte von Zellkanten mit der Slice-Ebene
                    DynamicList<point> intersectionPoints;
                    
                    // Sammle alle eindeutigen Kanten der Zelle
                    labelHashSet processedEdges;
                    
                    forAll(cellFaces, fI)
                    {
                        label faceI = cellFaces[fI];
                        const face& f = mesh.faces()[faceI];
                        
                        forAll(f, edgeI)
                        {
                            label p1 = f[edgeI];
                            label p2 = f[(edgeI + 1) % f.size()];
                            
                            // Erstelle eindeutige Kanten-ID (kleinerer Index zuerst)
                            label minP = min(p1, p2);
                            label maxP = max(p1, p2);
                            label edgeHash = minP * mesh.nPoints() + maxP;
                            
                            if (!processedEdges.found(edgeHash))
                            {
                                processedEdges.insert(edgeHash);
                                
                                const point& pt1 = mesh.points()[p1];
                                const point& pt2 = mesh.points()[p2];
                                
                                scalar d1 = (pt1 - slicePoint) & sliceNormal;
                                scalar d2 = (pt2 - slicePoint) & sliceNormal;
                                
                                // Prüfe ob Kante die Slice schneidet (unterschiedliche Vorzeichen der Distanzen)
                                if (d1 * d2 <= 0 && mag(d1 - d2) > tolerance)
                                {
                                    scalar t = d1 / (d1 - d2);
                                    t = max(0.0, min(1.0, t));
                                    point intersection = pt1 + t * (pt2 - pt1);
                                    intersectionPoints.append(intersection);
                                }
                            }
                        }
                    }
                    
                    // Berechne Fläche nur wenn mindestens 3 Punkte vorhanden
                    if (intersectionPoints.size() >= 3)
                    {
                        // Berechne Zentroid
                        vector centroid = vector::zero;
                        forAll(intersectionPoints, pI)
                        {
                            centroid += intersectionPoints[pI];
                        }
                        centroid /= intersectionPoints.size();
                        
                        // Sortiere Punkte um den Zentroid für korrekte Triangulation
                        // Projiziere auf Slice-Ebene und sortiere nach Winkel
                        vector u = vector(1,0,0);
                        if (mag(u & sliceNormal) > 0.9) u = vector(0,1,0);
                        u = u - (u & sliceNormal) * sliceNormal;
                        u /= mag(u);
                        vector v = sliceNormal ^ u;
                        
                        // Sortiere Punkte nach Winkel
                        for (label i = 0; i < intersectionPoints.size() - 1; i++)
                        {
                            for (label j = i + 1; j < intersectionPoints.size(); j++)
                            {
                                vector r1 = intersectionPoints[i] - centroid;
                                vector r2 = intersectionPoints[j] - centroid;
                                scalar angle1 = atan2(r1 & v, r1 & u);
                                scalar angle2 = atan2(r2 & v, r2 & u);
                                if (angle1 > angle2)
                                {
                                    point temp = intersectionPoints[i];
                                    intersectionPoints[i] = intersectionPoints[j];
                                    intersectionPoints[j] = temp;
                                }
                            }
                        }
                        
                        // Berechne Fläche durch Triangulation vom Zentroid aus
                        scalar totalArea = 0.0;
                        for (label i = 0; i < intersectionPoints.size(); i++)
                        {
                            label nextI = (i + 1) % intersectionPoints.size();
                            vector v1 = intersectionPoints[i] - centroid;
                            vector v2 = intersectionPoints[nextI] - centroid;
                            scalar triangleArea = 0.5 * mag(v1 ^ v2);
                            totalArea += triangleArea;
                        }
                        
                        label neighborCellId = -1;
                        scalar minFaceToSliceDist = GREAT;
                        
                        forAll(cellFaces, fI)
                        {
                            label faceI = cellFaces[fI];
                            if (mesh.isInternalFace(faceI))
                            {
                                label ownCell = mesh.faceOwner()[faceI];
                                label neiCell = mesh.faceNeighbour()[faceI];
                                label otherCell = (ownCell == cellI) ? neiCell : ownCell;
                                
                                scalar otherCellDist = (mesh.C()[otherCell] - slicePoint) & sliceNormal;
                                scalar currentCellDist = (mesh.C()[cellI] - slicePoint) & sliceNormal;
                                
                                // Nachbarzelle muss auf der anderen Seite der Slice liegen
                                if ((otherCellDist * currentCellDist) < 0)
                                {
                                    // Berechne Distanz des Face-Zentrums zur Slice
                                    vector faceCentre = mesh.Cf()[faceI];
                                    scalar faceToSliceDist = mag((faceCentre - slicePoint) & sliceNormal);
                                    
                                    // Wähle die Face, die am nächsten zur Slice liegt
                                    if (faceToSliceDist < minFaceToSliceDist)
                                    {
                                        minFaceToSliceDist = faceToSliceDist;
                                        neighborCellId = otherCell;
                                    }
                                }
                            }
                        }
                        
                        // Berechne Distanz und Gewichtungen für Interpolation
                        scalar cellDistance = mag((mesh.C()[cellI] - slicePoint) & sliceNormal);
                        scalar ownerWeight = 1.0;
                        scalar neighborWeight = 0.0;
                        
                        if (neighborCellId != -1)
                        {
                            scalar neighborDistance = mag((mesh.C()[neighborCellId] - slicePoint) & sliceNormal);
                            scalar totalDistance = cellDistance + neighborDistance;
                            if (totalDistance > tolerance)
                            {
                                // Inverse Distanz-Gewichtung: Je näher zur Slice, desto höher das Gewicht
                                // ownerWeight sollte HÖHER sein wenn cellDistance KLEINER ist
                                ownerWeight = neighborDistance / totalDistance;
                                neighborWeight = cellDistance / totalDistance;
                            }
                        }
                        
                        // Speichere Intersection-Information
                        SliceIntersection intersection;
                        intersection.cellId = cellI;
                        intersection.centroid = centroid;
                        intersection.area = totalArea;
                        intersection.normal = sliceNormal;
                        intersection.neighborCellId = neighborCellId;
                        intersection.distance = cellDistance;
                        intersection.ownerWeight = ownerWeight;
                        intersection.neighborWeight = neighborWeight;
                        
                        intersections.push_back(intersection);
                    }
                }
            }
            
            // Summiere Statistiken über alle Prozesse
            scalar totalArea = 0.0;
            scalar maxArea = 0.0;
            scalar minArea = GREAT;
            forAll(intersections, i)
            {
                totalArea += intersections[i].area;
                maxArea = max(maxArea, intersections[i].area);
                minArea = min(minArea, intersections[i].area);
            }
            
            reduce(totalArea, sumOp<scalar>());
            reduce(maxArea, maxOp<scalar>());
            reduce(minArea, minOp<scalar>());
            label globalIntersections = returnReduce(intersections.size(), sumOp<label>());
            
            Info << "Found " << globalIntersections << " slice intersections globally" << endl;
            Info << "Total slice area: " << totalArea << " m²" << endl;
            Info << "Average area per intersection: " << (globalIntersections > 0 ? totalArea/globalIntersections : 0) << " m²" << endl;
            Info << "Min/Max intersection area: " << minArea << " / " << maxArea << " m²" << endl;
            
            return intersections;
        };


        // Statische Variablen für einmalige Berechnung
        static std::vector<SliceIntersection> staticSliceIntersections;
        static bool intersectionsCalculated = false;

        //--------------------------------------------------------
        auto extractEnergyLoss = [&](const word& direction, const vector& lower, const vector& upper, const scalar& roundedTime)
        {

            vector slicePoint = vector::zero;
            vector sliceNormal = vector::zero;

            if (direction == "x") { slicePoint = vector(lower.x(), 0, 0); sliceNormal = vector(1, 0, 0); }
            else if (direction == "y") { slicePoint = vector(0, lower.y(), 0); sliceNormal = vector(0, 1, 0); }
            else if (direction == "z") { slicePoint = vector(0, 0, lower.z()); sliceNormal = vector(0, 0, 1); }

            const fvMesh& mesh = this->mesh(); // Referenz auf das Mesh
            const volScalarField& T = mesh.lookupObject<volScalarField>("T"); // Temperaturfeld
            const volVectorField& U = mesh.lookupObject<volVectorField>("U"); // Geschwindigkeitsfeld
            const volScalarField& rho = mesh.lookupObject<volScalarField>("rho"); // Dichtefeld
            const scalar cp = 1005.0; // spezifische Wärmekapazität von Luft bei konstantem Druck in J/(kg*K)

            fileName mergedDir = mesh.time().globalPath() / "postProcess" / "EnergyLoss";
            mkDir(mergedDir); 
            fileName mergedOutputPath = mergedDir / "Data"; 
            if (roundedTime == 0 && isFile(mergedOutputPath)){std::remove(mergedOutputPath.c_str());} // Lösche existierende Datei bei t=0

            if (!intersectionsCalculated)
            {
                staticSliceIntersections = calculateSliceIntersections(slicePoint, sliceNormal);
                intersectionsCalculated = true;
                Info << "Slice intersections calculated and stored for reuse" << endl;
            }

            // Static variables für zeitgewichtete Akkumulation - persistieren zwischen Aufrufen
            static scalar totalTimeSpan = 0.0;
            static scalar totalinFlowMass = 0.0;
            static scalar totaloutFlowMass = 0.0;
            static scalar totalMassTransfer = 0.0;
            static scalar totalinFlowVolume = 0.0;
            static scalar totaloutFlowVolume = 0.0;
            static scalar totalVolumeTransfer = 0.0;
            static scalar totalinFlowEnergy = 0.0;
            static scalar totaloutFlowEnergy = 0.0;           
            static scalar totalEnergyTransfer = 0.0;
            static scalar totalWeightedCells = 0.0;
            static int iterationCount = 0;
            static bool buffersInitialized = false;
            static scalar intervalStartTime = 0.0;
            
            if (!buffersInitialized) { 
                totalTimeSpan = 0.0;
                totalMassTransfer = 0.0;
                totalVolumeTransfer = 0.0;
                totalEnergyTransfer = 0.0;
                totalWeightedCells = 0.0;
                iterationCount = 0;
                intervalStartTime = roundedTime;
                buffersInitialized = true;
            }

            scalar inFlowMass = 0.0; // Einströmende Masse (kg/s)
            scalar outFlowMass = 0.0; // Ausströmende Masse (kg/s)
            scalar inFlowVolume = 0.0; // Einströmendes Volumen (m³/s)
            scalar outFlowVolume = 0.0; // Ausströmendes Volumen (m³/s)
            scalar inFlowPower = 0.0; // Einströmende Leistung (W)
            scalar outFlowPower = 0.0; // Ausströmende Leistung (W)
            scalar inFlowEnergy = 0.0; // Einströmende Energie (J)
            scalar outFlowEnergy = 0.0; // Ausströmende Energie (J)
            scalar weightedCellCount = 0.0; // Gewichtete Anzahl der Zellen die die Slice schneiden
            scalar totalSliceArea = 0.0; // Summiere alle Schnittflächen
            scalar inFlowTemp = 0.0; // Temperatur der einströmenden Luft (K)
            scalar outFlowTemp = 0.0; // Temperatur der ausströmenden Luft
            scalar inFlowCellCount = 0.0; 
            scalar outFlowCellCount = 0.0; 

            forAll(staticSliceIntersections, intI)
            {
                const SliceIntersection& intersection = staticSliceIntersections[intI];
                totalSliceArea += intersection.area; // Addiere Fläche zur Gesamtsumme
                scalar sliceTemperature = T[intersection.cellId];
                vector sliceVelocity = U[intersection.cellId];
                scalar sliceRho = rho[intersection.cellId];

                if (intersection.neighborCellId != -1)
                {
                    scalar neighborTemp = T[intersection.neighborCellId];
                    vector neighborVel = U[intersection.neighborCellId];
                    scalar neighborRho = rho[intersection.neighborCellId];
                    // Verwende vorberechnete Gewichtungen (inverse Distanz-Gewichtung)
                    scalar ownerWeight = intersection.ownerWeight;
                    scalar neighborWeight = intersection.neighborWeight;
                    // Standard lineare Interpolation: w1*val1 + w2*val2 (w1+w2=1)
                    sliceTemperature = ownerWeight * sliceTemperature + neighborWeight * neighborTemp;
                    sliceVelocity = ownerWeight * sliceVelocity + neighborWeight * neighborVel;
                    sliceRho = ownerWeight * sliceRho + neighborWeight * neighborRho;
                }
                
                // Berechne Flüsse an der Slice-Fläche
                scalar normalVel = sliceVelocity & sliceNormal;
                //Info << "Cell " << intersection.cellId << " normal velocity: " << normalVel << " m/s, area: " << intersection.area << " m²" << endl;
                scalar effectiveArea = intersection.area;
                scalar finalVolumeFlow = normalVel * effectiveArea;  // m³/s
                scalar finalMassFlow = sliceRho * finalVolumeFlow;  // kg/s
                scalar powerFlow = finalMassFlow * cp * sliceTemperature; // Leistungsfluss (W) J/s
                scalar energyFlow = powerFlow * mesh.time().deltaTValue(); // Energiefluss pro Zeitschritt (J)
                weightedCellCount += 1.0;
                
                if (normalVel > SMALL)
                {
                    inFlowMass += finalMassFlow; 
                    inFlowVolume += finalVolumeFlow; 
                    inFlowPower += powerFlow; 
                    inFlowEnergy += energyFlow;
                    inFlowTemp += sliceTemperature * finalMassFlow; // Masse-gewichtet
                    inFlowCellCount += 1.0;
                }
                else if (normalVel < -SMALL)
                {
                    outFlowMass += mag(finalMassFlow); 
                    outFlowVolume += mag(finalVolumeFlow); 
                    outFlowPower += mag(powerFlow); 
                    outFlowEnergy += mag(energyFlow); 
                    outFlowTemp += sliceTemperature * mag(finalMassFlow); // Masse-gewichtet
                    outFlowCellCount += 1.0;
                }
            }
            
            // Summiere über alle Prozesse
            reduce(totalSliceArea, sumOp<scalar>());
            reduce(inFlowMass, sumOp<scalar>());
            reduce(outFlowMass, sumOp<scalar>());
            reduce(inFlowVolume, sumOp<scalar>());
            reduce(outFlowVolume, sumOp<scalar>());
            reduce(inFlowPower, sumOp<scalar>());
            reduce(outFlowPower, sumOp<scalar>());
            reduce(inFlowEnergy, sumOp<scalar>());
            reduce(outFlowEnergy, sumOp<scalar>());
            reduce(weightedCellCount, sumOp<scalar>());
            reduce(inFlowTemp, sumOp<scalar>());
            reduce(outFlowTemp, sumOp<scalar>());
            reduce(inFlowCellCount, sumOp<scalar>());
            reduce(outFlowCellCount, sumOp<scalar>());

            scalar massDifference = inFlowMass - outFlowMass;  
            scalar volumeDifference = inFlowVolume - outFlowVolume; 
            scalar netPowerLoss = inFlowPower - outFlowPower;
            scalar netEnergyLoss = inFlowEnergy - outFlowEnergy;
            inFlowTemp = inFlowTemp / inFlowMass;
            outFlowTemp = outFlowTemp / outFlowMass;

            scalar deltaT = mesh.time().deltaTValue();
            
            
            if (iterationCount == 0) {intervalStartTime = roundedTime;} // Startzeit des Intervalls bei der ersten Iteration
            
            totalTimeSpan += deltaT;
            totalinFlowMass += inFlowMass * deltaT;          // kg (akkumuliert)
            totaloutFlowMass += outFlowMass * deltaT;        // kg (akkumul
            totalMassTransfer += massDifference * deltaT;        // kg (akkumuliert)
            totalinFlowVolume += inFlowVolume * deltaT;      // m³ (akkumuliert)
            totaloutFlowVolume += outFlowVolume * deltaT;    // m³ (akkumuliert)
            totalVolumeTransfer += volumeDifference * deltaT;    // m³ (akkumuliert)
            totalinFlowEnergy += inFlowEnergy;                // J (bereits mit deltaT multipliziert)
            totaloutFlowEnergy += outFlowEnergy;              // J (bereits mit deltaT
            totalEnergyTransfer += netEnergyLoss;                // J (bereits mit deltaT multipliziert)
            totalWeightedCells += weightedCellCount * deltaT;    // gewichtete Zellen × Zeit
            iterationCount++;

            if (iterationCount >= 1) {
                if (Pstream::master()) {
                    scalar avginFlowMass = (totalTimeSpan > SMALL) ? totalinFlowMass / totalTimeSpan : 0.0;          // kg/s
                    scalar avgoutFlowMass = (totalTimeSpan > SMALL) ? totaloutFlowMass / totalTimeSpan : 0.0;        // kg/s
                    scalar avgMassRate = (totalTimeSpan > SMALL) ? totalMassTransfer / totalTimeSpan : 0.0;      // kg/s
                    scalar avginFlowVolume = (totalTimeSpan > SMALL) ? totalinFlowVolume / totalTimeSpan : 0.0;      // m³/s
                    scalar avgoutFlowVolume = (totalTimeSpan > SMALL) ? totaloutFlowVolume / totalTimeSpan : 0.0;    // m³/s
                    scalar avgVolumeRate = (totalTimeSpan > SMALL) ? totalVolumeTransfer / totalTimeSpan : 0.0;  // m³/s
                    scalar avginFlowPower = (totalTimeSpan > SMALL) ? totalinFlowEnergy / totalTimeSpan : 0.0;      // W
                    scalar avgoutFlowPower = (totalTimeSpan > SMALL) ? totaloutFlowEnergy / totalTimeSpan : 0.0;    // W
                    scalar avgPowerRate = (totalTimeSpan > SMALL) ? totalEnergyTransfer / totalTimeSpan : 0.0;   // W
                    scalar avgWeightedCells = (totalTimeSpan > SMALL) ? totalWeightedCells / totalTimeSpan : 0.0; // gewichtete Zellen
                    scalar intervalMidTime = intervalStartTime + (totalTimeSpan / 2.0); // Mittlere Zeit des Intervalls


                    scalar avgMass = 0.5 * (avginFlowMass + avgoutFlowMass);
                    scalar avgVolume = 0.5 * (avginFlowVolume + avgoutFlowVolume);
                    scalar avgPower = 0.5 * (avginFlowPower + avgoutFlowPower);
                    scalar avgEnergy = 0.5 * (totalinFlowEnergy + totaloutFlowEnergy);
             

                    scalar massImbalancePercent = (avgMass > SMALL) ? 100.0 * avgMassRate / avgMass : 0.0;
                    scalar volumeImbalancePercent = (avgVolume > SMALL) ? 100.0 * avgVolumeRate / avgVolume : 0.0;
                    scalar netPowerLossPercent = (avgPower > SMALL) ? 100.0 * avgPowerRate / avgPower : 0.0;
                    scalar netEnergyLossPercent = (avgEnergy > SMALL) ? 100.0 * totalEnergyTransfer / avgEnergy : 0.0;
                    
                    std::ofstream merged(mergedOutputPath.c_str(), std::ios::app);
                    merged << "Timestep " << Foam::name(intervalMidTime) 
                           << " | Total Time Span " << totalTimeSpan 
                           << " | Cells " << static_cast<int>(avgWeightedCells) << "\n"
                           << "Mass flows:\n"
                           << "  Inflow mass:     " << avginFlowMass << " kg/s\n"
                           << "  Outflow mass:    " << avgoutFlowMass << " kg/s\n" 
                           << "  Mass imbalance:  " << avgMassRate << " kg/s (" << massImbalancePercent << " %)\n"
                           << "Volume flows:\n"
                           << "  Inflow volume:   " << avginFlowVolume << " m³/s \n"
                           << "  Outflow volume:  " << avgoutFlowVolume << " m³/s \n" 
                           << "  Volume diff:     " << avgVolumeRate << " m³/s (" << volumeImbalancePercent << " %)\n"
                           << "Power flows:\n"
                           << "  Inflow power:    " << avginFlowPower << " W\n"
                           << "  Outflow power:   " << avgoutFlowPower << " W\n"
                           << "  Net power loss:  " << avgPowerRate << " W (" << netPowerLossPercent << " %)\n"
                           << "Energy flows:\n"
                           << "  Inflow energy:   " << totalinFlowEnergy << " J \n"
                           << "  Outflow energy:  " << totaloutFlowEnergy << " J \n"
                           << "  Net energy loss: " << totalEnergyTransfer << " J (" << netEnergyLossPercent << " %)\n"

                           << "Debug flows:\n"
                           << "  Inflow Temp:   " << inFlowTemp  << " K \n"               
                           << "  Outflow Temp:  " << outFlowTemp << " K \n"                        
                           << "  Net Temp loss: " << inFlowTemp - outFlowTemp << " K \n"
                           << "  Inflow mass:     " << inFlowMass * totalTimeSpan << " kg\n"
                           << "  Outflow mass:    " << outFlowMass * totalTimeSpan << " kg\n"
                           << "  Inflow Energy:     " << inFlowMass * totalTimeSpan * cp * inFlowTemp << " J\n"
                           << "  Outflow Energy:    " << outFlowMass * totalTimeSpan * cp * outFlowTemp << " J\n"
                           << "Iterations:       " << iterationCount << "\n"
                           << "Area:             " << totalSliceArea << " m²\n"
                           << "----------------------------------------\n";
                    merged.close();
                    Info << "Written time-averaged EnergyLoss data (" << iterationCount << " iterations, " 
                         << totalTimeSpan << " s) from t=" << intervalStartTime << " to t=" << roundedTime 
                         << " to " << mergedOutputPath << endl;
                }
                
                // Reset Akkumulatoren für nächstes Intervall
                totalTimeSpan = 0.0;
                totalinFlowMass = 0.0;
                totaloutFlowMass = 0.0;
                totalMassTransfer = 0.0;
                totalinFlowVolume = 0.0;
                totaloutFlowVolume = 0.0;
                totalVolumeTransfer = 0.0;
                totalinFlowEnergy = 0.0;
                totaloutFlowEnergy = 0.0;
                totalEnergyTransfer = 0.0;
                totalWeightedCells = 0.0;
                iterationCount = 0;
                intervalStartTime = roundedTime; // Neue Startzeit für nächstes Intervall
            }
        };  


        //--------------------------------------------------------
        static scalar lastWrittenTime = -1;
        scalar writeInterval = 0.1; 
        scalar time = mesh().time().value();
        int precision = std::max(0, int(-std::floor(std::log10(writeInterval) + SMALL)));
        scalar factor = std::pow(10.0, precision);
        scalar roundedTime = std::floor(time / writeInterval) * writeInterval;
        roundedTime = std::floor(roundedTime * factor + SMALL) / factor;

        if (mag(roundedTime - lastWrittenTime) > SMALL)
        {
            lastWrittenTime = roundedTime;
            Info << "Writing U, CO2 and T data for time " << roundedTime << endl;
            //extractFieldData("U", vector(0, -0.2, 0), vector(3.4, 3.3, 2.7), roundedTime);
            //extractFieldData("CO2", vector(0, -0.2, 0), vector(3.4, 3.3, 2.7), roundedTime);
            //extractFieldData("T", vector(0, -0.2, 0), vector(3.4, 3.3, 2.7), roundedTime);
            //extractFieldData("alphat", vector(0, -0.2, 0), vector(3.4, 3.3, 2.7), roundedTime);
            //extractFieldData("epsilon", vector(0, -0.2, 0), vector(3.4, 3.3, 2.7), roundedTime);
            //extractFieldData("k", vector(0, -0.2, 0), vector(3.4, 3.3, 2.7), roundedTime);
            //extractFieldData("nut", vector(0, -0.2, 0), vector(3.4, 3.3, 2.7), roundedTime);
            //extractFieldData("p", vector(0, -0.2, 0), vector(3.4, 3.3, 2.7), roundedTime);
            //extractEnergyLoss("y", vector(0.450, -0.15, 0.786), vector(1.652, 0, 2.238), roundedTime);
        }
        extractEnergyLoss("y", vector(0.531, -0.06, 0.867), vector(1.571, -0.06, 2.157), time);
//}}} end code

    return true;
}


bool DataExtractFunctionObject::write()
{
    if (false)
    {
        Info<<"write DataExtract sha1: 0ae777a90e9ee978561550b3de303efe164d6b28\n";
    }

//{{{ begin code
    
//}}} end code

    return true;
}


bool DataExtractFunctionObject::end()
{
    if (false)
    {
        Info<<"end DataExtract sha1: 0ae777a90e9ee978561550b3de303efe164d6b28\n";
    }

//{{{ begin code
    
//}}} end code

    return true;
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// ************************************************************************* //

