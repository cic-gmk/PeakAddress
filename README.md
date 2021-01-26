### PeakAddress
A tool for the processing of peaks of spectrums.
### Quick start

Download the files and set the appropriate work path.

The spectrum file is needed. The details of data format are referred in docs.
```
python PeakAddress.py spectrum_data.csv -o newData.csv
```
### Parameters

```
positional arguments:
  spectrum_data         Input original spectrum data

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output dir

Peak Recognition Threshold Arguments:
  -p PATH, --path PATH  The path of peak recognition (1)
  -t THRESHOLD, --threshold THRESHOLD
                        The rate of increase or decrease of the peak (400)
  -O OVERLAP_RATE, --overlap_rate OVERLAP_RATE
                        Reciprocal overlaps between peaks to be demixed (0.7)

Optimization Arguments:
  -b BASELINECORRECT, --baselinecorrect BASELINECORRECT
                        Whether correct the baseline of the raw data (False)
  -i INTERMEDIATE, --intermediate INTERMEDIATE
                        Whether output the intermediate peak location files
                        (False)
```
