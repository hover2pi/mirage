# Generate observation list files based on default values and APT output files
from lxml import etree
import numpy as np
import pprint
from nircam_simulator.scripts import apt_inputs

def write_yaml(xml_file, pointing_file, yaml_file, ps_cat_sw=None, ps_cat_lw=None):
    # Define "default" values (probably should be changed eventually)
    date = '2019-07-04'
    PAV3 = '0.'
    GalaxyCatalog = 'None'
    ExtendedCatalog = 'None'
    ExtendedScale = '1.0'
    ExtendedCenter = '1024,1024'
    MovingTargetList = 'None'
    MovingTargetSersic = 'None'
    MovingTargetExtended = 'None'
    MovingTargetConvolveExtended = 'True'
    MovingTargetToTrack = 'None'
    BackgroundRate_sw = '0.5'
    BackgroundRate_lw = '1.2'

    # Read in observations from XML file
    with open(xml_file) as f:
        tree = etree.parse(f)

    apt = '{http://www.stsci.edu/JWST/APT}'
    observation_data = tree.find(apt + 'DataRequests')
    obs_results = observation_data.findall('.//' + apt + 'Observation')

    observations = []
    i_observations = []
    obs_names = []
    obs_indices = range(len(obs_results))
    for o, i_obs in zip(obs_results, obs_indices):
        if o.find(apt + 'Instrument').text in ['NIRCAM', 'WFSC']:
            observations.append(o)
            i_observations.append(i_obs)

            obs_names.append(o.find(apt + 'Label').text)

    num_obs = len(observations)

    # Read in filters from XML file
    xml_read = apt_inputs.AptInput()
    xml_table = xml_read.read_xml(xml_file)

    sw_filters = []
    lw_filters = []
    sw_filters_all = xml_table['ShortFilter']
    lw_filters_all = xml_table['LongFilter']
    tile_nums = xml_table['TileNumber']
    observation_ids = xml_table['ObservationID']
    for i_obs_all in set(observation_ids):
        # i_obs_all = int(i_obs_all)
        current_obs_indices = [i == i_obs_all for i in observation_ids]
        if len(set(np.array(sw_filters_all)[current_obs_indices])) > 1:
            raise ValueError('Multiple filters in one observation')
            # At some point could use the tile_nums to fix this
        sw_filters.append(sw_filters_all[current_obs_indices[0]])
        lw_filters.append(lw_filters_all[current_obs_indices[0]])

    # # Choose only the catalogs from observations that will be used
    # print(i_observations)
    # ps_cat_sw = np.array(ps_cat_sw)[i_observations]
    # ps_cat_lw = np.array(ps_cat_lw)[i_observations]

    # Check that all parameters have the right length
    all_param_lengths = [len(ps_cat_sw), len(ps_cat_lw), len(sw_filters),
                         len(lw_filters), len(observations), len(i_observations),
                         len(obs_names)]
    if len(set(all_param_lengths)) > 1:
        print(all_param_lengths)
        raise ValueError('Not all provided parameters have compatible '
                         'dimensions. Will not write {}'.format(yaml_file))

    # # Read in observation names from pointing file
    # f = open(pointing_file)
    # rows = f.readlines()
    # f.close()
    # obs_names = [row[2:-1].split(' (')[0] for row in rows if '* ' == row[:2]]
    # num_obs = len(obs_names)

    write = ["# Observation list created by write_observationlist.py script in\n",
             "# nircam_simulator/scripts. Note: all values except filters and\n",
             "# observation names are default.\n\n"]
    for i_obs in range(num_obs):
        write += [\
        "Observation{}:\n".format(i_observations[i_obs] + 1),
        "  Name: '{}'\n".format(obs_names[i_obs]),
        "  Date: {}\n".format(date),
        "  PAV3: {}\n".format(PAV3),
        "  SW:\n",
        "    Filter: {}\n".format(sw_filters[i_obs]),
        "    PointSourceCatalog: {}\n".format(ps_cat_sw[i_obs]),
        "    GalaxyCatalog: {}\n".format(GalaxyCatalog),
        "    ExtendedCatalog: {}\n".format(ExtendedCatalog),
        "    ExtendedScale: {}\n".format(ExtendedScale),
        "    ExtendedCenter: {}\n".format(ExtendedCenter),
        "    MovingTargetList: {}\n".format(MovingTargetList),
        "    MovingTargetSersic: {}\n".format(MovingTargetSersic),
        "    MovingTargetExtended: {}\n".format(MovingTargetExtended),
        "    MovingTargetConvolveExtended: {}\n".format(MovingTargetConvolveExtended),
        "    MovingTargetToTrack: {}\n".format(MovingTargetToTrack),
        "    BackgroundRate: {}\n".format(BackgroundRate_sw),
        "  LW:\n",
        "    Filter: {}\n".format(lw_filters[i_obs]),
        "    PointSourceCatalog: {}\n".format(ps_cat_lw[i_obs]),
        "    GalaxyCatalog: {}\n".format(GalaxyCatalog),
        "    ExtendedCatalog: {}\n".format(ExtendedCatalog),
        "    ExtendedScale: {}\n".format(ExtendedScale),
        "    ExtendedCenter: {}\n".format(ExtendedCenter),
        "    MovingTargetList: {}\n".format(MovingTargetList),
        "    MovingTargetSersic: {}\n".format(MovingTargetSersic),
        "    MovingTargetExtended: {}\n".format(MovingTargetExtended),
        "    MovingTargetConvolveExtended: {}\n".format(MovingTargetConvolveExtended),
        "    MovingTargetToTrack: {}\n".format(MovingTargetToTrack),
        "    BackgroundRate: {}\n\n".format(BackgroundRate_lw)]

    f = open(yaml_file, 'w')
    for line in write:
        f.write(line)
    f.close()
    print('\nSuccessfully wrote {} observations to {}'.format(num_obs, yaml_file))


if __name__ == '__main__':
    xml_file = '../OTECommissioning/OTE01/OTE01-1134.xml'
    pointing_file = '../OTECommissioning/OTE01/OTE01-1134.pointing'
    yaml_file = 'test.yaml'

    write_yaml(xml_file, pointing_file, yaml_file)