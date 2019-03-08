#!/usr/bin/env bash

# run command such as "bash run_cnnvd_crawler.sh 'Apache mod_perl'"
scrapy crawl -a module_name="$1" cnnvd_vuls_spider
