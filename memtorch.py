import numpy as np
import torch

import memtorch

'''
pulse_duration, refactory_period, pos_voltage_level, crossbar.devices[point].time_series_resolution,
Used to generate programming signal


'''

def stuckFaultMap(
):
    """Method to generate stuck-fault map using quiescent voltage method
    1. Read to store conductance values off chip
    2. Write +w to all cells
    3. Calculate reference current
    4. Apply test voltage to GROUP of rows
    5. Write -w to RRAM cells
    6. Discrepency between reference and measured current indicates stuck-fault
    7. Repeat process the other way by applying test voltages to columns
    8. Cross reference detected rows and columns to determine cells SA0
    9. Repeat process for SA1 detection by writing -w first then +w
    """

def conductanceSwitchingPulseNumberGraph(
    crossbar,
    max_conductance,
    min_conductance,
    pulse_duration=1e-3,
    refactory_period=0,
    pos_voltage_level=1.0,
    neg_voltage_level=-1.0,
    timeout=5,
    force_adjustment=1e-3,
    force_adjustment_rel_tol=1e-1,
    force_adjustment_pos_voltage_threshold=0,
    force_adjustment_neg_voltage_threshold=0,
    simulate_neighbours=True,
):

    """Method to generate conductane vs switching pulse number graph
    1. Switch to LRS
    2. Apply SET programming pulse
    3. Read conductance
    4. Repeat until conductance[i] - condutance[i-1] <= e where e is a pre-defined constant
    5. Apply RESET programming pulse
    4. Read conductance
    5. Repeat until conductance[i] <= conductance[0]

    ----------
    crossbar : memtorch.bh.crossbar.Crossbar
        Crossbar containing the device to program.
    SF_map : numpy.array/2d array
        Stuck-fault map (row, column).
    max_conductance : float
        Minimum conductance to use as LRS.
    min_conductance : float
        Maximum conductance to use a HRS.
    pulse_duration : float
        Duration of the programming pulse (s).
    refactory_period : float
        Duration of the refactory period (s).
    pos_voltage_level : float
        Positive voltage level (V).
    neg_voltage_level : float
        Negative voltage level (V).
    Returns
    -------
    memtorch.bh.memristor.Memristor.Memristor
        Programmed device.
    """

def naive_program(
    crossbar,
    point,
    conductance,
    rel_tol=0.01,
    pulse_duration=1e-3,
    refactory_period=0,
    pos_voltage_level=1.0,
    neg_voltage_level=-1.0,
    timeout=5,
    force_adjustment=1e-3,
    force_adjustment_rel_tol=1e-1,
    force_adjustment_pos_voltage_threshold=0,
    force_adjustment_neg_voltage_threshold=0,
    simulate_neighbours=True,
):
    """Method to program (alter) the conductance of a given device within a crossbar.
    Parameters
    ----------
    crossbar : memtorch.bh.crossbar.Crossbar
        Crossbar containing the device to program.
    point : tuple
        Point to program (row, column).
    conductance : float
        Conductance to program.
    rel_tol : float
        Relative tolerance between the desired conductance and the device's conductance.
    pulse_duration : float
        Duration of the programming pulse (s).
    refactory_period : float
        Duration of the refactory period (s).
    pos_voltage_level : float
        Positive voltage level (V).
    neg_voltage_level : float
        Negative voltage level (V).
    timeout : int
        Timeout (seconds) until stuck devices are unstuck.
    force_adjustment : float
        Adjustment (resistance) to unstick stuck devices.
    force_adjustment_rel_tol : float
        Relative tolerance threshold between a stuck device's conductance and high and low conductance states to force adjust.
    force_adjustment_pos_voltage_threshold : float
        Positive voltage level threshold (V) to enable force adjustment.
    force_adjustment_neg_voltage_threshold : float
        Negative voltage level threshold (V) to enable force adjustment.
    simulate_neighbours : bool
        Simulate neighbours (True).
    Returns
    -------
    memtorch.bh.memristor.Memristor.Memristor
        Programmed device.
    """
    assert (1 / conductance) >= crossbar.devices[
        point
    ].r_on and conductance <= crossbar.devices[
        point
    ].r_off, "Conductance to program must be between g_off and g_on."
    assert (
        len(crossbar.devices.shape) == 2 or len(crossbar.devices.shape) == 3
    ), "Invalid devices shape."
    if len(crossbar.devices.shape) == 3:
        tile, row, column = point
    else:
        row, column = point
        tile = None

    time_signal, pos_voltage_signal = gen_programming_signal(
        1,
        pulse_duration,
        refactory_period,
        pos_voltage_level,
        crossbar.devices[point].time_series_resolution,
    )
    _, neg_voltage_signal = gen_programming_signal(
        1,
        pulse_duration,
        refactory_period,
        neg_voltage_level,
        crossbar.devices[point].time_series_resolution,
    )
    timeout = time.time() + timeout
    iterations = 0
    while not math.isclose(conductance, crossbar.devices[point].g, rel_tol=rel_tol):
        if conductance < crossbar.devices[point].g:
            voltage_signal = neg_voltage_signal
        else:
            voltage_signal = pos_voltage_signal

        previous_g = crossbar.devices[point].g
        crossbar.devices[point].simulate(voltage_signal)
        if simulate_neighbours:
            for row_ in range(0, crossbar.devices.shape[-2]):
                if row_ != row:
                    if tile is not None:
                        idx = (tile, row_, column)
                    else:
                        idx = (row_, column)

                    crossbar.devices[idx].simulate(voltage_signal / 2)

            for column_ in range(0, crossbar.devices.shape[-1]):
                if column_ != column:
                    if tile is not None:
                        idx = (tile, row, column_)
                    else:
                        idx = (row, column_)

                    crossbar.devices[idx].simulate(voltage_signal / 2)

        if crossbar.devices[point].g == previous_g:
            if (
                np.amax(voltage_signal) >= force_adjustment_pos_voltage_threshold
                or np.amin(voltage_signal) <= force_adjustment_neg_voltage_threshold
            ):
                if math.isclose(
                    previous_g,
                    1 / crossbar.devices[point].r_on,
                    rel_tol=force_adjustment_rel_tol,
                ):
                    crossbar.devices[point].set_conductance(
                        crossbar.devices[point].g - force_adjustment
                    )
                elif math.isclose(
                    previous_g,
                    1 / crossbar.devices[point].r_off,
                    rel_tol=force_adjustment_rel_tol,
                ):
                    crossbar.devices[point].set_conductance(
                        crossbar.devices[point].g + force_adjustment
                    )

        iterations += 1
        if iterations % 100 == 0 and time.time() > timeout:
            warnings.warn("Failed to program device to rel_tol (%f)." % rel_tol)
            break

    return crossbar.devices