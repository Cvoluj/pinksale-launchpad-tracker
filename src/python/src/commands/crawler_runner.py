from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from multiprocessing import Process, Queue
from commands.exporter.export import Exporter
from scrapy.utils.project import get_project_settings


def run(q):
    try:
        runner = CrawlerRunner(get_project_settings())
        runner.crawl('pinksale')
        runner.crawl('gecko')
        runner.crawl('pump')
        d = runner.join()
        d.addCallback(export)  
        reactor.run()
        q.put(None) 
    except Exception as e:
        q.put(e)


def export(_):
    exporter = Exporter()
    reactor.callLater(0, exporter.run, [], None)


def run_crawler():
    """
    Run CrawlerRunner in new process so reactor work on
    """
    q = Queue()
    p = Process(target=run, args=(q, ))
    p.start()
    result = q.get()
    p.join()
    
    if result is not None:
        raise result


if __name__ == '__main__':
    """
    Example of running crawler multiple times
    """
    print('first run:')
    run_crawler()

    print('second run:')
    run_crawler()
