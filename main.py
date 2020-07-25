from Service.chart import ChartCrawler
if __name__=='__main__':
    c = ChartCrawler(year=2019, month=1, day=1)
    c.parse()
    c.save_html_to_file()