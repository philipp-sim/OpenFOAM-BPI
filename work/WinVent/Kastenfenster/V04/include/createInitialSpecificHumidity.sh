#!/bin/bash

scriptDir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FILE="$scriptDir/../constant/initialisationConditions"
TMPFILE="$(mktemp)" 

clean_number() {
    echo "$1" | sed 's/;.*//' | sed 's/\/\/.*//' | tr -d '[:space:]'
}

calc_specificHumidity() {
    local T_K=$1
    local relHum=$2

    local T_C=$(echo "$T_K - 273.15" | bc -l)
    local p_sat=$(echo "610.78 * e((17.27 * $T_C)/($T_C + 237.3))" | bc -l)
    local P=101325
    local q_s=$(echo "(0.622 * $p_sat) / ($P - $p_sat)" | bc -l)

    echo "$(echo "$relHum * $q_s" | bc -l)"
}

calc_CO2relativdensity() {
    local CO2_ppm=$1
    local T_K=$2
    local P=101325
    local M_CO2=0.04401
    local R=8.314

    if [[ -z "$CO2_ppm" ]]; then
        echo "0"
        return
    fi

    local xCO2=$(echo "$CO2_ppm / 1000000" | bc -l)
    echo "$(echo "($P * $xCO2 * $M_CO2) / ($R * $T_K)" | bc -l)"
}

currentBlock=""
T_val=""
relHum_val=""
inBlock=0
declare -a blockLines=()

while IFS= read -r line; do
    trimmedLine="$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"

    if [[ "$currentBlock" == "" && "$trimmedLine" =~ ^[a-zA-Z0-9_]+$ ]]; then
        currentBlock="$trimmedLine"
        T_val=""
        relHum_val=""
        CO2_val=""
        inBlock=0
        blockLines=()
        echo "$line" >> "$TMPFILE"
        continue
    fi

    if [[ "$currentBlock" != "" && "$trimmedLine" == "{" ]]; then
        inBlock=1
        blockLines+=("$line")
        continue
    fi

    if [[ $inBlock -eq 1 ]]; then

        if [[ "$trimmedLine" =~ ^T[[:space:]]+(.+) ]]; then
            T_val="${BASH_REMATCH[1]}"
        elif [[ "$trimmedLine" =~ ^relHumidity[[:space:]]+(.+) ]]; then
            relHum_val="${BASH_REMATCH[1]}"
        elif [[ "$trimmedLine" =~ ^CO2[[:space:]]+(.+) ]]; then
            CO2_val="${BASH_REMATCH[1]}"
        fi


        if [[ "$trimmedLine" == "}" ]]; then
           
            # Remove any existing specificHumidity or CO2relativdensity definitions before adding new ones
            filteredLines=()
            for l in "${blockLines[@]}"; do
                if [[ ! "$l" =~ ^[[:space:]]*specificHumidity ]] && [[ ! "$l" =~ ^[[:space:]]*CO2relativdensity ]]; then
                    filteredLines+=("$l")
                fi
            done

            if [[ -n "$T_val" && -n "$relHum_val" ]]; then
                T_clean=$(clean_number "$T_val")
                relHum_clean=$(clean_number "$relHum_val")
                specHum=$(calc_specificHumidity "$T_clean" "$relHum_clean")
                filteredLines+=("        specificHumidity    $(printf "%.5f" "$specHum");")
            fi

            if [[ -n "$CO2_val" && -n "$T_val" ]]; then
                CO2_clean=$(clean_number "$CO2_val")
                T_clean=$(clean_number "$T_val")
                # echo "Found CO2 in block $currentBlock: $CO2_clean"
                # echo "  → Cleaned CO2 value: $CO2_clean"
                # echo "  → Temperature in Kelvin: $T_clean"
                relCO2=$(calc_CO2relativdensity "$CO2_clean" "$T_clean")
                # echo "  → Converted to CO2relativdensity: $(printf "%.7f" "$relCO2")"
                filteredLines+=("        CO2relativdensity   $(printf "%.7f" "$relCO2");")
            fi

            filteredLines+=("$line")
        
            for outLine in "${filteredLines[@]}"; do
                echo "$outLine" >> "$TMPFILE"
            done

            currentBlock=""
            inBlock=0
            T_val=""
            relHum_val=""
            CO2_val=""
            blockLines=()
            continue
        fi

        blockLines+=("$line")
        continue
    fi

    echo "$line" >> "$TMPFILE"

done < "$FILE"


mv "$TMPFILE" "$FILE"
echo -e "File $FILE has been updated. \n"