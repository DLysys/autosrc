# cnnvd_culs_crawler

本项目用于爬虫国家信息安全漏洞库中相应模块相关的漏洞。

### 安装依赖（dependency）

  ```bash
  # 进入`cnnvd_culs_crawler`根目录安装依赖
  pip install -r requirements.txt
  ```
### 爬虫（crawler）
  - scrapy crawler: 使用scrapy爬虫框架

  ```bash
  # 进入`cnnvd_culs_crawler，爬取数据
  bash run_crawler.sh

  # 爬到的数据最终保存在MySQL数据库中
  ```
### 如何添加新爬虫（add new crawler）
  ```bash
  # 进入`cnnvd_culs_crawler，爬取数据
  bash run_crawler.sh

  # 爬到的数据最终保存在MySQL数据库中
  ```