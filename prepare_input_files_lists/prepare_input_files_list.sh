#!/bin/bash

dataset_directory=${HOME}/nobackup/SVJ/store/datasets
dataset_config=dataset_configs.t_channel_datasets_paths
module=analysis_configs.t_channel_pre_selection
selection_name=t_channel_pre_selection
year=2018

dataset_names=(
    #
    # Signals
    #
    t-channel_mMed-600_mDark-20_rinv-0p3_alpha-peak_yukawa-1
    t-channel_mMed-800_mDark-20_rinv-0p3_alpha-peak_yukawa-1
    t-channel_mMed-1000_mDark-20_rinv-0p3_alpha-peak_yukawa-1
    t-channel_mMed-1500_mDark-20_rinv-0p3_alpha-peak_yukawa-1
    t-channel_mMed-2000_mDark-1_rinv-0p3_alpha-peak_yukawa-1
    t-channel_mMed-2000_mDark-50_rinv-0p3_alpha-peak_yukawa-1
    t-channel_mMed-2000_mDark-100_rinv-0p3_alpha-peak_yukawa-1
    t-channel_mMed-2000_mDark-20_rinv-0p1_alpha-peak_yukawa-1
    t-channel_mMed-2000_mDark-20_rinv-0p3_alpha-peak_yukawa-1
    t-channel_mMed-2000_mDark-20_rinv-0p5_alpha-peak_yukawa-1
    t-channel_mMed-2000_mDark-20_rinv-0p7_alpha-peak_yukawa-1
    t-channel_mMed-3000_mDark-20_rinv-0p3_alpha-peak_yukawa-1
    t-channel_mMed-4000_mDark-20_rinv-0p3_alpha-peak_yukawa-1
    #
    # Backgrounds
    #
    # QCD
    #
    QCD_Pt_170to300
    QCD_Pt_300to470
    QCD_Pt_470to600
    QCD_Pt_600to800
    QCD_Pt_800to1000
    #QCD_Pt_1000to1400
    QCD_Pt_1400to1800
    QCD_Pt_1800to2400
    QCD_Pt_2400to3200
    QCD_Pt_3200toInf
    #
    # TTJets
    #
    TTJets
    TTJets_HT-600to800
    TTJets_HT-800to1200
    TTJets_HT-1200to2500
    TTJets_HT-2500toInf
)

prepare_input_files_list() {

    local dataset_config=$1
    local dataset_directory=$2
    local module=$3
    local selection_name=$4
    local year=$5
    local dataset_name=$6

    echo ""
    echo "Preparing input files for dataset ${dataset_name} year ${year} and selection ${selection_name}"

    python list_dataset_files.py -d ${dataset_name} -y ${year} -c ${dataset_config} -o ${dataset_directory} 
    python compute_unweighted_selection_efficiency.py -d ${dataset_name} -y ${year} -p ${module} -s ${selection_name} -i ${dataset_directory} -o ${dataset_directory} -n 6 -e futures -c 10000
    python prepare_input_files_list.py -d ${dataset_name} -y ${year} -s ${selection_name} -i ${dataset_directory} -o ${dataset_directory}
}


for dataset_name in ${dataset_names[@]}; do

    prepare_input_files_list ${dataset_config} ${dataset_directory} ${module} ${selection_name} ${year} ${dataset_name}

done
