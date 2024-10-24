import awkward as ak

from skimmer import skimmer_utils
from utils.awkward_array_utilities import as_type
import analysis_configs.triggers as trg
from analysis_configs.met_filters import met_filters_treemaker as met_filters
from analysis_configs import objects_definition as obj
from analysis_configs import sequences


def process(events, cut_flow, year, primary_dataset="", pn_tagger=False, variation=None, **kwargs):
    """SVJ t-channel pre-selection."""

    # If this config is changed, changes must be reflected in t_channel_lost_lepton_control_region.py

    if skimmer_utils.is_data(events):
        events = sequences.remove_primary_dataset_overlap(events, year, primary_dataset)
        skimmer_utils.update_cut_flow(cut_flow, "PrimaryDatasetOvelap", events)

    events = skimmer_utils.apply_variation(events, variation)

    # Trigger event selection
    triggers = getattr(trg, f"t_channel_{year}")
    events = skimmer_utils.apply_trigger_cut(events, triggers)
    skimmer_utils.update_cut_flow(cut_flow, "Trigger", events)

    # ST cut for triggers to be fully efficient
    st = events.MET + events.HT
    events = events[st > 1300]
    skimmer_utils.update_cut_flow(cut_flow, "STGt1300GeV", events)

    # HEM veto
    if year == "2018" and skimmer_utils.is_data(events):
        ak4_jets = events.Jets
        electrons = events.Electrons
        muons = events.Muons
        jet_condition = obj.is_good_ak4_jet(ak4_jets)
        electron_condition = obj.is_veto_electron(electrons)
        muon_condition = obj.is_veto_muon(muons)
        good_ak4_jets = ak4_jets[jet_condition]
        veto_electrons = electrons[electron_condition]
        veto_muons = muons[muon_condition]
        events = skimmer_utils.apply_hem_veto(events, good_ak4_jets, veto_electrons, veto_muons)
        skimmer_utils.update_cut_flow(cut_flow, "HEMVeto", events)

    # Good jet filters
    events = sequences.apply_good_ak8_jet_filter(events)
    skimmer_utils.update_cut_flow(cut_flow, "GoodJetsAK8", events)

    # Adding JetsAK8_isGood branch already so that it can be used
    # in the rest of the pre-selection
    events = sequences.add_good_ak8_jet_branch(events)

    # Requiring at least 2 good FatJets
    filter = ak.count(events.JetsAK8.pt[events.JetsAK8.isGood], axis=1) >= 2
    events = events[filter]
    skimmer_utils.update_cut_flow(cut_flow, "nJetsAK8Gt2", events)

    # Veto events with mini-isolated leptons
    events = sequences.apply_lepton_veto(events)
    skimmer_utils.update_cut_flow(cut_flow, "LeptonVeto", events)

    # Delta phi min cut
    if len(events) != 0:
        # If needed because the selection crashes due to the special ak type
        met = skimmer_utils.make_pt_eta_phi_mass_lorentz_vector(
            pt=events.MET,
            phi=events.METPhi,
        )
        good_jets_ak8 = events.JetsAK8[events.JetsAK8.isGood]
        jets = skimmer_utils.make_pt_eta_phi_mass_lorentz_vector(
            pt=good_jets_ak8.pt,
            eta=good_jets_ak8.eta,
            phi=good_jets_ak8.phi,
            mass=good_jets_ak8.mass,
        )

        met = ak.broadcast_arrays(met, jets)[0]
        delta_phi_min = ak.min(abs(jets.delta_phi(met)), axis=1)
        filter = delta_phi_min < 1.5
        # Needed otherwise type is not defined and skim cannot be written
        filter = as_type(filter, bool)
        events = events[filter]
        
        delta_phi_min = delta_phi_min[filter]

    skimmer_utils.update_cut_flow(cut_flow, "DeltaPhiMinLt1p5", events)

    # MET cut
    events = events[events.MET > 200]
    skimmer_utils.update_cut_flow(cut_flow, "METGt200GeV", events)

    # MET filter event selection
    events = skimmer_utils.apply_met_filters_cut(events, met_filters)
    skimmer_utils.update_cut_flow(cut_flow, "METFilters", events)

    # Phi spike filter
    events = skimmer_utils.apply_phi_spike_filter(events, year, "skimmer/tchannel_phi_spike_hot_spots.pkl", n_jets=4)
    skimmer_utils.update_cut_flow(cut_flow, "PhiSpikeFilter", events)

    events = sequences.add_analysis_branches(events)

    if pn_tagger:
        events = sequences.add_particle_net_tagger(events)

    events = sequences.remove_collections(events)

    return events, cut_flow

