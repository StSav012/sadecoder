# coding=utf-8
import locale
import struct
import sys
from pathlib import Path
from tkinter import filedialog, messagebox


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
        is_trace1_written: bool
        trace1_view_state: int
        is_trace2_written: bool
        trace2_view_state: int
        is_trace3_written: bool
        trace3_view_state: int
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
            is_trace1_written,  # maybe it is of an `I` type, not padded
            trace1_view_state,  # see below
            _trace1_1,  # unknown
            _trace1_averaging,  # unknown
            is_trace2_written,  # maybe it is of an `I` type, not padded
            trace2_view_state,  # see below
            _trace2_1,  # unknown
            _trace2_averaging,  # unknown
            is_trace3_written,  # maybe it is of an `I` type, not padded
            trace3_view_state,  # see below
            _trace3_1,  # unknown
            _trace3_averaging,  # unknown
        ) = struct.unpack("<2L5dQdf?3xdI" + "?3xBBh" * 3 + "4x", binary_data[:0x70])
        # View State:
        #  0x00: clear write
        #  0x01: min hold
        #  0x02: max hold
        #  0x03: view
        #  0x04: blank
        #  and there are more
        # XXX: what are the values prefixed with an underscore?!

        size_per_channel: int = 2001 * struct.calcsize("<d")
        binary_data = binary_data[0x70:]
        if len(binary_data) % size_per_channel:
            messagebox.showerror("Error", f"File '{ofn}' seems corrupted")
            return -4

        number_of_channels: int = len(binary_data) // size_per_channel
        if number_of_channels != is_trace1_written + is_trace2_written + is_trace3_written:
            messagebox.showerror("Error", f"File '{ofn}' seems corrupted")
            return -4

        y_values: list[list[float]] = []
        for ch in range(number_of_channels):
            y_values.append(
                list(struct.unpack_from(f"<{points_per_channel}d", binary_data))
            )
            binary_data = binary_data[size_per_channel:]

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
            f_out.write(
                sep.join(
                    (
                        repr("Frequency, Hz"),
                        *[
                            repr(f"Trc{ch + 1}, dBm")
                            for ch in range(number_of_channels)
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
                            locale.format_string(
                                "%.12e",
                                frequency,
                            ),
                            *[
                                locale.format_string("%.12e", y_values[ch][point_index])
                                for ch in range(number_of_channels)
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
