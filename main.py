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
        start_frequency: float
        end_frequency: float
        center_frequency: float
        frequency_span: float
        points_per_channel: int
        (
            _1,
            _2,
            start_frequency,
            end_frequency,
            center_frequency,
            frequency_span,
            _3,  # RBW?
            points_per_channel,  # maybe it is of a shorted type, then padded
            _4,  # ref level?
            _5,
        ) = struct.unpack_from("<2L5dQdf", binary_data)
        # XXX: what are the unnamed values?!
        #  is the number of channels @ the offset 0x54?

        size_per_channel: int = 2001 * struct.calcsize("<d")
        binary_data = binary_data[0x70:]
        if len(binary_data) % size_per_channel:
            messagebox.showerror("Error", f"File '{ofn}' seems corrupted")
            return -4

        number_of_channels: int = len(binary_data) // size_per_channel

        y_values: list[list[float]] = []
        for ch in range(number_of_channels):
            y_values.append(list(struct.unpack_from(f"<{points_per_channel}d", binary_data)))
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
                        repr("frequency, Hz"),
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
