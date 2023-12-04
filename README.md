# Decode binary trace files written by Gratten™ Spectrum Analyzer

The basic app reads a filename of a trace file produced by Gratten™ Spectrum Analyzer and converts it into a CSV file.

The names of the file to read and the one to save can be provided as command line parameters.
Unless they are given, a graphical dialog appears, prompting to specify the files.

### Deployment with `nuitka`

To deploy, install what is listed in `deploy-requirements.txt` and run `deplot.bat` or `deploy.sh`.

Some user interactions might be required while `nuitka` is doing its job.

An executable file named `sadecoder` will appear in the directory.
