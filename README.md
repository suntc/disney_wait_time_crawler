`wait_time_crawler.py` downloads original pages to local drive `./tables` using webdriver. Please make sure `geckodriver` is in your PATH before you run it.

`wait_time_stats.py` load the files in `./tables` and extract the wait time information into json files. It stores the json files into `./extracted_json`