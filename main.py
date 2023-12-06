# coding=utf-8
import enum
import locale
import struct
import sys
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Final

MAX_TRACES: Final[int] = 3
SIZE_PER_TRACE: Final[int] = 2001 * struct.calcsize("<d")


class ViewState(enum.IntEnum):
    ClearWrite = 0x00
    MinHold = 0x05
    MaxHold = 0x02
    View = 0x03
    Blank = 0x04
    Averaging = 0x01


VIEW_STATE_NAMES: Final[dict[int, str]] = {
    ViewState.ClearWrite.value: "Clear Write",
    ViewState.MinHold.value: "Min Hold",
    ViewState.MaxHold.value: "Max Hold",
    ViewState.View.value: "View",
    ViewState.Blank.value: "Blank",
    ViewState.Averaging.value: "Averaging",
}


def main() -> int:
    # get open filename
    ofn: Path
    if len(sys.argv) < 2:
        try:
            ofn = Path(
                filedialog.askopenfilename(
                    title="Open",
                    filetypes=[("SA Files", [".txt", ".ini", ".dat"])],
                )
            )
        except TypeError:
            # rejected
            return 0
    else:
        if not sys.argv[1]:
            return 0
        ofn = Path(sys.argv[1])

    binary_data: bytes
    try:
        with open(ofn, "rb") as f_in:
            binary_data = f_in.read()
    except Exception as ex:
        messagebox.showerror("Error", f"Unable to read '{ofn}':\n{ex}")
        return -2
    else:
        if len(binary_data) < 0x70:
            messagebox.showerror("Error", f"File '{ofn}' seems corrupted")
            return -4

        res_bw: int
        video_bw: int
        start_frequency: float
        end_frequency: float
        center_frequency: float
        frequency_span: float
        sweep_time_ns: float
        points_per_channel: int
        ref_level: float
        attenuation: float
        is_display_line_shown: bool
        display_line_position: float
        selected_trace: int
        is_trace_written: list[bool] = [False] * MAX_TRACES
        trace_view_state: list[int] = [-1] * MAX_TRACES
        (
            res_bw,
            video_bw,
            start_frequency,
            end_frequency,
            center_frequency,
            frequency_span,
            sweep_time_ns,
            points_per_channel,  # maybe it is of an `h` type, then padded
            ref_level,
            attenuation,
            is_display_line_shown,  # maybe it is of an `I` type, not padded
            display_line_position,
            selected_trace,  # zero-based, maybe it is of a `B` type, then padded
            is_trace_written[0],  # maybe it is of an `I` type, not padded
            trace_view_state[0],  # see below
            _always_03,  # unknown
            is_trace_written[1],  # maybe it is of an `I` type, not padded
            trace_view_state[1],  # see below
            _always_03,  # unknown
            is_trace_written[2],  # maybe it is of an `I` type, not padded
            trace_view_state[2],  # see below
            _always_03,  # unknown
        ) = struct.unpack(
            "<2L5dQdf?3xdI" + "?3xBB2x" * MAX_TRACES + "4x", binary_data[:0x70]
        )
        # XXX: what are the values prefixed with an underscore?!

        binary_data = binary_data[0x70:]
        if len(binary_data) % SIZE_PER_TRACE:
            messagebox.showerror("Error", f"File '{ofn}' seems corrupted")
            return -4

        number_of_traces: int = len(binary_data) // SIZE_PER_TRACE
        if number_of_traces != sum(is_trace_written):
            messagebox.showerror("Error", f"File '{ofn}' seems corrupted")
            return -4

        y_values: dict[int, list[float]] = {}
        for ch in range(number_of_traces):
            if is_trace_written[ch] and trace_view_state[ch] != ViewState.Blank:
                y_values[ch] = list(
                    struct.unpack_from(f"<{points_per_channel}d", binary_data)
                )
                binary_data = binary_data[SIZE_PER_TRACE:]

    # get save filename
    sfn: Path
    if len(sys.argv) < 3:
        try:
            sfn = Path(
                filedialog.asksaveasfilename(
                    confirmoverwrite=True,
                    title="Save",
                    initialdir=ofn.parent,
                    initialfile=ofn.with_suffix(".csv").name,
                    filetypes=[
                        (
                            "Tab Separated Values",
                            ".csv",
                        )
                    ],
                )
            )
        except TypeError:
            # rejected
            return 0
    else:
        if not sys.argv[2]:
            return 0
        sfn = Path(sys.argv[2])

    # fixing the file extension
    if sfn.suffix.casefold() != ".csv":
        sfn = sfn.with_name(sfn.name + ".csv")

    sep: str = "\t"

    try:
        with open(sfn, "wt") as f_out:
            f_out.writelines(
                (
                    f"# Res BW [Hz]: {res_bw}\n",
                    f"# Video BW [Hz]: {video_bw}\n",
                    f"# Start Frequency [Hz]: {start_frequency}\n",
                    f"# End Frequency [Hz]: {end_frequency}\n",
                    f"# Center Frequency [Hz]: {center_frequency}\n",
                    f"# Frequency Span [Hz]: {frequency_span}\n",
                    f"# Sweep [ns]: {sweep_time_ns}\n",
                    f"# Points: {points_per_channel}\n",
                    f"# Ref Level: {ref_level}\n",
                    f"# Attenuation: {attenuation}\n",
                )
            )
            f_out.write(
                sep.join(
                    (
                        '"Frequency [Hz]"',
                        *[
                            f'"Trc{ch + 1} ({VIEW_STATE_NAMES[trace_view_state[ch]]})"'
                            for ch in y_values
                        ],
                    )
                )
                + "\n"
            )
            for point_index in range(points_per_channel):
                frequency: float = start_frequency + frequency_span * point_index / (
                    points_per_channel - 1
                )
                f_out.write(
                    sep.join(
                        (
                            locale.format_string("%.12e", frequency),
                            *[
                                locale.format_string("%.12e", y_values[ch][point_index])
                                for ch in y_values
                            ],
                        )
                    )
                    + "\n"
                )
    except Exception as ex:
        messagebox.showerror("Error", f"Unable to write '{sfn}':\n{ex}")
        return -3

    messagebox.showinfo(message="File processed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
