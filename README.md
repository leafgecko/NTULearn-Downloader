# NTU Learn Downloader

Command line interface to downloading files and lecture videos from [NTULearn](http://ntulearn.ntu.edu.sg). See
[NTULearn-Downloader-GUI](https://github.com/leafgecko/NTULearn-Downloader-GUI) if you prefer a graphical user interface (GUI).

## Usage

```
usage: main.py [-h] [-username USERNAME] [-password PASSWORD]
               [--download_to DOWNLOAD_TO] [--ignore IGNORE] [--ignore_files]
               [--download_recorded_lectures] [--sem SEM] [--prompt]

CLI wrapper to NTULearn Downloader

optional arguments:
  -h, --help            show this help message and exit
  -username USERNAME    username including domain name (e.g.
                        username@student.main.ntu.edu.sg)
  -password PASSWORD    password
  --download_to DOWNLOAD_TO
                        Download destination (required if downloading files)
  --ignore IGNORE       Comma seperated list of modules to ignore, will ignore
                        module if it contains any of the supplied values (e.g.
                        CE2006)
  --ignore_files        Ignore downloading of files, useful if only
                        downloading lectures
  --download_recorded_lectures
                        Download recorded lectures. WARNING downloading large
                        files
  --sem SEM             Which semester to download from (e.g. AY2019/20
                        Semester 2 would be 19S2, see you are taking the
                        following courses output)
  --prompt              Prompt whether to download lecture video or files
                        above set (set with --max_size)
```

## Example

Download all files from 20/21 semester 1, and prompt to download recorded lectures
```
python main.py --sem 20S1 -username student@student.main.ntu.edu.sg -password password1234 --prompt --download_to NTU --download_recorded_lectures
```

## Packaging

```
python setup.py sdist
```

The `tar.gz` file will be created in the `dist` folder