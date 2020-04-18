import numpy
from django.core.management.base import BaseCommand

from neware_parser.neware_processing_functions import *
from WetCellDatabase.models import *
from neware_parser.Key import Key


# TODO (harvey): add docstring
def get_pos_id_from_cell_id(cell_id):
    wet_cells = WetCell.objects.filter(cell_id = cell_id)
    if wet_cells.exists():
        wet_cell = wet_cells[0]
        dry_cell = wet_cell.dry_cell
        if dry_cell is None:
            return None, None
        dry_cell = dry_cell.dry_cell
        if dry_cell is None:
            return None, None
        cathode = dry_cell.cathode
        if cathode is None:
            return None, None
        else:
            return cathode.id, str(cathode)

    return None, None


# TODO (harvey): add docstring
def get_neg_id_from_cell_id(cell_id):
    wet_cells = WetCell.objects.filter(cell_id = cell_id)
    if wet_cells.exists():
        wet_cell = wet_cells[0]
        dry_cell = wet_cell.dry_cell
        if dry_cell is None:
            return None, None
        dry_cell = dry_cell.dry_cell
        if dry_cell is None:
            return None, None
        anode = dry_cell.anode
        if anode is None:
            return None, None
        else:
            return anode.id, str(anode)

    return None, None


# TODO (harvey): add docstring
def get_electrolyte_id_from_cell_id(cell_id):
    wet_cells = WetCell.objects.filter(cell_id = cell_id)
    if wet_cells.exists():
        wet_cell = wet_cells[0]
        electrolyte = wet_cell.electrolyte
        if electrolyte is None:
            return None, None
        else:
            return electrolyte.id, str(electrolyte)

    return None, None


# TODO (harvey): add docstring
def get_component_from_electrolyte(electrolyte):
    weight_dict = {"solvent": {}, "salt": {}, "additive": {}}
    name_dict = {"solvent": {}, "salt": {}, "additive": {}}
    electrolyte_lots = CompositeLot.objects.filter(id = electrolyte)
    if electrolyte_lots.exists():
        electrolyte_lot = electrolyte_lots[0]
        if electrolyte_lot.composite is not None:
            my_electrolyte = electrolyte_lot.composite
            my_components = my_electrolyte.components

            for component in my_components.order_by("id"):
                for st, s in [
                    ("solvent", SOLVENT), ("salt", SALT), ("additive", ADDITIVE)
                ]:
                    if component.component_lot.component.component_type == s:
                        name_dict[st][component.component_lot.id]\
                            = str(component.component_lot)
                        weight_dict[st][component.component_lot.id]\
                            = [component.ratio]

    return weight_dict, name_dict


# TODO (harvey): add docstring
def make_my_barcodes(fit_args):
    my_barcodes = CyclingFile.objects.filter(
        database_file__deprecated = False,
        database_file__is_valid = True
    ).exclude(
        database_file__valid_metadata = None
    ).order_by(
        "database_file__valid_metadata__barcode"
    ).values_list(
        "database_file__valid_metadata__barcode",
        flat = True
    ).distinct()

    used_barcodes = []
    for b in my_barcodes:
        if (ChargeCycleGroup.objects.filter(barcode = b).exists()
            or DischargeCycleGroup.objects.filter(barcode = b).exists()
        ):
            used_barcodes.append(b)

    if len(fit_args["wanted_barcodes"]) == 0:
        return used_barcodes
    else:
        return list(
            set(used_barcodes).intersection(
                set(fit_args["wanted_barcodes"])
            )
        )


