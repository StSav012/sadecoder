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
        ofn = Path(sys.argv[1])
    if not ofn:
        return 0

    try:
        with open(ofn, "rb") as fin:
            h = fin.read()
    except Exception as ex:
        messagebox.showwarning("Error", f"Unable to read '{ofn}':\n{ex}")
        return -2
    else:
        if len(h) not in (16120, 48136):
            messagebox.showwarning("Error", f"File '{ofn}' has wrong length: {len(h)}")
            return -4

        # test whether the file is binary
        i = 0
        while i < 8:
            if not h[i : (i + 1)].isspace() and h[i] < b" "[0]:
                break
            i += 1
        if i >= 8:
            messagebox.showwarning(
                "Error",
                f"File '{ofn}' seems invalid",
            )
            return -2

        fv = struct.unpack_from("=4d", h, 8)
        # XXX: what are the other values?!

        points_per_channel: int = min(2001, (h[0x31] << 8) + h[0x30])
        size_per_channel: int = 2001 * struct.calcsize("=d")
        h = h[0x70:]
        if len(h) % size_per_channel:
            messagebox.showwarning("Error", f"File '{ofn}' seems corrupted")
            return -4

        number_of_channels: int = len(h) // size_per_channel

        v = [[] for _ in range(number_of_channels)]
        for ch in range(number_of_channels):
            v[ch] = list(struct.unpack_from(f"={points_per_channel}d", h))
            h = h[size_per_channel:]

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
        sfn = Path(sys.argv[2])
    if not sfn:
        return 0

    # fixing the file extension
    if sfn.suffix.casefold() != ".csv":
        sfn = sfn.with_name(sfn.name + ".csv")

    sep = "\t"

    try:
        with open(sfn, "wt") as fout:
            fout.write(
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
                fout.write(
                    sep.join(
                        (
                            locale.format_string(
                                "%.12e",
                                fv[0] + fv[3] * point_index / points_per_channel,
                            ),
                            *[
                                locale.format_string("%.12e", v[ch][point_index])
                                for ch in range(number_of_channels)
                            ],
                        )
                    )
                    + "\n"
                )
    except Exception as ex:
        messagebox.showwarning("Error", f"Unable to write '{sfn}':\n{ex}")
        return -3

    messagebox.showinfo(message="File processed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
