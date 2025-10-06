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

calc_YCO2() {
    local CO2_ppm=$1

    local M_C=0.0120107
    local M_O=0.0159994
    local M_N=0.0140067
    local M_Ar=0.039948

    #local M_CO2=$(awk "BEGIN {print $M_C + 2 * $M_O}")
    local M_CO2=$(echo "$M_C + 2 * $M_O" | bc -l)
    local M_Air=$(echo "2 * $M_N * 0.78 + 2 * $M_O * 0.21 + $M_Ar * 0.01" | bc -l)
    local x=$(echo "$CO2_ppm / 1000000" | bc -l)

    # Formel: Y = (x * M_CO2) / (x * M_CO2 + (1 - x) * M_Air)
    echo "$(echo "($x * $M_CO2) / ($x * $M_CO2 + (1 - $x) * $M_Air)" | bc -l)"
}

currentBlock=""
T_val=""
relHum_val=""
CO2_val=""
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
           
            filteredLines=()
            for l in "${blockLines[@]}"; do
                if [[ ! "$l" =~ ^[[:space:]]*specificHumidity && ! "$l" =~ ^[[:space:]]*Y_CO2 ]]; then
                    filteredLines+=("$l")
                fi
            done

            if [[ -n "$T_val" && -n "$relHum_val" ]]; then
                T_clean=$(clean_number "$T_val")
                relHum_clean=$(clean_number "$relHum_val")
                specHum=$(calc_specificHumidity "$T_clean" "$relHum_clean")
                echo "Debug: specificHumidity for T=$T_clean K and RH=$relHum_clean is $specHum"
                filteredLines+=("        specificHumidity    $specHum;")
            fi

            if [[ -n "$CO2_val" ]]; then
                CO2_clean=$(clean_number "$CO2_val")
                echo "Debug: Y_CO2 for CO2=$CO2_clean ppm is $CO2_clean"
                Y_CO2=$(calc_YCO2 "$CO2_clean")
                echo "Debug: Y_CO2 for CO2=$CO2_clean ppm is $Y_CO2"
                filteredLines+=("        Y_CO2    $Y_CO2;")
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