# TODO (harvey): reformat docstring
def initial_processing(my_barcodes, fit_args):
    """
        the output of this function has the following structure:
            a dictionary indexed by various data:
                - Key.V_GRID: 1D array of voltages
                - Key.Q_GRID: 1D array of log currents
                - Key.TEMP_GRID: 1D array of temperatures
                - Key.SIGN_GRID: 1D array of signs
                - Key.CELL_TO_POS: a dictionary indexed by barcode yielding a positive electrode id.
                - Key.CELL_TO_NEG: a dictionary indexed by barcode yielding a positive electrode id.
                - Key.CELL_TO_ELE: a dictionary indexed by barcode yielding a positive electrode id.
                - Key.CELL_TO_LAT: a dictionary indexed by barcode yielding
                         1 if the cell is latent,
                         0 if made of known pos,neg,electrolyte
                - Key.ALL_DATA: a dictionary indexed by barcode. Each barcode yields:
                    - "all_reference_mats": structured array with dtype =
                        [
                            (
                                "cycle_number",
                                "f4"
                            ),
                            (
                                Key.COUNT_MATRIX,
                                "f4",
                                (
                                    len(sign_grid),
                                    len(voltage_grid_degradation),
                                    len(current_grid),
                                    len(temperature_grid)
                                )
                            ),
                        ]

                    - "cyc_grp_dict": we know how this works.
                        basically groups of steps indexed by group averages of
                        (
                            end_current_prev,
                            constant_current,
                            end_current,
                            end_voltage_prev,
                            end_voltage,
                            sign
                        )

                        each group is a dictinary indexed by various quantities:
                        - Key.MAIN:  a numpy structured array with dtype:
                            [
                                ("cycle_number", "f4"),
                                ("cc_voltage_vector", "f4", len(voltage_grid)),
                                ("cc_capacity_vector", "f4", len(voltage_grid)),
                                ("cc_mask_vector", "f4", len(voltage_grid)),
                                ("cv_current_vector", "f4", fit_args["current_max_n"]),
                                ("cv_capacity_vector", "f4", fit_args["current_max_n"]),
                                ("cv_mask_vector", "f4", fit_args["current_max_n"]),
                                ("constant_current", "f4"),
                                ("end_current_prev", "f4"),
                                ("end_current", "f4"),
                                ("end_voltage_prev", "f4"),
                                ("end_voltage", "f4"),
                                ("last_cc_voltage", "f4"),
                                ("last_cc_capacity", "f4"),
                                ("last_cv_capacity", "f4"),
                                ("temperature", "f4"),
                            ]

                        -     Key.I_CC_AVG
                        -     Key.I_PREV_END_AVG
                        -     Key.Q_END_AVG
                        -     Key.V_PREV_END_AVG
                        -     Key.V_END_AVG
                        -     "avg_last_cc_voltage"
    """

    all_data = {}
    voltage_grid = make_voltage_grid(
        fit_args["voltage_grid_min_v"],
        fit_args["voltage_grid_max_v"],
        fit_args["voltage_grid_n_samples"],
        my_barcodes
    )

    voltage_grid_degradation = make_voltage_grid(
        fit_args["voltage_grid_min_v"],
        fit_args["voltage_grid_max_v"],
        int(fit_args["voltage_grid_n_samples"] / 4),
        my_barcodes
    )

    current_grid = make_current_grid(
        fit_args["current_grid_min_v"],
        fit_args["current_grid_max_v"],
        fit_args["current_grid_n_samples"],
        my_barcodes
    )

    temperature_grid = make_temperature_grid(
        fit_args["temperature_grid_min_v"],
        fit_args["temperature_grid_max_v"],
        fit_args["temperature_grid_n_samples"],
        my_barcodes
    )
    sign_grid = make_sign_grid()
    """
    - cycles are grouped by their charge rates and discharge rates.
    - a cycle group contains many cycles
    - things are split up this way to sample each group equally
    - each barcode corresponds to a single cell
    """
    for barcode in my_barcodes:
        """
        - dictionary indexed by charging and discharging rate (i.e. cycle group)
        - contains structured arrays of
            - cycle_number
            - capacity_vector: a vector where each element is a
              capacity associated with a given voltage
              [(voltage_grid[i], capacity_vector[i])
              is a voltage-capacity pair]
            - vq_curve_mask: a vector where each element is a weight
              corresponding to a voltage-capacity pair
              [this allows us to express the fact that sometimes a given
              voltage was not measured, so the capacity is meaningless.
              (mask of 0)]
        """

        files = get_files_for_barcode(barcode)

        all_mats = []
        for cyc in Cycle.objects.filter(cycling_file__in = files).order_by(
            "cycle_number"):
            count_matrix = get_count_matrix(
                cyc, voltage_grid_degradation, current_grid, temperature_grid,
                sign_grid,
            )
            true_cycle = cyc.get_offset_cycle()
            # for each cycle, call COUNT_MATRIX,
            # and get (true_cyc, COUNT_MATRIX) list
            if count_matrix is None:
                continue
            all_mats.append((true_cycle, count_matrix))

        all_mats = numpy.array(
            all_mats,
            dtype = [
                ("cycle_number", "f4"),
                (
                    Key.COUNT_MATRIX, "f4",
                    (
                        len(sign_grid), len(voltage_grid_degradation),
                        len(current_grid), len(temperature_grid),
                    ),
                ),
            ]
        )

        min_cycle = numpy.min(all_mats["cycle_number"])
        max_cycle = numpy.max(all_mats["cycle_number"])

        cycle_span = max_cycle - min_cycle

        delta_cycle = cycle_span / float(fit_args["reference_cycles_n"])

        reference_cycles = [
            min_cycle + i * delta_cycle for i in
            numpy.arange(1, fit_args["reference_cycles_n"] + 1)
        ]

        all_reference_mats = []
        # then for reference cycle,
        # mask all cycles < reference cycle compute the average.
        for reference_cycle in reference_cycles:
            prev_matrices = all_mats[Key.COUNT_MATRIX][
                all_mats["cycle_number"] <= reference_cycle
                ]
            avg_matrices = numpy.average(prev_matrices)
            all_reference_mats.append((reference_cycle, avg_matrices))
            # each step points to the nearest reference cycle

        all_reference_mats = numpy.array(
            all_reference_mats,
            dtype = [
                ("cycle_number", "f4"),
                (
                    Key.COUNT_MATRIX, "f4",
                    (
                        len(sign_grid), len(voltage_grid_degradation),
                        len(current_grid), len(temperature_grid),
                    ),
                ),
            ]
        )

        cyc_grp_dict = {}
        for typ in ["chg", "dchg"]:
            if typ == "dchg":
                sign = -1.
            else:
                sign = 1.

            if typ == "dchg":
                groups = DischargeCycleGroup.objects.filter(
                    barcode = barcode
                ).order_by("constant_rate")
            else:
                groups = ChargeCycleGroup.objects.filter(
                    barcode = barcode
                ).order_by("constant_rate")
            for cyc_group in groups:
                result = []

                for cyc in cyc_group.cycle_set.order_by("cycle_number"):
                    if cyc.valid_cycle:
                        post_process_results = ml_post_process_cycle(
                            cyc, voltage_grid, typ,
                            current_max_n = fit_args["current_max_n"]
                        )

                        if post_process_results is None:
                            continue

                        result.append((
                            cyc.get_offset_cycle(),
                            post_process_results["cc_voltages"],
                            post_process_results["cc_capacities"],
                            post_process_results["cc_masks"],
                            sign * post_process_results["cv_currents"],
                            post_process_results["cv_capacities"],
                            post_process_results["cv_masks"],
                            sign * post_process_results["constant_current"],
                            -sign * post_process_results["end_current_prev"],
                            sign * post_process_results["end_current"],
                            post_process_results["end_voltage_prev"],
                            post_process_results["end_voltage"],
                            post_process_results["last_cc_voltage"],
                            post_process_results["last_cc_capacity"],
                            post_process_results["last_cv_capacity"],
                            cyc.get_temperature()
                        ))

                res = numpy.array(
                    result,
                    dtype = [
                        ("cycle_number", "f4"),

                        ("cc_voltage_vector", "f4", len(voltage_grid)),
                        ("cc_capacity_vector", "f4", len(voltage_grid)),
                        ("cc_mask_vector", "f4", len(voltage_grid)),

                        ("cv_current_vector", "f4", fit_args["current_max_n"]),
                        ("cv_capacity_vector", "f4", fit_args["current_max_n"]),
                        ("cv_mask_vector", "f4", fit_args["current_max_n"]),

                        ("constant_current", "f4"),
                        ("end_current_prev", "f4"),
                        ("end_current", "f4"),
                        ("end_voltage_prev", "f4"),
                        ("end_voltage", "f4"),
                        ("last_cc_voltage", "f4"),
                        ("last_cc_capacity", "f4"),
                        ("last_cv_capacity", "f4"),
                        ("temperature", "f4"),
                    ]
                )

                if len(res) > 0:
                    cyc_grp_dict[(
                        cyc_group.constant_rate, cyc_group.end_rate_prev,
                        cyc_group.end_rate, cyc_group.end_voltage,
                        cyc_group.end_voltage_prev, typ,
                    )] = {
                        Key.MAIN: res,
                        Key.I_CC_AVG:
                            numpy.average(res["constant_current"]),
                        Key.I_PREV_END_AVG:
                            numpy.average(res["end_current_prev"]),
                        Key.Q_END_AVG: numpy.average(res["end_current"]),
                        Key.V_PREV_END_AVG:
                            numpy.average(res["end_voltage_prev"]),
                        Key.V_END_AVG: numpy.average(res["end_voltage"]),
                        "avg_last_cc_voltage":
                            numpy.average(res["last_cc_voltage"]),
                    }

        all_data[barcode] = {
            "cyc_grp_dict": cyc_grp_dict,
            "all_reference_mats": all_reference_mats,
        }

    """
    "cell_id_list": 1D array of barcodes
    "pos_id_list": 1D array of positive electrode ids
    "neg_id_list": 1D array of negative electrode ids
    "electrolyte_id_list": 1D array of electrolyte ids
    Key.CELL_TO_POS: a dictionary indexed by barcode yielding a positive
        electrode id.
    Key.CELL_TO_NEG: a dictionary indexed by barcode yielding a positive
        electrode id.
    Key.CELL_TO_ELE: a dictionary indexed by barcode yielding a
        positive electrode id.
    """

    cell_id_to_pos_id = {}
    cell_id_to_neg_id = {}
    cell_id_to_electrolyte_id = {}
    cell_id_to_latent = {}
    electrolyte_id_to_latent = {}
    electrolyte_id_to_solvent_id_weight = {}
    electrolyte_id_to_salt_id_weight = {}
    electrolyte_id_to_additive_id_weight = {}

    pos_to_pos_name = {}
    neg_to_neg_name = {}
    electrolyte_to_electrolyte_name = {}
    molecule_to_molecule_name = {}

    for cell_id in my_barcodes:
        pos, pos_name = get_pos_id_from_cell_id(cell_id)
        neg, neg_name = get_neg_id_from_cell_id(cell_id)
        electrolyte, electrolyte_name = get_electrolyte_id_from_cell_id(cell_id)
        if pos is None or neg is None or electrolyte is None:
            cell_id_to_latent[cell_id] = 1.
        else:
            pos_to_pos_name[pos] = pos_name
            neg_to_neg_name[neg] = neg_name
            electrolyte_to_electrolyte_name[electrolyte] = electrolyte_name

            cell_id_to_latent[cell_id] = 0.
            cell_id_to_pos_id[cell_id] = pos
            cell_id_to_neg_id[cell_id] = neg
            cell_id_to_electrolyte_id[cell_id] = electrolyte

            component_weight, component_name\
                = get_component_from_electrolyte(electrolyte)

            if (
                any([
                    s[0] is None for s in component_weight["solvent"].values()
                ]) or
                any([
                    s[0] is None for s in component_weight["salt"].values()
                ]) or
                any([
                    s[0] is None for s in component_weight["additive"].values()
                ])
            ):
                electrolyte_id_to_latent[electrolyte] = 1.
            else:
                for k in component_name["solvent"].keys():
                    molecule_to_molecule_name[k] = component_name["solvent"][k]
                for k in component_name["salt"].keys():
                    molecule_to_molecule_name[k] = component_name["salt"][k]
                for k in component_name["additive"].keys():
                    molecule_to_molecule_name[k] = component_name["additive"][k]

                electrolyte_id_to_latent[electrolyte] = 0.
                electrolyte_id_to_solvent_id_weight[electrolyte] = [
                    (sid, component_weight["solvent"][sid][0]) for sid in
                    component_weight["solvent"].keys()
                ]
                electrolyte_id_to_salt_id_weight[electrolyte] = [
                    (sid, component_weight["salt"][sid][0]) for sid in
                    component_weight["salt"].keys()
                ]
                electrolyte_id_to_additive_id_weight[electrolyte] = [
                    (sid, component_weight["additive"][sid][0]) for sid in
                    component_weight["additive"].keys()
                ]

    max_cap = 0.
    for barcode in all_data.keys():

        cyc_grp_dict = all_data[barcode]["cyc_grp_dict"]
        # find largest cap measured for this cell (max over all cycle groups)
        for k in cyc_grp_dict.keys():
            if len(cyc_grp_dict[k][Key.MAIN]["last_cc_capacity"]) > 0:
                max_cap = max(
                    max_cap,
                    max(abs(cyc_grp_dict[k][Key.MAIN]["last_cc_capacity"]))
                )

    return {
               Key.MAX_CAP: max_cap,
               Key.ALL_DATA: all_data,
               Key.V_GRID: voltage_grid_degradation,
               Key.Q_GRID: current_grid,
               Key.TEMP_GRID: temperature_grid,
               Key.SIGN_GRID: sign_grid,
               Key.CELL_TO_POS: cell_id_to_pos_id,
               Key.CELL_TO_NEG: cell_id_to_neg_id,
               Key.CELL_TO_ELE: cell_id_to_electrolyte_id,
               Key.CELL_TO_LAT: cell_id_to_latent,
               Key.ELE_TO_LAT: electrolyte_id_to_latent,
               Key.ELE_TO_SOL: electrolyte_id_to_solvent_id_weight,
               Key.ELE_TO_SALT: electrolyte_id_to_salt_id_weight,
               Key.ELE_TO_ADD: electrolyte_id_to_additive_id_weight,
           }, {
               "pos_to_pos_name": pos_to_pos_name,
               "neg_to_neg_name": neg_to_neg_name,
               "electrolyte_to_electrolyte_name":
                   electrolyte_to_electrolyte_name,
               "molecule_to_molecule_name": molecule_to_molecule_name,
           }


def compile_dataset(fit_args):
    if not os.path.exists(fit_args["path_to_dataset"]):
        os.mkdir(fit_args["path_to_dataset"])
    my_barcodes = make_my_barcodes(fit_args)
    pick, pick_names = initial_processing(my_barcodes, fit_args)
    with open(
        os.path.join(
            fit_args["path_to_dataset"],
            "dataset_ver_{}.file".format(fit_args["dataset_version"])
        ),
        "wb"
    ) as f:
        pickle.dump(pick, f, pickle.HIGHEST_PROTOCOL)

    with open(
        os.path.join(
            fit_args["path_to_dataset"],
            "dataset_ver_{}_names.file".format(fit_args["dataset_version"])
        ),
        "wb"
    ) as f:
        pickle.dump(pick_names, f, pickle.HIGHEST_PROTOCOL)


class Command(BaseCommand):

    def add_arguments(self, parser):
        required_args = [
            "--path_to_dataset",
            "--dataset_version",
        ]
        float_args = {
            "--voltage_grid_min_v": 2.5,
            "--voltage_grid_max_v": 5.0,
            "--current_grid_min_v": 1.,
            "--current_grid_max_v": 1000.,
            "--temperature_grid_min_v": -20.,
            "--temperature_grid_max_v": 80.,
        }
        int_args = {
            "--reference_cycles_n": 10,
            "--voltage_grid_n_samples": 32,
            "--current_grid_n_samples": 8,
            "--current_max_n": 8,
            "--temperature_grid_n_samples": 3,
        }

        for arg in required_args:
            parser.add_argument(arg, required = True)
        for arg in float_args:
            parser.add_argument(arg, type = float, default = float_args[arg])
        for arg in int_args:
            parser.add_argument(arg, type = int, default = int_args[arg])

        parser.add_argument(
            "--wanted_barcodes", type = int, nargs = "+",
            default = [
                57706, 57707, 57710, 57711, 57714, 57715, 64260, 64268, 81602,
                81603, 81604, 81605, 81606, 81607, 81608, 81609, 81610, 81611,
                81612, 81613, 81614, 81615, 81616, 81617, 81618, 81619, 81620,
                81621, 81622, 81623, 81624, 81625, 81626, 81627, 81712, 81713,
                82300, 82301, 82302, 82303, 82304, 82305, 82306, 82307, 82308,
                82309, 82310, 82311, 82406, 82407, 82410, 82411, 82769, 82770,
                82771, 82775, 82776, 82777, 82779, 82992, 82993, 83010, 83011,
                83012, 83013, 83014, 83015, 83016, 83083, 83092, 83101, 83106,
                83107, 83220, 83221, 83222, 83223, 83224, 83225, 83226, 83227,
                83228, 83229, 83230, 83231, 83232, 83233, 83234, 83235, 83236,
                83237, 83239, 83240, 83241, 83242, 83243, 83310, 83311, 83312,
                83317, 83318, 83593, 83594, 83595, 83596, 83741, 83742, 83743,
                83744, 83745, 83746, 83747, 83748,
            ],

        )

    def handle(self, *args, **options):
        compile_dataset(options)
